"""Pure defensive scope for the inherited no-fire diagnostic, never input itself."""

class InputScope:
    PREFIX=(('look_right',None),('forward',None),('look_left',None),
            ('forward',None),('look_vertical',12),('look_vertical',-12))
    def __init__(self):self.count=0;self.failed=False
    def admit(self,role,control,seconds,pixels):
        try:
            if role!='vanilla' or seconds!=.1 or type(seconds) not in (int,float):
                raise ValueError('trace only inherited vanilla .1s controls')
            if self.failed or self.count>=48:raise ValueError('trace input scope exhausted/failed')
            if self.count<len(self.PREFIX):
                if (control,pixels)!=self.PREFIX[self.count]:raise ValueError('trace inherited calibration order')
            elif control not in ('look_horizontal','look_vertical')or type(pixels)is not int or not 1<=abs(pixels)<=12:
                raise ValueError('trace aim only; no route or fire')
            self.count+=1
            return 12 if control=='look_right'else-12 if control=='look_left'else pixels
        except BaseException:
            self.failed=True;raise


def trace_complete(report, verdict):
    """Keep two explicit non-PASS diagnostic scopes, never an A1 qualification."""
    mode=report.get('observer_mode')
    if mode not in ('instrumented-trace','uninstrumented-control'):return False
    expected='TRACE_ONLY_NO_FIRE'if mode=='instrumented-trace'else'CONTROL_ONLY_NO_FIRE'
    common=(report.get('status')==expected
        and report.get('shooter_preparation',{}).get('status')=='TRACE_ONLY_NO_FIRE'
        and report.get('normal_route_or_fire')is False
        and report.get('diagnostic_only')is True
        and report.get('restoration',{}).get('restored')is True
        and report.get('post_close_logs',{}).get('accepted')is True
        and all(r.get('closed')is True for r in report.get('displays',{}).values())
        and verdict.reasons==('window_not_passed',))
    if not common:return False
    if mode=='uninstrumented-control':
        return (report.get('collector_requested')is False
            and not any(key in report for key in ('collector_arm','collector_cleanup','collector_worker','collector_ipc_timings')))
    return (report.get('collector_requested')is True
        and report.get('collector_cleanup',{}).get('closed')is True
        and report.get('collector_cleanup',{}).get('original_bytes_verified')is True
        and report.get('collector_worker',{}).get('reaped')is True)
