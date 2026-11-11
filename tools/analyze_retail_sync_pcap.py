#!/usr/bin/env python3
"""Read-only comparison of observed Retail 1.07 sampled sync checks.

Accepts classic little-endian microsecond PCAP, Ethernet/IPv4/UDP only.
Observed envelope: 11-byte CPacket transport header, unreliable flag 0,
transfer size 17 at payload[7:11], type 0x13 at payload[11], then little-endian
FLOAT tick, INDEX sequence, ULONG CRC, INDEX level at payload[12:28]. Total
UDP payload is 28 bytes (UDP length 36). ACK flag 8 is transport data, not a
message type. Reliable/connect transports are counted but not reassembled.
No packet capture, engine-state reconstruction, or stability qualification.
"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path


def analyze(stream, source_ports, destination_port=25650):
    ports=tuple(source_ports)
    if len(ports)!=2 or len(set(ports))!=2 or any(type(p) is not int or not 1<=p<=65535 for p in ports):
        raise ValueError("two distinct explicit source ports required")
    if type(destination_port) is not int or not 1<=destination_port<=65535:
        raise ValueError("invalid destination port")
    digest=hashlib.sha256()
    def read(size):
        data=stream.read(size);digest.update(data);return data
    def require(valid,message):
        if not valid:raise ValueError(message)
    header=read(24)
    require(len(header)==24,"truncated PCAP header")
    magic,major,minor,zone,accuracy,snaplen,network=struct.unpack("<IHHIIII",header)
    require(magic==0xa1b2c3d4 and (major,minor)==(2,4),
            "only little-endian microsecond classic PCAP 2.4 is supported")
    require(network==1 and snaplen>=42,"Ethernet PCAP with valid snaplen required")
    records=sync_records=fragments=duplicates=acknowledgements=0
    unsupported={}
    checks={}
    while True:
        header=read(16)
        if not header:break
        records+=1
        require(len(header)==16,f"record {records}: truncated record header")
        seconds,micros,captured,original=struct.unpack("<IIII",header)
        require(micros<1000000 and 14<=captured<=snaplen and captured==original,
                f"record {records}: invalid timestamp/length or truncated capture")
        packet=read(captured)
        require(len(packet)==captured,f"record {records}: truncated packet")
        if packet[12:14]!=b"\x08\x00":continue
        require(len(packet)>=34,f"record {records}: truncated IPv4")
        version,ihl=packet[14]>>4,(packet[14]&15)*4
        require(version==4 and ihl>=20 and len(packet)>=14+ihl,
                f"record {records}: invalid IPv4 header")
        total=struct.unpack_from("!H",packet,16)[0]
        require(ihl<=total<=len(packet)-14,f"record {records}: invalid IPv4 total length")
        if packet[23]!=17:continue
        fragment=struct.unpack_from("!H",packet,20)[0]
        require(not fragment&0x8000,f"record {records}: reserved fragment flag")
        if fragment&0x3fff:
            fragments+=1;continue
        offset=14+ihl
        require(total>=ihl+8,f"record {records}: truncated UDP header")
        source,destination,length,checksum=struct.unpack_from("!HHHH",packet,offset)
        require(length>=8 and length==total-ihl,f"record {records}: invalid UDP length")
        if source not in ports or destination!=destination_port:continue
        payload=packet[offset+8:offset+length]
        require(len(payload)>=11,f"record {records}: truncated CPacket transport header")
        flags=payload[0];transfer=struct.unpack_from("<I",payload,7)[0]
        # Engine107/Engine/Network/CPacket.h:15,19-25: 11-byte header and flags.
        # A reliable fragment's transfer size may describe the whole transfer.
        if flags not in (0,8):
            key=str(flags);unsupported[key]=unsupported.get(key,0)+1;continue
        require(transfer==len(payload)-11,f"record {records}: CPacket transfer size mismatch")
        if flags==8:
            require(transfer>0 and transfer%4==0,f"record {records}: invalid ACK sequence array")
            acknowledgements+=1;continue
        if len(payload)<12 or payload[11]!=0x13:continue
        require(len(payload)==28,f"record {records}: unexpected SYNC payload length")
        tick,sequence,crc,level=struct.unpack_from("<fiIi",payload,12)
        require(math.isfinite(tick),f"record {records}: nonfinite sync tick")
        bits=struct.unpack_from("<I",payload,12)[0];key=(bits,sequence)
        sample=checks.setdefault(key,{"tick":tick,"ports":{}})
        variants=sample["ports"].setdefault(source,{})
        if variants:duplicates+=1
        variants.setdefault((crc,level),records)
        sync_records+=1

    def identity(key):
        return {"tick_bits":f"{key[0]:08x}","tick":checks[key]["tick"],"sequence":key[1]}
    missing=[];conflicts=[];pairs=[];matched=0
    for key,sample in checks.items():
        seen=sample["ports"]
        for port,variants in seen.items():
            if len(variants)>1:
                conflicts.append(dict(identity(key),source_port=port,
                                      variants=[{"crc32":f"{crc:08x}","level":level,"first_record":index}
                                                for (crc,level),index in variants.items()]))
        absent=set(ports)-set(seen)
        if absent:
            missing.append(dict(identity(key),present_source_port=next(iter(seen)),
                                missing_source_port=next(iter(absent))))
            continue
        # An ambiguous same-port sample is never accepted as a matching pair.
        if any(len(variants)!=1 for variants in seen.values()):continue
        values={port:next(iter(seen[port])) for port in ports}
        pair=dict(identity(key),paired_at_record=max(next(iter(seen[p].values())) for p in ports),
                  checks={str(p):{"crc32":f"{values[p][0]:08x}","level":values[p][1]} for p in ports})
        pair["equal"]=values[ports[0]]==values[ports[1]]
        pairs.append(pair);matched+=int(pair["equal"])
    differing=sorted((p for p in pairs if not p["equal"]),key=lambda p:p["paired_at_record"])
    if differing:status="DIFFERING_SAMPLED_SYNCCHECK"
    elif conflicts:status="CONFLICTING_DUPLICATES"
    elif missing or fragments or unsupported:status="INCOMPLETE_SAMPLED_COMPARISON"
    elif pairs:status="MATCHING_SAMPLED_SYNCCHECKS_ONLY"
    else:status="NO_COMPARABLE_SYNC_CHECKS"
    return {"schema_version":1,"capture_sha256":digest.hexdigest(),"qualified":False,"status":status,
            "source_ports":list(ports),"destination_port":destination_port,
            "packet_records":records,"sync_records":sync_records,"ignored_packets":records-sync_records,
            "fragmented_packets":fragments,"transport_ack_packets":acknowledgements,
            "unsupported_transport_packets":sum(unsupported.values()),"unsupported_transport_flags":unsupported,
            "duplicate_records":duplicates,"duplicate_conflicts":conflicts,
            "paired_checks":len(pairs),"matching_pairs":matched,"differing_pairs":len(differing),
            "missing_peers":missing,"first_differing_sampled_synccheck":differing[0] if differing else None,
            "interpretation":"Sampled checks only; first difference is ordered by capture pair availability, "
                             "not the first differing 20 Hz simulation tick. Missing packets, fragments, unimplemented "
                             "reliable/connect transports and "
                             "conflicting duplicates prevent complete comparison. Matching CRCs are not a "
                             "stability PASS; transport checksums and engine CRC contents are not recomputed."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pcap",type=Path)
    parser.add_argument("--source-ports",type=int,nargs=2,required=True,metavar=("A","B"))
    parser.add_argument("--destination-port",type=int,default=25650)
    args=parser.parse_args()
    try:
        with args.pcap.open("rb") as stream:result=analyze(stream,args.source_ports,args.destination_port)
    except (OSError,ValueError) as exc:parser.exit(2,f"sync PCAP: {exc}\n")
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=="__main__":main()
