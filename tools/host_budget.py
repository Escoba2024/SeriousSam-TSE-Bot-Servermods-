"""Measured host budget; CPU is /proc/stat delta, not load average."""
import math
class HostBudget:
 LIMITS={'cpu_busy_ceiling_percent':75.,'min_mem_available_bytes':1610612736,'min_disk_free_bytes':8589934592,'target_sample_interval_seconds':1.}
 def __init__(self):self.samples=[];self.previous=None
 def add(self,when,cpu_line,mem_available,disk_free):
  if type(when)not in(int,float)or not math.isfinite(when):raise ValueError('invalid monotonic clock')
  parts=cpu_line.split()
  if parts[0]!='cpu'or len(parts)<9:raise ValueError('aggregate CPU counters required')
  counters=[int(n)for n in parts[1:9]] # user,nice,system,idle,iowait,irq,softirq,steal; guest already included
  if min(counters)<0:raise ValueError('negative CPU counter')
  total=sum(counters);idle=counters[3]+counters[4];percent=None;gap=None
  if self.previous:
   t,old_total,old_idle=self.previous;gap=when-t;delta=total-old_total;idle_delta=idle-old_idle
   if gap<=0 or delta<=0 or not 0<=idle_delta<=delta:raise ValueError('CPU/clock discontinuity')
   percent=100*(delta-idle_delta)/delta
  if type(mem_available)is not int or type(disk_free)is not int:raise ValueError('byte counters must be integers')
  failures=[]
  if percent is not None and percent>self.LIMITS['cpu_busy_ceiling_percent']:failures.append('host CPU delta exceeds75%')
  if mem_available<self.LIMITS['min_mem_available_bytes']:failures.append('MemAvailable below1.5GiB')
  if disk_free<self.LIMITS['min_disk_free_bytes']:failures.append('disk free below8GiB')
  row={'monotonic':when,'cpu_busy_percent':percent,'sample_gap_seconds':gap,'mem_available_bytes':mem_available,'disk_free_bytes':disk_free,'violations':failures}
  self.samples.append(row);self.previous=(when,total,idle)
  if failures:raise ValueError('; '.join(failures))
  return row
 def summary(self):
  return {'scope':'HOST aggregate non-idle delta including other workloads; interval averages not instantaneous peaks','limits':dict(self.LIMITS),'samples':len(self.samples),'cpu_busy_max_measured_percent':max((r['cpu_busy_percent']for r in self.samples if r['cpu_busy_percent']is not None),default=None),'mem_available_min_bytes':min((r['mem_available_bytes']for r in self.samples),default=None),'disk_free_min_bytes':min((r['disk_free_bytes']for r in self.samples),default=None),'max_sample_gap_seconds':max((r['sample_gap_seconds']for r in self.samples if r['sample_gap_seconds']is not None),default=None),'budget_pass_claim':False}
