import io
import math
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import analyze_retail_sync_pcap as audit

PORTS=(38640,37120)

def packet(port=PORTS[0],tick=1.0,seq=7,crc=123,level=1,kind=0x13,fragment=0,
           destination=25650,options=b"",extra=b"",bits=None,transport_flags=0,transfer_size=None,body_override=None):
    body=struct.pack("<f",tick) if bits is None else struct.pack("<I",bits)
    body+=struct.pack("<iIi",seq,crc,level)
    message=bytes([kind])+body+extra if body_override is None else body_override
    payload=struct.pack("<BIHI",transport_flags,0,0,len(message) if transfer_size is None else transfer_size)+message
    udp=struct.pack("!HHHH",port,destination,8+len(payload),0)+payload
    ip=bytearray(20+len(options));ip[0]=0x40+len(ip)//4
    struct.pack_into("!HHH",ip,2,len(ip)+len(udp),1,fragment);ip[8]=64;ip[9]=17
    ip[12:20]=bytes([127,0,0,1,127,0,0,1]);ip[20:]=options
    return b"\0"*12+b"\x08\x00"+ip+udp

def capture(*packets):
    header=struct.pack("<IHHIIII",0xa1b2c3d4,2,4,0,0,262144,1)
    return header+b"".join(struct.pack("<IIII",100,i,len(p),len(p))+p for i,p in enumerate(packets))

def analyze(data):
    return audit.analyze(io.BytesIO(data),PORTS)

class SyncPcapTests(unittest.TestCase):
    def test_identical_pair_and_ignored_action(self):
        result=analyze(capture(packet(),packet(PORTS[1]),packet(kind=0x12)))
        self.assertEqual((result["sync_records"],result["paired_checks"],result["matching_pairs"]),(2,1,1))
        self.assertEqual(result["differing_pairs"],0);self.assertIsNone(result["first_differing_sampled_synccheck"])
        self.assertFalse(result["qualified"])
    def test_crc_and_level_differences_are_sampled_checks(self):
        result=analyze(capture(packet(tick=1),packet(PORTS[1],tick=1),
                               packet(tick=2),packet(PORTS[1],tick=2,crc=9),
                               packet(tick=3),packet(PORTS[1],tick=3,level=2)))
        self.assertEqual(result["differing_pairs"],2)
        first=result["first_differing_sampled_synccheck"]
        self.assertEqual((first["tick"],first["sequence"],first["tick_bits"]),(2.0,7,"40000000"))
        self.assertEqual(result["status"],"DIFFERING_SAMPLED_SYNCCHECK")
        self.assertIn("not the first",result["interpretation"])
    def test_float_bits_and_sequence_form_exact_pair_identity(self):
        result=analyze(capture(packet(bits=0),packet(PORTS[1],bits=0x80000000),
                               packet(tick=2,seq=8),packet(PORTS[1],tick=2,seq=9)))
        self.assertEqual(result["paired_checks"],0);self.assertEqual(len(result["missing_peers"]),4)
    def test_missing_peer_explicit(self):
        result=analyze(capture(packet()))
        self.assertEqual(result["status"],"INCOMPLETE_SAMPLED_COMPARISON")
        self.assertEqual(result["missing_peers"][0]["missing_source_port"],PORTS[1])
    def test_identical_duplicates_do_not_inflate_pairs(self):
        result=analyze(capture(packet(),packet(),packet(PORTS[1])))
        self.assertEqual(result["matching_pairs"],1);self.assertEqual(result["duplicate_records"],1)
        self.assertEqual(result["duplicate_conflicts"],[])
    def test_conflicting_duplicates_cannot_count_as_match(self):
        result=analyze(capture(packet(),packet(crc=456),packet(PORTS[1])))
        self.assertEqual(result["matching_pairs"],0);self.assertEqual(len(result["duplicate_conflicts"]),1)
        self.assertEqual(result["status"],"CONFLICTING_DUPLICATES")
    def test_only_explicit_source_and_destination_ports(self):
        result=analyze(capture(packet(port=1234),packet(destination=25600)))
        self.assertEqual(result["sync_records"],0)
        with self.assertRaises(ValueError):audit.analyze(io.BytesIO(capture()),(1,1))
    def test_ipv4_options_and_ethernet_padding(self):
        result=analyze(capture(packet(options=b"\0"*4)+b"\0"*16,packet(PORTS[1])))
        self.assertEqual(result["matching_pairs"],1)
    def test_fragments_ignored_and_visible(self):
        result=analyze(capture(packet(fragment=0x2000),packet(PORTS[1],fragment=1)))
        self.assertEqual(result["sync_records"],0);self.assertEqual(result["fragmented_packets"],2)
    def test_ack_sequence_19_is_not_sync_message_type(self):
        ack=packet(transport_flags=8,body_override=struct.pack("<I",19))
        result=analyze(capture(ack,packet(),packet(PORTS[1])))
        self.assertEqual(result["transport_ack_packets"],1)
        self.assertEqual((result["sync_records"],result["matching_pairs"]),(2,1))
    def test_real_sync_transfer_size_corruption_is_not_ignored(self):
        for p in (packet(transfer_size=16),packet(extra=b"x",transfer_size=17),
                  packet(transport_flags=8,body_override=b"\x13",transfer_size=1)):
            with self.subTest(length=len(p)),self.assertRaises(ValueError):analyze(capture(p))
    def test_unimplemented_transport_is_counted_as_incomplete(self):
        result=analyze(capture(packet(transport_flags=7),packet(),packet(PORTS[1])))
        self.assertEqual(result["unsupported_transport_packets"],1)
        self.assertEqual(result["unsupported_transport_flags"],{"7":1})
        self.assertEqual(result["status"],"INCOMPLETE_SAMPLED_COMPARISON")
        self.assertEqual(result["matching_pairs"],1)
    def test_nonfinite_tick_rejected(self):
        for tick in (math.nan,math.inf,-math.inf):
            with self.subTest(tick=tick),self.assertRaises(ValueError):analyze(capture(packet(tick=tick)))
    def test_global_record_and_packet_truncation_fail(self):
        good=capture(packet())
        for broken in (good[:5],good[:30],good[:-1],capture(packet()[:20])):
            with self.subTest(size=len(broken)),self.assertRaises(ValueError):analyze(broken)
        wrong=bytearray(good);struct.pack_into("<I",wrong,24+12,len(packet())+1)
        with self.assertRaises(ValueError):analyze(wrong)
    def test_corrupt_ip_udp_and_sync_lengths_fail(self):
        for offset,value in ((14,0x44),(14+2,0),(14+20+4,0)):
            p=bytearray(packet())
            if offset==14:p[offset]=value
            else:struct.pack_into("!H",p,offset,value)
            with self.subTest(offset=offset),self.assertRaises(ValueError):analyze(capture(p))
        with self.assertRaises(ValueError):analyze(capture(packet(extra=b"x")))
    def test_first_difference_uses_pair_availability_and_signed_index(self):
        result=analyze(capture(packet(tick=20,seq=-2),packet(tick=10,seq=-1),
                               packet(PORTS[1],tick=10,seq=-1,crc=7),packet(PORTS[1],tick=20,seq=-2,crc=8)))
        first=result["first_differing_sampled_synccheck"]
        self.assertEqual((first["tick"],first["sequence"],first["paired_at_record"]),(10.0,-1,3))
    def test_record_timestamp_bounds_and_cli_rejection(self):
        bad=bytearray(capture(packet()));struct.pack_into("<I",bad,28,1000000)
        with self.assertRaises(ValueError):analyze(bad)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"bad.pcap";p.write_bytes(bad)
            process=subprocess.run([sys.executable,"-B",str(Path(audit.__file__)),str(p),"--source-ports",str(PORTS[0]),str(PORTS[1])],capture_output=True,text=True)
            self.assertEqual(process.returncode,2);self.assertEqual(process.stdout,"")
            self.assertIn("invalid timestamp",process.stderr)
    def test_other_protocols_ignored_and_unsupported_pcap_rejected(self):
        p=bytearray(packet());p[23]=6
        self.assertEqual(analyze(capture(p))["sync_records"],0)
        bad=bytearray(capture());struct.pack_into("<I",bad,20,113)
        with self.assertRaises(ValueError):analyze(bad)
        bad=bytearray(capture());bad[:4]=b"\xa1\xb2\xc3\xd4"
        with self.assertRaises(ValueError):analyze(bad)

if __name__=="__main__":unittest.main()
