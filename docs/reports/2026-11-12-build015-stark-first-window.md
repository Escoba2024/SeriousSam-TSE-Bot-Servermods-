# Build015 STARK comparison: first completed window

Recorded UTC: 2026-11-12T09:47:46.469772+00:00

The predeclared single identical capture retry `arena015public-damage-checked-swap0-trial-2-093722` passed the unchanged initial-state guard and completed 120.12392144789919 seconds. The original `085731` capture failure remains FAIL and is retained; this new observation is not a reclassification of it. Strict post-analysis passed, including lifecycle accounting, full passive damage coverage, exact common initial states, the Original loaded-body restore and native kill-pair/lethal-record correspondence. All four native roles closed normally; 640 tracked fixture files were restored. No sync/disconnect events were reported in the tested window or retained closed-log checks.

| Measurement | Previous public DLL | Build015 STARK |
|---|---:|---:|
| Observed lives | 40 | 17 |
| Observed HP deaths | 36 | 13 |
| Right-censored lives | 4 | 4 |
| Lives with useful weapon possession | 3 | 13 |
| Completed lives without useful weapon | 35 | 3 |
| Censored lives without useful weapon | 2 | 1 |
| Lives with useful current weapon | 1 | 13 |
| Lives with useful ranged fire request | 0 | 11 |
| Query frag change | 15 | 35 |
| Known-foreign damage calls | 62 | 118 |
| HP loss capped at pre-hit health | 2156.3333282470703 | 3196.7954902648926 |
| Lethal foreign-damage calls | 15 | 35 |

Among successful acquisitions only, median observed acquisition age was 5.5503387451171875 seconds for public and 5.900360107421875 seconds for STARK; the sharply different successful/failed/censored denominators above are essential. Candidate first-life acquisition ages were about 3.85, 4.05, 2.35 and 10.40 seconds. No human difficulty judgment follows from this single bot comparison. Opposite starts, final DEMON comparisons and full A3 acceptance remain open.

Maximum measured aggregate CPU was 61.556603773584904%; minimum MemAvailable 2184712192 bytes. Maximum gameplay sample gap was 1.745555441826582 seconds. The separate 47.02645340212621-second setup gap is retained, so this is not complete startup resource or long-duration qualification.

Candidate DLL SHA256 remains `10015f213c05b2faefc312e11a310dae63d64eda1c7173601c6ffd4386a70313`, build source `b6b776ddbc761ee96049e6626edd5af4895cb3af`; candidate has not been deployed live.
