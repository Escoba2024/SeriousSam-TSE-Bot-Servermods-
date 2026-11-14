"""Source-driven command control-flow model; NOT a compiled/native proof.

Root alone compiles/runs the Win32 fixture. The small evaluator accepts only
the declared command subset and executes its actual guards against API stubs.
"""
from pathlib import Path
import re
from types import SimpleNamespace
import unittest

SOURCE=Path(__file__).with_name('win32_instruction_probe.cpp')


class ProcessExit(Exception):pass


def command_model(wait=0,*,created=True,ok=True,done=1,byte='R',close=True):
    source=SOURCE.read_text();start=source.index('static BOOL command(char wanted) {')
    body=source[start+len('static BOOL command(char wanted) {'):source.index('\n}',start)]
    if 'CommandRead state'not in body:raise AssertionError('bounded own ReaderThread implementation missing')
    events=[];state=SimpleNamespace(byte=0,done=0,ok=False)
    def create(*args):events.append('create');return 1 if created else 0
    def waiting(handle,ms):
        events.append(('wait',handle,ms));state.ok=ok;state.done=done;state.byte=byte;return wait
    def closing(handle):events.append('close');return close
    def exiting(code):events.append(('exit',code));raise ProcessExit(code)
    env=dict(state=state,wanted='R',NULL=0,FALSE=False,TRUE=True,WAIT_OBJECT_0=0,
             CreateThread=create,CommandReader=object(),WaitForSingleObject=waiting,
             CloseHandle=closing,ExitProcess=exiting)
    def expression(text):
        text=text.replace('&&',' and ').replace('||',' or ').replace('&state','state')
        text=re.sub(r'!(?!=)','not ',text)
        return eval(text,{'__builtins__':{}},env)
    try:
        for statement in body.split(';'):
            statement=re.sub(r'//[^\n]*','',statement).strip()
            if not statement:continue
            if statement.startswith('CommandRead state'):continue
            declaration=re.fullmatch(r'(?:const )?(?:HANDLE|DWORD) (\w+)\s*=\s*(.*)',statement,re.S)
            if declaration:env[declaration[1]]=expression(declaration[2]);continue
            guard=re.fullmatch(r'if\((.*?)\)\s*(return FALSE|ExitProcess\(12\))',statement,re.S)
            if guard:
                if expression(guard[1]):
                    if guard[2]=='return FALSE':return False,events
                    exiting(12)
                continue
            if statement.startswith('return '):return bool(expression(statement[7:])),events
            raise AssertionError('unsupported actual command statement: '+statement)
        raise AssertionError('actual command has no return')
    except ProcessExit:return 'EXIT12',events


class CommandReaderTests(unittest.TestCase):
    def test_success_waits_for_reader_closes_handle_and_checks_actual_byte(self):
        result,events=command_model();self.assertTrue(result)
        self.assertEqual(events,['create',('wait',1,15000),'close'])

    def test_timeout_and_wait_failure_exit_without_returning_or_closing_live_thread(self):
        for wait in (258,0xffffffff):
            result,events=command_model(wait);self.assertEqual(result,'EXIT12')
            self.assertEqual(events,['create',('wait',1,15000),('exit',12)])

    def test_failed_thread_creation_never_waits_or_leaves_reader(self):
        result,events=command_model(created=False);self.assertFalse(result);self.assertEqual(events,['create'])

    def test_eof_io_error_wrong_byte_and_close_failure_never_pass(self):
        for options in (dict(ok=False),dict(done=0),dict(byte='Q'),dict(close=False)):
            result,events=command_model(**options);self.assertFalse(result);self.assertEqual(events[-1],'close')


if __name__=='__main__':unittest.main()
