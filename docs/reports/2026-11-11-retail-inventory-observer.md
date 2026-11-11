# Passive four-player inventory observer for the public baseline

The new `tools/retail_inventory_readonly.py` observes four explicitly selected
**global** player slots through the original Retail 1.07 session player table.
It does not depend on Cecil telemetry, HumanAI, SupplyNavigation or ArenaTier.
It therefore closes the source-level observation gap for the old public `7fc94a…`
DLL without changing that client's behavior. Native runtime acceptance is **open**.
No native process was launched or read during this implementation task.

## Verified layout and provenance

Static counterchecks used original files in the private fixture
`/srv/tse-cecil-gate8-20261109/server/Bin/`:

| Image | SHA256 | Preferred base |
|---|---|---|
| Engine.dll | `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f` | `0x600c0000` |
| EntitiesMP.dll | `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350` | `0x60310000` |

Exports were resolved from each PE export table; instructions were disassembled
with `objdump -d -Mintel --start-address=... --stop-address=... IMAGE`.
The eight relocation-free fingerprints in the tool were separately checked
against PE section file offsets. That check initially caught two RVA arithmetic
errors (GetGameTime and WeaponSelectOk); the final eight checks all match.
Synthetic tests alone would not have established those addresses.

| Observation | Original instruction/function evidence | Offset |
|---|---|---|
| Network pointer and player table | Engine `GetPlayerEntity`, VA `0x601b9d70`: global `0x602cd6a4`, network+20, session+4, stride136, active+0/entity+4 | Engine RVA `0x20d6a4` |
| Game tick | Engine `GetGameTime`, VA `0x6019c8d0`, `8b4120d9404cc3` | session+`0x4c` |
| Health | Engine `GetHealth`, VA `0x600d7020` | entity+`0xcc` |
| World | Engine `GetWorld`, VA `0x600d6e10` | entity+`0x8c` |
| Player weapons pointer | Entities `GetPlayerWeapons`, VA `0x603f6b90` | player+`0x384` |
| Armor | Entities `InflictDamage`, VA `0x603fd52a` subtracts armor, `0x603fd536` stores it | player+`0x370` |
| Spawn clock | Same original damage function, VA `0x603fd46c` subtracts spawn time | player+`0xc14` |
| Owned weapons | `ReceiveWeapon`, VA `0x6041b1de` reads and `0x6041b1f3` stores ORed pickup bit; `WeaponSelectOk` VA `0x6041c5d4` tests it | weapons+`0x104` |
| Current/wanted/change | `WeaponSelectOk`, VA `0x6041c5e8`, `0x6041c5f0`, `0x6041c5f6` | weapons+`0xf8`, `0xfc`, `0x108` |
| Weapon owner and auxiliary flags | `SetDefaultProperties`, VA `0x60414e42` onward, compared with Engine107 generated member order | owner+`0xec`, fire+`0xf0`, ammo+`0xf4`, previous+`0x100`, reload+`0x10c`, mirror+`0x110`, animation+`0x114` |
| AI state stack | Engine `CRationalEntity::Call`, VA `0x601c3037`, `0x601c3040`, `0x601c3080`; push writes at `0x601c3128` | capacity+`0xdc`, pointer+`0xe0`, used+`0xe4` |

SDK context is specifically
`/srv/tse-sdk-20261021/Sources/Includes/Engine107/EntitiesV/Player.h:67`,
`PlayerWeapons.h:93`, and `Engine107/Engine/Entities/Entity.h:165,742`,
with common `StaticArray.h:29` / `StaticStackArray.h:29` layout definitions.
Player default initialization at original VA `0x603f5f57` onward agrees with
name+368, last-buttons+36c, armor+370, weapons+384. The existing SDK107 layout
probe also reported health204, placement32, spawned3092, armor880, entityid28.
This is a targeted original-1.07 countercheck, not a claim of general SDK/1.10 ABI
equivalence.

## Guards and output limits

The reader accepts only the existing private arena's `botA`, `botB`, `server`
or `vanilla` child directories. Caller must supply the recorded PID **and Linux
start ticks**, exact CWD, and expected GameMP SHA256. Engine and Entities hashes
are fixed. Module inode, device and base, file identity and process identity/CWD
are checked before and after sampling. Files are hashed at initialization;
subsequent calls check inode/size/mtime/ctime. Loaded instruction fingerprints
are checked each sample. `/proc/PID/mem` is opened with `O_RDONLY`; no target
calls, input, hooks, pause, signals, process creation or writes exist in this tool.

Each sample reads only four caller-selected slots, bounded player/weapon fields,
and at most16 stack entries per player. It validates owner backreference,
matching world, deletion flags, enum/mask bounds, finite floats and stack bounds.
Null/missing players or weapons remain explicit; previous inventories are never
reused. A complete second read must match every observed byte, including tick,
entity/life identity, ownership and stack. A final tick read and process guard
must also pass. Changed/invalid observations fail with nonzero CLI exit status;
there is no automatic retry that silently hides missing samples.

Output provides health, armor, placement, spawn clock, last buttons, inventory,
current/wanted/previous weapon, fire request, ammo flag, change/reload/mirror flags,
animation and raw weapon AI stack. `useful_owned = owned & 0x3df8` matches this
milestone's acquisition metric; it excludes Knife, both Colts and Chainsaw.
Fire requests and firing states **are not hit attribution or proof of damage**.
Do not interpret every nonzero inventory as an acquired useful ranged weapon.

Two matching read passes are **not atomic**, cannot rule out an ABA transition,
and cannot guarantee observing every game tick. Returned `elapsed_seconds` and
`bytes_read` allow actual probe cost to be measured; initialization hashing is
outside per-sample timing. Runtime cadence, rejected-sample frequency and impact
on the comparison need an uninstrumented control. Native use should retain one
reader per process instead of rehashing images for every frame.

Global slots are not local-player indices. Establish the mapping from the exact
trial's `[BotDriver] local player N (player index M)` join records, and retain it
with the evidence. The original server's player table is preferable for
authoritative cohort observations. On a client this samples the original session
player entity, not a separately selected local prediction entity.

Example, with values from the harness's captured launch identity and join log:

```python
from retail_inventory_readonly import InventoryReader
with InventoryReader(pid, start_ticks, fixture_role_root, expected_game_sha) as reader:
    record = reader.sample(tuple(global_slots_for_the_four_old_players))
```

The one-shot CLI accepts `--pid`, `--start-ticks`, `--root`, `--game-sha256`,
and `--slots 0,1,2,3` (replace indices with actual evidence). It prints JSON.
No fixture values or player names are assumed by the example.

## Old public first-spawn timing

The pinned public source is
`/srv/tse-integrated-build-20261021-04/Sources/Game/BotDriver.cpp`:

- Lines795–800 derive period/fire ticks from configured period and TickQuantum.
- Lines824–839 reset each source's tick to0, then increment it.
- Lines1123–1125 compute `(tick + local * periodTicks / 4) % periodTicks`.
- Lines1129–1136 distinguish the HumanAI respawn override from the legacy pulse.
- Lines845–852 and1078–1082 show that AutoCombat0, TestTarget-1, Move0 and Yaw0
  provide a neutral action path; HumanAI may remain0 throughout old-client use.

At the actual standard .05-second tick and one-second period, four local phases
are offset0/5/10/15 ticks. Pause alone cannot remove that within-client stagger.
For an isolated **pretrial bootstrap**, a supported normal shell configuration
with period .05 and FireTicks1 makes periodTicks1 and removes the local phase
offset. Both cohorts can use the same neutral bootstrap, then normal Pause and
normal shell commands can restore exact intended combat policies before a common
release. This does not require HumanAI1 on the old client or memory writes.

This is a proposed discriminating protocol, **not a passed matched-start gate**.
An always-on bootstrap fire pulse can become a shot after spawn; a delayed pause
can permit simulation, item contact or damage. Require actual all-eight spawn
clocks, positions, health/armor, inventories, no pretrial damage/acquisition and
restored policy receipts before accepting any leg. If those conditions cannot be
met through the ordinary input path, keep the stagger explicit instead of calling
the starts equal. Temporary bootstrap changes must not extend into scoring.

## Verification

`python3 -m unittest discover -s tools` passes207 tests, including15 focused new
tests. The focused sequence included the missing-module RED, then three actual
semantic failures where same-tick ownership/spawn changes and tick changes were
incorrectly accepted; the second-read implementation makes those pass.
Filesystem-backed synthetic `/proc` tests exercise read-only file descriptors,
four independent inventories, PID reuse, wrong CWD, changed mapping/file/code,
mid-sample identity change and closure. They do not emulate the engine.

Original image hashes and all eight fingerprint bytes passed independent static
PE-section counterchecks. Runtime reading, overhead, prolonged sync stability,
the proposed legacy bootstrap and equal physical starts remain untested here.
