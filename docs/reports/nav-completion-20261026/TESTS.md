# Portable verification

All commands in verification.json exited0, serial nice19. Native parent had an isolated1bot run active; these timings describe synthetic offline work only.

Initial focused test:12checks,10 failures; explicit pickup-cap API initially failed compilation; same-ID floor-change test:29checks,1 failure. All fixed and29completion checks now pass. Existing imported C2 original-source reproducer independently confirms its8expected failures.

```text
NAV GRAPH PASS (0 failures, 1084 checks)
NAV ASTAR PASS (0 failures, 97 checks)
NAV AGENT PASS (0 failures, 3272 checks)
NAV SEAM PASS (0 failures, 307 checks)
ITEM UTILITY: 378 checks, 0 failures
ITEM UTILITY PASS
SCORING TERMS: 91711 checks, 0 failures
SCORING TERMS PASS
BOTCORE ADAPTER: 401 checks, 0 failures
BOTCORE ADAPTER PASS
ALL ITEM-UTILITY OFFLINE TESTS PASSED
[PASS] C01_BuildAll30Profiles                       5 tiers x 6 personas valid
[PASS] C02_SkillOrthogonalAcross3Layers             180 (tier,pa,pb) checks across Combat + Item + Nav
[PASS] C03_InvalidProfileBoundsRejected             tier 0/6 and persona -1/6 rejected fail-closed
[PASS] C04_CoordinateAndYawParity                   yaw(0,-Z)=-0.0 yaw(+X)=-90.0 bot_x=8.59
[PASS] C05_TrueGraphCostBeatsEuclideanTrapAndCaches chosen_id=2 (expect 2, not Euclidean-4m trap 1) t1_probes=2 t2_hits=2 t2_probes=0
[PASS] C06_MalformedWorldFailsClosed                NaN item rejected via ItemReason::kInvalidWorld; finite intent
[PASS] C07_EmptyGraphFallsBackToMaplessScan         mapless-scan
[PASS] C08_DeathAndRespawnStateHygiene              goal, damage-alert & movement reset cleanly across death/respawn
[PASS] C09_Fuzz1000TicksFiniteBoundedAndFireSafe    1000 ticks: max_exp=44/80 pickups=1 finite=1 fire_hygiene=1
[PASS] S01 LowHpReachableMedkit               | goal=101 owner=item-nav pickup_tick=51 hp=22->72
[PASS] S02 EmptyAmmoReachableAmmo             | ammo_starved->goal=201 pickup_tick=30 rockets=0->5
[PASS] S03 WeaponInsteadOfFullHealth          | first_goal=302 (skipped 3.5m Medkit 301=0) acquired_RL=1
[PASS] S04 EnemyContactDuringItemSearch       | pre_nav=1 abort=1 owner=combat(31 ticks) shots=1 sink_idle=1
[PASS] S05 IncomingFireDamageDuringNav        | 5A_dmg_abort=1(under_fire=1) 5B_survival_retreat_ticks=11 healed_hp=66
[PASS] S06 UnreachableIslandItem              | rejected_island=601(unreach=1,t2_reprobes=0) picked_reachable=602(1)
[PASS] S07 ObstacleAndAlternativeRoute        | bypassed_blocked_gate=1(min_x<-7.5) pickup_tick=143 armor=100
[PASS] S08 DynamicStuckAndReplan              | 8A_east_trap=1 replan=1 detour_pickup_t=172 | 8B_stalled_abort=1
[PASS] S09 TwoBotsSameGoalCompetition         | both_init_goal=901(1) winner_901=bot0 bot1_rerouted_902=1 winner_902=bot1
[PASS] S10 PersonalityDependentDecision       | Tier4 Aggressor->1002(Weapon) Survivor->1001(Health) skill_orthogonal=1
[PASS] S11 LargeGraphBudgetCap                | nodes=1024 ticks=400 max_exp=96/96 violations=0 pickups=5
[PASS] S12 DeterministicReplay                | 600t x 4bots hashA=0xd9b0cf1aa2b0b01c == hashB=0xd9b0cf1aa2b0b01c (!= hashC) pickups=8
=== SCENARIO MATRIX SUMMARY: 12 / 12 PASSED (0 failed) ===
[PASS] M01_EightBotContentionAndGraphImmutability | graph_immutable=1 pickups=6==6(exact_conservation) active_collectors=4/8
[PASS] M02_SlotStepOrderIndependence              | A(first==second)=0xcbf29ce484222325 B(first==second)=0xcbf29ce484222325
[PASS] M03_HysteresisPreventsGoalThrashing        | near_equal_goals switches=0 (expect 0) pickups=1
[PASS] compat: C++14, C++17, C++20 clean
[PASS] check-noalloc: 6 headers clean (zero dynamic allocation / STL heap tokens)
ALL CHECKS PASSED
ALL AI CHECKS PASSED
BOT RECONNECT POLICY PASS
COMBAT POLICY PASS (0 failures)
NATIVE WEAPON INPUT PASS (0 failures)
OBSTACLE RECOVERY PASS (0 failures)
HUMAN AI PASS: 555 checks, 0 failures
Completion: 29 checks, 0 failures
C2 regressions: 0 failures
C2 controller: 404 checks, 0 failures
Completion: 29 checks, 0 failures
C2 regressions: 0 failures
C2 controller: 404 checks, 0 failures
sizeof_controller=66320 graph_bytes=173060 static_16_agent_bytes=1061120
bots=1 cpu_ms=162.872 wall_ms=162.985 cpu_us_per_bot_tick=162.872 max_exp=96 allocations=0 digest=da396b67ec2c0ac4 deterministic=1
bots=4 cpu_ms=634.579 wall_ms=634.991 cpu_us_per_bot_tick=158.645 max_exp=96 allocations=0 digest=936e8bcdfbcacf29 deterministic=1
bots=8 cpu_ms=1394.265 wall_ms=1394.953 cpu_us_per_bot_tick=174.283 max_exp=96 allocations=0 digest=2268b1556752a964 deterministic=1
bots=16 cpu_ms=2837.856 wall_ms=2838.919 cpu_us_per_bot_tick=177.366 max_exp=96 allocations=0 digest=05cc36a6828d2e77 deterministic=1
```

ASan+UBSan with leak detection passed completion, regression and controller suites. Compatibility passed C++14/20 for candidate and C++11/14/17 for nav plus C++14/17/20 for bridge. Existing PR69 M02 even-XOR output is excluded as proof; fieldwise controller tests and streaming controller benchmark carry determinism evidence.

C1 cross-build result:
```text
C2 regressions: 0 failures
C2 controller: 404 checks, 0 failures
C1/C2 real headers: escape and travel retain external movement; health item cannot preempt
PASS C1/C2 scratch cross-build; baseline upstream tree unchanged
```

The cross manifest pins combatapplier SHA and source commits/hashes. No files from that candidate were modified. No native/MSVC/Wine tests, install, process signalling, push, merge or deployment were run.
