"""Disabled own-Original-client input observer; no launch or input implementation.

Main must freeze/review exact source and independently hold the arena lock and
own-population gate. Importing this module does not import Frida or access /proc.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import sys
import time

RUNTIME_REVIEWED = False
ORIGINAL_GAME_SHA = '1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'
FRIDA_PACKAGE = Path('/srv/tse-frida-probe-20261111/lib/python3.12/site-packages')
A3 = Path('/srv/tse-milestone-a-continuation-evidence-20261112/a3-build017-root-frozen')
PRIVATE = Path('/srv/tse-a1-input-trace-guard-cleanup-library-20261114')
DEPENDENCIES = {
    A3/'frozen-v2/host_binding.py': 'db411bb6757abdc6e6b0ca124f948234fff656a71d8ec7659bb4322cbc18caa8',
    A3/'frozen-v2/controller_guard.py': '3f7142734eb26eb5d6277671b04299bbd0d167be085da14082726feff95274bf',
    A3/'damage_policy.py': '4095c30e55e4b8996a87807f3c55c7357411bf9c5fcd91d93f748d31cef84525',
}
GUARDS_SHA = '3d2b237a787869fee27b02ac22a84f5bdf4e3528e8e2fee2981f05d3e8d7e9d1'
CONTROLS_ROOT = Path('/srv/tse-a1-nosmooth-root-frozen-20261114')
CONTROLS_SHA = '726a5abd10ff646b0c54c318d13cfb373b4bbaa37fa2e4162e05ebe448d99d54'


def require(ok, message):
    if not ok:
        raise ValueError('Original input collector: '+message)


def checked(path, digest):
    raw = Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == digest, 'source/file pin '+str(path))
    return raw


def load_dependencies():
    loaded = []
    for index, (path, digest) in enumerate(DEPENDENCIES.items()):
        checked(path, digest)
        spec = importlib.util.spec_from_file_location('a1_input_frozen_'+str(index), path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded.append(module)
    return loaded


def validate_registry(reg):
    require(reg.get('role') == 'vanilla', 'own vanilla role only')
    require(reg.get('game_sha256') == ORIGINAL_GAME_SHA, 'Original GameMP only')


def validate_effective(observation, mouse_globals, arm):
    require(all(type(observation.get(key)) is int and observation[key] == 0
                for key in ('local_slot','profile','global_smooth')),
            'active controls profile/smoothing changed')
    for axis, binding in [('x',1),('y',2)]:
        values = observation['axes'][axis]
        for key, wanted in [('binding',binding),('invert',0),('relative',1),
                            ('smooth',0),('effective_smooth',0),('sensitivity',50),
                            ('deadzone',0),('influence',1)]:
            require(type(values.get(key)) in (int,float) and values[key] == wanted,
                    'effective '+axis+' '+key+' changed')
    require(observation['source_pointer'] == int(arm['source'],16)
            and observation['controls_address'] == int(arm['controls'],16),
            'controls/source registry differs')
    require(mouse_globals == (0,.25,0), 'effective mouse globals changed')


def validate_packet(packet, *, final=False):
    for key in ('faults', 'dropped', 'game_state_writes'):
        require(type(packet.get(key)) is int and packet[key] == 0, key)
    require(packet.get('native_qualified') is False, 'invalid qualification')
    require(packet.get('detach_errors') == [], 'detach errors')
    require(type(packet.get('in_flight')) is int and packet['in_flight'] >= 0,
            'in-flight denominator')
    require(isinstance(packet.get('records'), list) and len(packet['records']) <= 256,
            'record bound')
    require(packet.get('enabled') is (not final), 'unexpected observer stop')
    require(packet.get('stop_reason') == ('host requested' if final else ''),
            'unexpected stop reason')
    if final:
        require(packet['in_flight'] == 0 and packet.get('restored') is True,
                'in-flight or unrestored final listener')


class Collector:
    def __init__(self, reader, registry, evidence, ownership_gate):
        self.reader = reader
        self.registry = registry
        self.original_bytes_verified = False
        self.original_verification_receipt = None
        self.evidence = Path(evidence)
        self.ownership_gate = ownership_gate
        self.session = self.script = self.stream = None
        self.policy = self.host = self.message_guard = None
        self.guards = None
        self.controls_module = None
        self.failed = False
        self.used = False
        self.closed = False
        self.cleanup_errors = []

    def _host_pin(self):
        # Root callback attests its still-held lock, isolated population and
        # role ownership. Host pins alone do not prove exclusivity.
        require(self.ownership_gate() is True, 'exclusive owned fixture gate')
        validate_registry(self.registry)
        self.host.validate_host(self.registry)
        require(tuple(self.reader.identity) == (self.registry['pid'],
                    self.registry['start_ticks']), 'reader process differs')
        require(self.reader.rotation_diagnostics is True,
                'existing Original rotation-field guards required')
        self.reader._guard()
        net = (Path('/proc')/str(self.registry['pid'])/'ns/net').stat().st_ino
        require(net == self.registry['net_namespace_inode'], 'network namespace changed')

    def _pin(self):
        self._host_pin()
        arm = self.registry['arm']
        for key, name in [('engine_base','Engine.dll'), ('game_base','GameMP.dll')]:
            require(int(arm[key], 16) == self.registry['modules'][name]['base'],
                    'arm module differs from pinned mapping')
        # Snapshot omits repeated code-guard verification here: this collector
        # owns an intentional CreateAction code interception. Whole Original
        # ranges are checked before attach and again after detach instead.
        observation = self.controls_module.snapshot(self.reader._read,
            self.registry['modules']['GameMP.dll']['base'],
            self.registry['modules']['Engine.dll']['base'], local_slot=0)
        engine = self.registry['modules']['Engine.dll']['base']
        acceleration, sensitivity = struct.unpack('<if', self.reader._read(engine+0x1e7f48,8))
        prescan = struct.unpack('<i',self.reader._read(engine+0x1e7f5c,4))[0]
        validate_effective(observation, (acceleration,sensitivity,prescan), arm)
        self.reader._guard()

    def _record(self, row):
        require(self.stream is not None, 'journal absent')
        row = dict(row, host_monotonic=time.monotonic(), host_epoch_ms=time.time()*1000)
        self.stream.write(json.dumps(row, allow_nan=False)+'\n')
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def verify_original(self):
        self._host_pin()
        for guard in self.guards['guards']:
            module = self.guards['modules'][guard['module']]
            base = self.registry['modules'][guard['module']]['base']
            expected = self.policy.rebased(guard, module['preferred_base'],
                                           base, module['image_size'])
            require(self.reader._read(base+guard['rva'], len(expected)) == expected,
                    'full Original byte range differs: '+guard['label'])
        self._host_pin()

    def arm(self):
        if not RUNTIME_REVIEWED:
            raise RuntimeError('disabled draft: main review/freeze required')
        require(not self.used and not self.closed, 'one arm only')
        self.used = True
        self.host, guard_module, self.policy = load_dependencies()
        controls_path = CONTROLS_ROOT/'a1_controls_diagnostic.py'
        checked(controls_path, CONTROLS_SHA)
        spec = importlib.util.spec_from_file_location('a1_input_frozen_controls', controls_path)
        self.controls_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.controls_module)
        self.message_guard = guard_module.MessageGuard({'errors': []})
        self.guards = json.loads(checked(PRIVATE/'original-input-guards.json', GUARDS_SHA))
        self._pin()
        self.verify_original()
        # Parent manifest must pin this source, JS, Frida __init__ and extension
        # in addition to these inherited helpers and private Original guards.
        manifest = json.loads((PRIVATE/'source-manifest.json').read_text())
        require(manifest['runtime_reviewed'] is True, 'reviewed manifest required')
        for path, digest in manifest['source_pins'].items():
            checked(path, digest)
        checked(Path(__file__), manifest['source_pins'][str(Path(__file__))])
        hook_path = Path(__file__).with_name('a1_original_input_readonly.js')
        hook_source = checked(hook_path, manifest['source_pins'][str(hook_path)]).decode()
        sys.path.insert(0, str(FRIDA_PACKAGE))
        import frida
        require(Path(frida.__file__).resolve() == FRIDA_PACKAGE/'frida/__init__.py'
                and Path(frida._frida.__file__).resolve() == FRIDA_PACKAGE/'frida/_frida.abi3.so'
                and frida.__version__ == '17.26.2', 'Frida origin/version')
        try:
            self.stream = (self.evidence/'original-input-trace.jsonl').open('x')
            os.chmod(self.stream.name, 0o600)
            self._record({'phase': 'pre-arm', 'native_qualified': False})
            self.session = frida.get_local_device().attach(self.registry['pid'])
            self._pin()
            self.script = self.session.create_script(hook_source)
            self.script.on('message', self.message_guard.on_message)
            self.script.load()
            self._pin()
            config = dict(self.registry['arm'], pid=self.registry['pid'],
                          max_records=256, max_calls=4096, ttl_ms=90000)
            result = self.script.exports_sync.arm(config, self.guards)
            require(result.get('armed') is True, 'arm refused')
            self._record({'phase': 'armed', 'result': result})
            binding=self.await_ready()
            result.update(ready=True,input_thread=binding['input_thread'])
            return result
        except BaseException:
            self.failed = True
            try:
                self.close()
            except BaseException:
                pass  # Errors retained; root's outer cleanup must still run.
            raise

    def drain(self, *, final=False):
        try:
            require(not self.failed or final, 'prior sticky failure')
            self._pin()
            packet = self.script.exports_sync.drain()
            self.message_guard.check()
            validate_packet(packet, final=final)
            self._record({'phase': 'final' if final else 'drain', 'packet': packet})
            self._pin()
            return packet
        except BaseException:
            self.failed = True
            raise

    def await_ready(self):
        """Observe at most one second; no mouse/route/fire action or retry."""
        deadline = time.monotonic()+1
        for unused in range(21):
            packet = self.drain()
            if packet.get('ready') is True:
                return packet
            if time.monotonic() >= deadline:
                break
            time.sleep(.05)
        self.failed = True
        raise RuntimeError('no complete Original input/action sequence; no input allowed')

    def before_input(self, *, control, pixels=None):
        """Only inherited calibration/aim; the controller separately counts them."""
        require(control in ('look_right','look_left','look_horizontal','look_vertical','forward'),
                'diagnostic calibration/aim scope: no route/fire')
        require((control=='forward' and pixels is None) or
                (control!='forward' and type(pixels) is int and 0<abs(pixels)<=12),
                'diagnostic input shape')
        require(not self.failed and not self.closed, 'inactive/failed observer')
        packet = self.drain()
        if packet.get('ready') is not True:
            self.failed = True
            raise RuntimeError('complete Original input/action binding missing; no input allowed')
        return packet

    def _stop_and_wait(self):
        """No unload is safe until admitted callback pairs completed and detached."""
        self.policy.cleanup_steps([('pre-stop pins',self._host_pin),
            ('stop',self.script.exports_sync.stop)],self.cleanup_errors)
        deadline=time.monotonic()+1
        for unused in range(21):
            try:
                packet=self.script.exports_sync.drain()
            except BaseException as error:
                self.cleanup_errors.append('stop drain:'+repr(error));return False
            if not isinstance(packet,dict):
                self.cleanup_errors.append('malformed quiescence packet');return False
            # A sticky JS/message error invalidates the trace, but cannot skip
            # safe detach/unload once the actual RPC packet proves idle/restored.
            self.policy.cleanup_steps([('cleanup messages',self.message_guard.check)],
                                      self.cleanup_errors)
            try:
                self._record({'phase':'quiescence','packet':packet})
            except BaseException as error:
                self.cleanup_errors.append('cleanup journal:'+repr(error))
            if (type(packet.get('in_flight')) is int and packet['in_flight']==0
                    and packet.get('enabled') is False and packet.get('restored') is True):
                self.policy.cleanup_steps([('final packet',lambda:validate_packet(packet,final=True))],
                                          self.cleanup_errors)
                return True
            if time.monotonic()>=deadline:
                break
            time.sleep(.05)
        self.cleanup_errors.append('bounded quiescence timeout: retain script/session; outer owned-role cleanup required')
        return False

    def close(self):
        if self.closed:
            require(not self.cleanup_errors, 'prior cleanup errors')
            return
        if self.policy is None:
            require(self.session is None and self.script is None and self.stream is None,
                    'resources exist without validated cleanup helper')
            self.closed = True;return
        steps = []
        safe=True
        self.original_bytes_verified = False
        self.original_verification_receipt = dict(
            phase='host-original-verification',attempted=False,verified=False,
            error='not attempted',native_qualified=False)
        if self.script is not None:
            safe=self._stop_and_wait()
        if safe:
            def unload():
                self.script.unload();self.script=None
            def detach():
                self.session.detach();self.session=None
            if self.script is not None:steps.append(('unload',unload))
            if self.session is not None:steps.append(('detach',detach))
            def verify_restored_original():
                receipt=self.original_verification_receipt
                receipt.update(attempted=True,error=None)
                try:
                    self.verify_original()
                except BaseException as error:
                    receipt['error']=repr(error)
                    raise
                self.original_bytes_verified = True
                receipt['verified']=True
            if steps:steps.append(('verify full Original bytes',verify_restored_original))
        else:
            self.original_verification_receipt['error']='not attempted: callback quiescence unproven'
        if self.stream is not None:
            def record_verification():
                receipt=self.original_verification_receipt
                receipt.update(script_unloaded=self.script is None,
                               session_detached=self.session is None,
                               cleanup_errors=list(self.cleanup_errors))
                self._record(receipt)
            steps.append(('host Original verification receipt',record_verification))
            steps.append(('close journal', self.stream.close))
        self.policy.cleanup_steps(steps, self.cleanup_errors)
        self.closed=self.script is None and self.session is None
        if self.cleanup_errors:
            self.failed = True
            raise RuntimeError('Original input cleanup: '+'; '.join(self.cleanup_errors))
