"""Text prepared during Root's exclusive native window; NOT EXECUTED yet.

The future implementation must satisfy this contract only after observed RED.
All fixtures are synthetic protocol bytes; they never open an X display.
"""
import importlib
import struct
import unittest


def implementation(case):
    try:return importlib.import_module('xrecord_core_method')
    except ModuleNotFoundError:case.fail('missing separately disabled XRecord core method implementation')


def request(opcode,size,minor=0,endian='<'):
    value=bytearray(size);struct.pack_into(endian+'BBH',value,0,opcode,minor,size//4)
    return value


def fake_input(major=137,dx=12,dy=0,endian='<'):
    value=request(major,36,2,endian)
    value[4]=6;value[5]=1
    struct.pack_into(endian+'hh',value,24,dx,dy)
    return bytes(value)


def warp(x=400,y=300,endian='<'):
    value=request(41,24,endian=endian)
    struct.pack_into(endian+'I',value,8,0x100)
    struct.pack_into(endian+'hh',value,20,x,y)
    return bytes(value)


def query(endian='<'):
    value=request(38,8,endian=endian);struct.pack_into(endian+'I',value,4,0x100)
    return bytes(value)


def query_reply(sequence,x,y,endian='<'):
    value=bytearray(32);value[0]=1;value[1]=1
    struct.pack_into(endian+'H',value,2,sequence)
    struct.pack_into(endian+'I',value,8,0x100)
    struct.pack_into(endian+'hhhh',value,16,x,y,x,y)
    return bytes(value)


def motion(x=412,y=300,sequence=0,endian='<'):
    value=bytearray(32);value[0]=6
    struct.pack_into(endian+'HI',value,2,sequence,1234)
    struct.pack_into(endian+'I',value,8,0x100)
    struct.pack_into(endian+'hhhh',value,20,x,y,x,y)
    return bytes(value)


class CoreProtocolTests(unittest.TestCase):
    def setUp(self):self.m=implementation(self)
    def record(self,wire,category=1,client=0x200000,sequence=10,swapped=False):
        return dict(category=category,client_base=client,client_sequence=sequence,
                    server_time=1234,client_swapped=swapped,wire=wire)
    def stream(self):return self.m.CoreTrace(xtest_opcode=137)
    def test_native_and_wire_sizes_are_separate_on_pinned_lp64_host(self):
        layout=self.m.native_layout()
        self.assertEqual(layout['pointer_bytes'],8)
        self.assertEqual(layout['intercept_size'],48)
        self.assertEqual(layout['range_size'],32)
        self.assertEqual(layout['wire_range_bytes'],24)
        self.assertEqual(layout['intercept_offsets'],dict(id_base=0,server_time=8,
            client_seq=16,category=24,client_swapped=28,data=32,data_len=40))
    def test_dynamic_xtest_major_and_single_relative_request_decode(self):
        row=self.stream().accept(**self.record(fake_input()))
        self.assertEqual((row['kind'],row['dx'],row['dy']),('xtest_relative_motion',12,0))
        self.assertEqual(row['requested_device'],0)
    def test_swapped_client_request_is_parsed_in_its_own_byte_order(self):
        row=self.stream().accept(**self.record(fake_input(dx=-12,endian='>'),swapped=True))
        self.assertEqual(row['dx'],-12)
    def test_other_extension_opcode_is_explicitly_unsupported(self):
        trace=self.stream();row=trace.accept(**self.record(fake_input(major=138)))
        self.assertEqual(row['kind'],'unsupported');self.assertEqual(trace.unsupported,1)
    def test_warp_request_is_not_a_confirmed_pointer_position(self):
        row=self.stream().accept(**self.record(warp()))
        self.assertEqual((row['kind'],row['dst_x'],row['dst_y']),('warp_request',400,300))
        self.assertIs(row['position_confirmed'],False)
    def test_query_reply_requires_matching_client_and_request_sequence(self):
        trace=self.stream();trace.accept(**self.record(query(),sequence=10))
        row=trace.accept(**self.record(query_reply(10,412,300),category=0))
        self.assertEqual((row['kind'],row['root_x'],row['root_y']),('query_pointer_reply',412,300))
        self.assertEqual(row['request_sequence'],10)
    def test_unmatched_query_reply_is_failure(self):
        with self.assertRaises(ValueError):self.stream().accept(**self.record(query_reply(10,412,300),category=0))
    def test_query_from_different_client_does_not_match(self):
        trace=self.stream();trace.accept(**self.record(query(),sequence=10))
        with self.assertRaises(ValueError):trace.accept(**self.record(query_reply(10,412,300),category=0,client=0x400000))
    def test_device_and_delivered_motion_copies_stay_separate(self):
        trace=self.stream()
        a=trace.accept(**self.record(motion(),category=0,client=0))
        b=trace.accept(**self.record(motion(),category=0,client=0x200000))
        self.assertEqual(a['kind'],'device_motion');self.assertEqual(b['kind'],'delivered_motion')
        self.assertEqual(a['root_x'],412);self.assertIsNone(a['originating_client'])
        self.assertEqual(trace.device_motion_count,1);self.assertEqual(trace.delivered_motion_count,1)
    def test_generic_event_is_explicitly_unqualified_never_core_motion(self):
        value=bytearray(36);value[0]=35;struct.pack_into('<I',value,4,1)
        trace=self.stream();row=trace.accept(**self.record(bytes(value),category=0))
        self.assertEqual(row['kind'],'unsupported');self.assertFalse(trace.xi2_complete)
    def test_truncated_or_bad_declared_request_length_is_failure(self):
        for value in(fake_input()[:-1],bytes(request(41,20)),b'',b'\x29\0\0\0'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):self.stream().accept(**self.record(value))
    def test_long_or_unknown_server_event_is_not_silently_treated_as_32bytes(self):
        value=bytearray(32);value[0]=35;struct.pack_into('<I',value,4,2)
        with self.assertRaises(ValueError):self.stream().accept(**self.record(bytes(value),category=0))
    def test_invalid_categories_and_noninteger_metadata_fail(self):
        for change in({'category':99},{'client_sequence':True},{'server_time':float('nan')},{'client_base':-1}):
            row=self.record(fake_input());row.update(change)
            with self.subTest(change=change):
                with self.assertRaises(ValueError):self.stream().accept(**row)


class CoreLimitsTests(unittest.TestCase):
    def setUp(self):self.m=implementation(self)
    def test_limits_are_exact_root_contract(self):
        self.assertEqual(self.m.LIMITS,dict(display=':167',recorder_seconds=15,records=1024,
            total_bytes=2*1024*1024,record_bytes=16384,arm_seconds=3,stop_seconds=3,
            driver_seconds=2,controller_seconds=30,cleanup_seconds=5))
    def test_four_byte_unit_bound_is_checked_before_any_pointer_copy(self):
        seen=[]
        def read(pointer,length):seen.append((pointer,length));return b'\0'*length
        out=self.m.copy_payload(data_pointer=123,data_len=8,reader=read)
        self.assertEqual(len(out),32);self.assertEqual(seen,[(123,32)])
        for count in(-1,4097,True):
            seen.clear()
            with self.assertRaises(ValueError):self.m.copy_payload(data_pointer=123,data_len=count,reader=read)
            self.assertEqual(seen,[])
    def test_null_pointer_nonzero_length_fails_before_copy(self):
        def read(*unused):self.fail('invalid memory must not be read')
        with self.assertRaises(ValueError):self.m.copy_payload(data_pointer=0,data_len=1,reader=read)
    def test_record_and_total_serialized_byte_limits_are_sticky(self):
        budget=self.m.CaptureBudget(started=1.)
        for unused in range(1024):budget.charge(record_bytes=32,serialized_bytes=64,now=2.)
        with self.assertRaises(ValueError):budget.charge(record_bytes=32,serialized_bytes=64,now=2.)
        with self.assertRaisesRegex(ValueError,'sticky'):budget.charge(record_bytes=0,serialized_bytes=0,now=2.)
        budget=self.m.CaptureBudget(started=1.)
        with self.assertRaises(ValueError):budget.charge(record_bytes=16385,serialized_bytes=16385,now=2.)
        budget=self.m.CaptureBudget(started=1.)
        for unused in range(128):budget.charge(record_bytes=16384,serialized_bytes=16384,now=2.)
        with self.assertRaises(ValueError):budget.charge(record_bytes=1,serialized_bytes=1,now=2.)
    def test_fifteen_seconds_or_invalid_clock_is_failure(self):
        for now in(16.,float('nan'),0.):
            with self.subTest(now=now):
                with self.assertRaises(ValueError):self.m.CaptureBudget(started=1.).charge(record_bytes=0,serialized_bytes=0,now=now)


if __name__=='__main__':unittest.main()
