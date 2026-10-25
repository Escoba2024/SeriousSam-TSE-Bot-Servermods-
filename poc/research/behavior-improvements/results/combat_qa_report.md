# Combat-QA report (offline simulation - NOT_TESTED_RETAIL)

Seeds/cell: 16 (seed base 0xC0FFEE + 977*i). Invariants: **11/11 PASS**.

- PASS `I1-beginner-floor` - t1 mirror draws base=6 cand=3, hitrate 0.213->0.302 (F-2)
- PASS `I2-skill-monotonicity` - candidate mirror aim-err deg t1..t5: 3.54, 2.74, 2.22, 1.66, 1.33; hitrates: 0.302, 0.373, 0.382, 0.449, 0.569
- PASS `I3-ladder` - t2>t1: 14-2; t3>t2: 11-4; t4>t3: 12-4; t5>t4: 15-1; t5>t1: 15-1
- PASS `I4-cross-policy` - candidate beats baseline in 7/7 same-tier cells: t1p2@18m 15-0 D1; t2p2@18m 12-2 D2; t3p2@18m 12-1 D3; t4p2@18m 14-2 D0; t5p2@18m 13-3 D0; t3p0@10m 13-3 D0; t3p4@40m 10-6 D0
- PASS `I5-weapon-diversity` - laser share mirrors base=['0.98', '0.97', '0.93', '0.94', '0.94'] cand=['0.01', '0.02', '0.01', '0.00', '0.00']; distinct weapons cand=[6, 5, 6, 3, 3] (F-1)
- PASS `I6-latency-lead` - mover t5 hitrate 0->200ms base 0.798->0.381, cand 0.781->0.768 (F-3)
- PASS `I7-strafe-active` - strafe ticks/duel cand=[462, 227, 199, 157, 137] base=0 (shipped bot_fStrafeScale=0, F-5)
- PASS `I8-cover-retreat` - cover probe: baseline  los_break_s=-1.00 final=(-140.0,0.0) | candidate los_break_s=2.40 final=(-15.2,7.0) (F-4)
- PASS `I9-persona-difference` - weapon-histogram L1 aggressor-vs-marksman cand=0.89 base=0.02; mean-range spread=8.0 m; tops={0: 'minigun', 1: 'minigun', 2: 'minigun', 3: 'minigun', 4: 'laser', 5: 'minigun'}
- PASS `I10-reaction-ordering` - candidate first-fire s t1..t5: 2.94, 1.56, 0.98, 0.68, 0.55
- PASS `I11-ttk-ordering` - candidate mirror duration t1=26.3s t5=7.0s

## CPU bench
```
baseline  policy+overlay: 0.264 us/tick (sink=1916322.2) -> 0.0005% of one core @20Hz/bot
candidate policy+overlay: 0.424 us/tick (sink=729007.5) -> 0.0008% of one core @20Hz/bot
```

## Cover probe
```
baseline  los_break_s=-1.00 final=(-140.0,0.0)
candidate los_break_s=2.40 final=(-15.2,7.0)
```
