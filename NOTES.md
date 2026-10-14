# Ducati World: Racing Challenge (PSX, Acclaim / ATD) — notes

Rules: same as the other decomps (names + notes only, no game data / BIOS in any repo, never download a BIOS).

## Layout
- `trace\` — emulator scripts and outputs.

## Emulator: PCSX-Redux
- Runs with its built-in HLE BIOS (no BIOS file needed).
- Hidden run (from trace\, never steals focus):
  `py -3.13 -I Tools\mednafen\bgrun.py 75 'Tools\pcsx-redux\pcsx-redux.exe' -no-ui -portable -iso '<cue>' -dofile 'DucatiWorld\trace\shot.lua' -run`
- `-portable` writes memcards + settings next to the cwd (trace\).

## Boot check (10-13, DONE)
- `trace\shot.lua`: GPU::Vsync listener, every 600 vsyncs `PCSX.GPU.takeScreenShot()` -> `shot<n>.raw`, quits at 1800.
- Raw format: first line `<w> <h> cdata<enum 722>: <bpp>` (bpp enum 0 = BPP_16, 1 = BPP_24), then pixels. 16 bpp is PSX 5:5:5 with red in the low bits = ffmpeg `bgr555le`.
- `trace\raw2png.py <in.raw> <out.png>` converts.
- Result: shot600 640x478 black, shot1200 512x228 Acclaim logo, shot1800 512x228 ATD logo -> `trace\boot_check.png`. The game boots.

## Disc layout (10-13)
- Extract: `py -3.13 -I ..\Scorcher\tools\isoextract.py "<Track 01>.bin" psx\cd 2352 24` (4th arg = 24-byte MODE2 form 1 header; added to isoextract.py 10-13).
- psx\cd: SYSTEM.CNF (BOOT = cdrom:\SLUS_010.25;1, STACK 801FFFF0), SLUS_010.25 = 45,056-byte boot loader (PS-X EXE, pc 0x80020ae8, load 0x8001c000, text 0xa800), IDX\IDXFILES.IDX (7200 bytes) + IDX\IDXFILES.IMG (28,993,536 bytes).
- IDXFILES.IDX = 450 x 16-byte records {u32 offset, u32 stored size, u32 unpacked size, u32 flags}, no names. flags 3 = packed, magic "GT20" (364 entries); also flags 0/4/5/7/16xx.
- `tools\idxlist.py <IDX> <IMG> [outdir]` lists / dumps entries; listing in psx\idxlist.txt.
- Plan: take the game code from RAM dumps (trace\dump.lua: screenshot + 2 MB RAM every 900 vsyncs) rather than decoding GT20 first; GT20 unpacker = in the loader / game code.

## RAM dumps + Ghidra (10-14)
- dump.lua run (150 s hidden): ram900..ram5400.bin + shots. 900 = Loading screen, 2700/3600/4500/5400 = attract demo race (trace\dump_shots.png).
- ghidra\dwram.bin = copy of ram4500.bin (2,097,152 bytes); 727 `addiu sp,sp,-N` prologues.
- ghidra\dwrun.sh = headless wrapper (copied from SegaRally srrun.sh), project ghidra\DucatiWorld.gpr.
- Import DONE 10-14 (SeedMipsFunctions: 2908 jal refs, 686 prologues, 1121 functions seeded; a few pcode errors at 801c0158 / 801d1d30 = delay slots past data). Import: `bash dwrun.sh '<log>' -import '<dwram.bin>' -loader BinaryLoader -loader-baseAddr 0x80000000 -processor MIPS:LE:32:default -preScript SeedMipsFunctions.java` (seeds jal targets + prologues above 0x80010000).
- funcinfo (10-14): `SP='Amok\ghidra\scripts' bash dwrun.sh '<log>' -process dwram.bin -noanalysis -readOnly -postScript ExportFuncInfo.java '<ghidra\funcinfo_0.tsv>'` -> 1166 functions, 2859 calls, 354 string refs.

- Decider (10-14): tools/psxrules.py <ram> <funcinfo> <names> <hints> -> ghidra/rules_0.txt 42 names (36 BIOS A0/B0/C0 call stubs named from psx-spx tables, stub_/retN_) + ghidra/hints_0.txt 222 (hw blocks via lui 0x1f80, gte count, cop0, strings). hand_0.txt = rules_0; ApplyNames 42; CsDumpAll -> ghidra/decomp_0.c (1166 fn).
- Round 1 (10-14): tools/injecthints.py (fixed for 2-field hints) -> naming/decomp_hint.c (222 hints); tools/slice.py 8 -> naming/s1..s8.c (128/122/128/92/102/147/148/255 fn = 1122); naming/prompt_r1.txt; 8 Sonnet agents -> naming/h1..h8.txt (128/122/128/92/102/147/148/255 lines, 0 bad).
- Round 1 merged (10-14): ghidra/hand_0.txt 1166 lines (42 rules + 1122 Sonnet + 2 by hand: 0x8003253c obj_RunPathScript_case5 = Ghidra switch split, 0x80075044 memcmp_Thunk), 77 provisional, 2 duplicate names given _2. Backups naming/hand_0_dec.bak, naming/hand_0_r1.bak. ApplyNames 1166 -> funcinfo_0.tsv 1166 fn, 0 FUN_; dump ghidra/decomp_1.c. Top prefixes: math 76, pad 67, ai 62, car 57, phys 52, data 51, cd 47, gpu 37, hud 36, obj 35, spu 34, race 31, cam 30.

- Round 2 (10-14): naming/prov_list.txt 122 (77 provisional + _N/stub suffix names) -> naming/r2_1.c, r2_2.c (61+61 fn from decomp_1.c), naming/prompt_r2.txt -> 2 Sonnet agents -> naming/v2_1.txt, v2_2.txt: 122 verdicts, CONFIRM 88, RENAME 30, UNSURE 4. Applied -> hand_0.txt (backup naming/hand_0_r2.bak), 15 lines still say provisional; ApplyNames 1166, funcinfo_0.tsv 0 FUN_, dump ghidra/decomp_2.c. Verdict line: 0x<addr> <old> CONFIRM|RENAME|UNSURE <new> <reason>.
## Bike physics map (round 1 names, 10-14; check before relying)
- Per frame: car_UpdatePhysicsAll 0x800309d0 (matrix, car_ComputeSteeringAxes, car_UpdateAllWheelContacts 0x8002dd74, car_ApplySuspensionForces 0x8002e910, car_UpdateSteering 0x8002d478, car_UpdateWheelForces 0x8002ad7c) -> car_ApplyWheelFrictionAll 0x80031470 / car_ApplyWheelFriction 0x8003164c, car_ApplyAirDrag 0x800310b0, car_ApplyWheelRollingResistance 0x80031118 (surface type switch), car_SleepWhenSlow 0x80030e0c, car_UpdateCrashState 0x8003138c.
- Bike = rigid body with TWO wheel records (stride 0x90) + a set of collision spheres (pool slots stride 0x44, phys_AttachCollisionSpheres 0x80023cb0). Differs from Scorcher (one swept sphere) and Manx TT (point + octagon).
- Collision: phys_BuildCollisionCandidates 0x8002420c -> phys_GatherNearbyTrackPolys 0x800245cc (surface patch grid), swept sphere vs plane/edge/vertex (phys_SpherePlaneTest 0x80024f88 packed 10-bit normals, phys_SweepSphereVsEdge 0x8002604c, phys_RaySphereIntersect 0x800259cc), body pairs phys_CollideBodyPair 0x800268c4. Time-of-impact event queue: phys_QueueCollisionEvent 0x80028508 / phys_PopCollisionEvent 0x800286a0 (heap at 0x80096a78), phys_ResolveCollisionEvent 0x80027b5c -> phys_ApplyWallImpulse 0x80028d38 / phys_ApplyBodyBodyImpulse 0x80028f44.
- Setup: car_Create 0x8002c244 (physics source module, per-bike stats), car_InitPhysicsBody 0x8002f204 (mass, inertia), car_SetupSuspensionTables 0x8002e860; input car_ReadControlsFromPad 0x8005fc48, car_AutoShiftGear 0x8005b990.

## Next
- Lua exec tracer: function-entry hits (PCSX.addBreakpoint Exec) + RAM read/write per function, attract mode / race.
- Export funcinfo (strings + calls per function), find the PsyQ runtime (libgpu/libgte/libcd/libspu) by hardware addresses 0x1f80xxxx and GTE cop2 ops, then the decider + Sonnet naming rounds as in Sega Rally.
- Find the bike physics (Scorcher reference: Scorcher/pcwin/HANDOFF-consoles.md).
