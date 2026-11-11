# Trial1 Supply review and retained-goal correction

Independent read-only review used the actual completed private folder `/srv/tse-milestone-a-evidence-20261111/arena-trial-1-193924`, specifically `result.json`, `queries.json`, `session-health.jsonl` and the frozen `botA.log`, `botB.log`, `server.log`. Final cleanup logs were not substituted for the observation logs. No runtime or native verdict was changed by this task.

Old botA: DLL `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`. New MITTEL botB: build002 DLL `50b132c0d83d209b399c7178bcb41dc16c0ee1ffe7c28652cecbd69a07baafd5`. Both cohorts have four bots. Original server and controlled original Retail client use GameMP SHA256 `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208`. Map: Red Station. Observation:240.085903s, 100/100 queries with nine players,1561 passive session/health samples, zero recorded bad-sync or disconnect matches, normal owned cleanup. These are limited native facts, not final acceptance.

## Combat and route observations

Query scores end old+7/new+25. Server kill text separately attributes15 new-to-old kills versus2 old-to-new,7 new-to-observer versus1 old-to-observer, and5 new-to-new versus4 old-to-old. New also has two negative-score events: one explicit explosive suicide and one `passed away` event whose cause is not established. Thus the score improvement is not only observer kills, but this is still one short, unpaired ordering and one tier/map. It does not replace three matched comparisons.

The longest new uninterrupted same-item NAV run lasts28s and traverses approximately346m across many hops and a large map extent; this is travel, not the bounded ordinary-edge cycle previously seen on Hole. No new `CecilItemTransitEnd` occurs. The new bounded-failure policy was therefore not exercised, and successful pickup/attack after that specific rejection remains unproven. These Red Station observations cannot close Hole/Skulls or special-action gates.

Actual life records show19 old and9 new death-to-next-spawn pairs, each corroborated by a same-life sampled nonpositive-health state, with maximum logged delay1.85s in both cohorts. No unmatched final death appears in these frozen bot logs. This does not establish exact health-death timing or every native first tick after respawn.

## Supply failure and root cause

First useful ranged acquisition means a gained weapon bit among IDs4–14 excluding Chainsaw10; starting Colts do not satisfy it. Latency below is from the logged native spawn to the actual ownership gain, not to selecting a goal.

| Initial local life | Old048 | New MITTEL build002 |
|---|---|---|
| local0 |11.45s pickup |53.55s pickup |
| local1 |3.95s pickup |death after64.30s without useful ranged pickup |
| local2 |death after37.95s without useful ranged pickup |12.75s pickup |
| local3 |2.40s pickup |24.15s pickup |

Across the complete process logs, old has23 spawned lives with15 observed useful ranged gains; new has13 lives with11 gains. These totals include final lives censored by the end of observation and initial old lives beginning before the mixed-cohort window. They must not be converted into a first-ten Supply PASS. New subsequent lives also include53.15s and36.80s delays. Sampled shot counters increase after13/15 old and10/11 new gains; the other cases lack subsequent sampled attack evidence. These counters prove emitted attack actions, not hits.

New local0 repeatedly selects and loses mapped weapons before finally obtaining its first gun: goal starts at ticks35,219,316,637 and958, with `unavailable` endings at195,242,520 and877; pickup occurs at1106. New local1's next life similarly drops/reselects goals repeatedly at ticks1460–1625 and obtains its gun only at2421. Local0 is under NAV ownership in48/54 sampled pre-pickup states, local1 in61/65 pre-death states. Absence of Driver movement ownership is not the main bottleneck.

Source review finds a concrete inconsistency in `BotSupplyTick`: mapped-weapon retention includes `input.enemy_distance>=8`, so a nearby opponent makes an otherwise live, needed weapon `unavailable`, clears its directed path and resets subsequent goal selection. Ordinary item retention does not do that. A later existing branch already pauses item movement below8 while yielding action ownership to visible combat and preserving the attempt. This churn can repeatedly replace partially completed routes and assign fresh deadlines. The logs' generic `unavailable` reason cannot independently disambiguate every occurrence, but the controlled regression reproduces the distance-triggered invalidation in the actual native bridge.

The fix removes the distance condition from **retaining an existing mapped weapon only**. Initial mapped admission still requires distance at least8. The close-combat action-yield branch remains; typed live need, allowed weapons, ownership, graph/connector validation, death/reset handling, original fixed deadline and rejection backoff remain. A paused attempt can still time out; pauses do not buy extra time. No Driver, aim, loadout, range limit or physical movement policy changes are included.

Behavioral RED: six assertions fail on build002 source. GREEN: repeated7.9/8.1 distance crossings retain one mapped goal and its original start/deadline, yield close-fight actions, resume the same urgent route, and end normally after a real ownership gain or reject at the original timeout. Existing disappearance, ownership, allowed-weapon, connector, close-admission and movement guards remain covered.

## Early regular damage evidence

Server slot3 in a distinct respawn life has spawned time171.8558807373. The passive server samples show HP100 at game time172.0558929443 (age0.2000122s), followed by HP-1085.8236084 at172.1558990479 (age0.3000183s). Server log line651 attributes the matching death to a normal cannon kill by a new bot, between SYNCOK ticks171.41 and172.41. An earlier same-attacker/victim cannon line643 belongs to the previous life and was excluded. This proves an observed lethal normal hit within the sampled age interval(0.20,0.30]s; it does not prove damage on the first50ms tick.

## Verification boundary

The actual bridge passed1378 checks both normally and with `--sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es`. The extracted native Driver action suite passed under ASan/UBSan, and `python3 -m unittest discover -s tools` passed183 tests, including the arena feedback checks. A fresh build and new complete native observations are required after this correction. Build002 comparisons remain baseline evidence; neither their scores nor the portable correction close A3, Supply or all-map acceptance.
