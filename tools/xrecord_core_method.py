"""Pure bounded RECORD Core parser and native ABI declarations. No Xlib load."""
import ctypes as C
import math
import struct

LIMITS=dict(display=':167',recorder_seconds=15,records=1024,total_bytes=2*1024*1024,
            record_bytes=16384,arm_seconds=3,stop_seconds=3,driver_seconds=2,
            controller_seconds=30,cleanup_seconds=5)


class Range8(C.Structure):_fields_=[('first',C.c_ubyte),('last',C.c_ubyte)]
class Range16(C.Structure):_fields_=[('first',C.c_ushort),('last',C.c_ushort)]
class ExtRange(C.Structure):_fields_=[('ext_major',Range8),('ext_minor',Range16)]
class RecordRange(C.Structure):
    _fields_=[('core_requests',Range8),('core_replies',Range8),('ext_requests',ExtRange),
              ('ext_replies',ExtRange),('delivered_events',Range8),('device_events',Range8),
              ('errors',Range8),('client_started',C.c_int),('client_died',C.c_int)]
class Intercept(C.Structure):
    _fields_=[('id_base',C.c_ulong),('server_time',C.c_ulong),('client_seq',C.c_ulong),
              ('category',C.c_int),('client_swapped',C.c_int),('data',C.c_void_p),('data_len',C.c_ulong)]


def native_layout():
    return dict(pointer_bytes=C.sizeof(C.c_void_p),intercept_size=C.sizeof(Intercept),
                range_size=C.sizeof(RecordRange),wire_range_bytes=24,
                intercept_offsets={name:getattr(Intercept,name).offset for name,_ in Intercept._fields_})


def integer(value,maximum):
    if type(value)is not int or not 0<=value<=maximum:raise ValueError('invalid unsigned integer')
    return value


def copy_payload(*,data_pointer,data_len,reader):
    integer(data_len,LIMITS['record_bytes']//4)
    if data_len and not data_pointer:raise ValueError('null RECORD payload')
    if not data_len:return b''
    raw=reader(data_pointer,data_len*4)
    if len(raw)!=data_len*4:raise ValueError('short RECORD copy')
    return raw


class CaptureBudget:
    def __init__(self,*,started):
        if not isinstance(started,(float,int))or not math.isfinite(started)or started<0:raise ValueError('clock')
        self.started=self.last=started;self.records=self.bytes=0;self.failed=False
    def charge(self,*,record_bytes,serialized_bytes,now):
        if self.failed:raise ValueError('sticky capture budget failure')
        try:
            integer(record_bytes,LIMITS['record_bytes']);integer(serialized_bytes,LIMITS['total_bytes'])
            if not isinstance(now,(float,int))or not math.isfinite(now)or now<self.last or now-self.started>=15:raise ValueError('capture clock/TTL')
            if self.records>=1024 or self.bytes+serialized_bytes>LIMITS['total_bytes']:raise ValueError('capture record/byte limit')
            self.records+=1;self.bytes+=serialized_bytes;self.last=now
        except BaseException:self.failed=True;raise


class CoreTrace:
    def __init__(self,*,xtest_opcode):
        integer(xtest_opcode,255)
        if xtest_opcode<128:raise ValueError('dynamic extension major required')
        self.xtest_opcode=xtest_opcode;self.pending={};self.unsupported=0
        self.device_motion_count=self.delivered_motion_count=0;self.xi2_complete=False
    def accept(self,*,category,client_base,client_sequence,server_time,client_swapped,wire):
        integer(category,5);integer(client_base,0xffffffff);integer(client_sequence,0xffffffff);integer(server_time,0xffffffff)
        if type(client_swapped)is not bool or not isinstance(wire,bytes)or len(wire)>16384:raise ValueError('RECORD metadata/size')
        endian='>'if client_swapped else'<'
        row=dict(category=category,client_base=client_base,client_sequence=client_sequence,
                 server_time=server_time,client_swapped=client_swapped,wire_hex=wire.hex())
        def unpack(fmt,offset):
            try:return struct.unpack_from(endian+fmt,wire,offset)
            except struct.error as e:raise ValueError('truncated protocol')from e
        def exact(size):
            if len(wire)!=size:raise ValueError('protocol length mismatch')
        def unsupported():self.unsupported+=1;row['kind']='unsupported';return row
        if category in(2,3,4,5):
            if category in(3,4,5)and wire:raise ValueError('control record contains unexpected data')
            row['kind']={2:'client_started',3:'client_died',4:'start',5:'end'}[category];return row
        if len(wire)<4:raise ValueError('truncated protocol header')
        if category==1:
            opcode,minor,length=unpack('BBH',0)
            if not length or length*4!=len(wire):raise ValueError('request declared length')
            if opcode==self.xtest_opcode and minor==2:
                exact(36)
                if wire[4]!=6 or wire[5]!=1:return unsupported()
                dx,dy=unpack('hh',24)
                row.update(kind='xtest_relative_motion',dx=dx,dy=dy,requested_device=wire[35])
            elif opcode==41:
                exact(24);x,y=unpack('hh',20)
                row.update(kind='warp_request',dst_x=x,dst_y=y,position_confirmed=False)
            elif opcode==38:
                exact(8);key=(client_base,client_sequence&0xffff)
                if key in self.pending:raise ValueError('ambiguous query sequence')
                self.pending[key]=client_sequence;row['kind']='query_pointer_request'
            else:return unsupported()
            return row
        if category!=0:raise ValueError('invalid protocol category')
        event=wire[0]&0x7f
        if event==1:
            exact(32);sequence=unpack('H',2)[0];key=(client_base,sequence)
            if unpack('I',4)[0]!=0 or key not in self.pending:raise ValueError('unmatched query reply')
            x,y=unpack('hh',16);row.update(kind='query_pointer_reply',root_x=x,root_y=y,
                                         same_screen=bool(wire[1]),request_sequence=self.pending.pop(key));return row
        if event==35:
            if len(wire)!=32+unpack('I',4)[0]*4:raise ValueError('malformed GenericEvent')
            return unsupported()
        exact(32)
        if event!=6:return unsupported()
        # Device events have recorder byte order, irrespective of client_swapped.
        if client_base==0:endian='<'
        x,y=unpack('hh',20)
        row.update(kind='device_motion'if client_base==0 else'delivered_motion',
                   root_x=x,root_y=y,originating_client=None,event_time=unpack('I',4)[0])
        if client_base==0:self.device_motion_count+=1
        else:self.delivered_motion_count+=1
        return row
