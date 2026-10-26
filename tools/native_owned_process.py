"""Bounded pidfd cleanup for a direct Popen child, never arbitrary PID adoption."""
import math
import os
from pathlib import Path
import signal
import subprocess


class OwnedProcess:
    def __init__(self,process):
        if not isinstance(process,subprocess.Popen) or process.poll() is not None:
            raise ValueError('live directly owned Popen child required')
        path=Path('/proc')/str(process.pid)/'stat'
        before=path.read_text().rsplit(') ',1)[1].split()
        if int(before[1])!=os.getpid():raise ValueError('process is not our direct child')
        fd=os.pidfd_open(process.pid)
        try:
            after=path.read_text().rsplit(') ',1)[1].split()
            if before[19]!=after[19] or before[1]!=after[1] or process.poll() is not None:
                raise ValueError('child identity changed while binding pidfd')
        except BaseException:
            os.close(fd);raise
        self.process=process;self.pidfd=fd;self.start_ticks=int(before[19])

    def close(self):
        if self.process.poll() is None:raise RuntimeError('cannot discard live child cleanup handle')
        if self.pidfd is not None:os.close(self.pidfd);self.pidfd=None

    def stop(self,*,timeout=10,kill_timeout=5):
        if any(type(t) not in (int,float) or not math.isfinite(t) or not 0<t<=30 for t in (timeout,kill_timeout)):
            raise ValueError('bounded child stop timeouts required')
        if self.process.poll() is None:
            if self.pidfd is None:raise RuntimeError('live child without identity-bound handle')
            try:signal.pidfd_send_signal(self.pidfd,signal.SIGTERM)
            except ProcessLookupError:pass
            try:self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                try:signal.pidfd_send_signal(self.pidfd,signal.SIGKILL)
                except ProcessLookupError:pass
                self.process.wait(timeout=kill_timeout)
        self.close()
