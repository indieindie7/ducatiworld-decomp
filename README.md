# Ducati World: Racing Challenge (PlayStation) reverse-engineering notes and symbols

Function names, tools and working notes for **Ducati World: Racing Challenge** (PlayStation, USA, SLUS-01025;
Acclaim / Attention To Detail). The game executable is stored packed inside the disc's `IDXFILES` archive, so the
code was taken from a 2 MB main-RAM snapshot during the attract-mode race (base `0x80000000`, MIPS R3000
little-endian, PsyQ SDK + GCC). Same method as [segarally-decomp](https://github.com/indieindie7/segarally-decomp)
and [manxtt-decomp](https://github.com/indieindie7/manxtt-decomp).
Non-commercial, done for study and preservation. No game data, binaries, RAM dumps or decompiled C are in this
repository, and this is not a matching or rebuildable decompilation.

All 1166 functions found in the snapshot have a name, 0 `FUN_` left; 15 stay marked `provisional` in their comment.

## How it was named

1. **Function discovery** (`ghidra/scripts/SeedMipsFunctions.java`, pre-script): seeds every `jal` target and every
   `addiu sp,sp,-N` prologue above `0x80010000`.
2. **Decider** (`tools/psxrules.py`): BIOS A0/B0/C0 call stubs named from the public psx-spx function tables, empty
   and constant-return bodies, plus hints per function (hardware blocks touched through `0x1f80xxxx`, GTE op count,
   cop0 use). 42 names.
3. **Round 1**: the decompile, with the hints injected (`tools/injecthints.py`), cut into 8 slices (`tools/slice.py`)
   and named by language-model agents (`ghidra/naming/prompt_r1.txt`). 1122 names.
4. **Round 2**: every provisional or suffixed name reviewed again (`ghidra/naming/prompt_r2.txt`): 122 reviewed,
   88 confirmed, 30 renamed, 4 unsure.

Largest groups: `math_` 76, `pad_` 67, `ai_` 62, `car_` 57, `phys_` 52, `cd_` 47, `gpu_` 39, `obj_` 36, `hud_` 36,
`spu_` 34, `race_` 31, `cam_` 30. The bike is called "car" in the game's code.

## Bike physics in short

A bike is a rigid body with two wheel records and a set of collision spheres. Each frame `car_UpdatePhysicsAll`
(`0x800309d0`) runs wheel ground contacts, suspension springs, steering, engine and tyre forces, air drag and
surface-dependent rolling resistance. Collision sweeps the spheres against nearby track polygons (plane, edge and
vertex tests) and other bodies, queues the hits by time of impact and resolves them in order with wall and
body-body impulses. Addresses are in `NOTES.md`, "Bike physics map".

## What is here

| Path | Content |
|---|---|
| `NOTES.md` | the working log: disc layout, emulator setup, RAM snapshots, naming rounds, physics map |
| `ghidra/hand_0.txt` | the names: `0x<addr> func <name> hand <comment>` |
| `ghidra/naming/` | the naming and review prompts |
| `ghidra/scripts/SeedMipsFunctions.java` | function seeding for a raw PSX RAM image |
| `ghidra/dwrun.sh` | headless runner (set `GHIDRA_HEADLESS` and `DW_GHIDRA`) |
| `tools/psxrules.py`, `injecthints.py`, `slice.py` | decider and slicing for the naming rounds |
| `tools/idxlist.py` | lists / extracts the `IDXFILES.IDX` + `IDXFILES.IMG` archive entries |
| `tools/dump.lua`, `raw2png.py` | PCSX-Redux script saving screenshots + RAM snapshots, and a screenshot converter |

## Use

Bring your own disc. Run it in PCSX-Redux with `tools/dump.lua` to save RAM snapshots, import one (the names were
made on the snapshot at 4500 vsyncs) into Ghidra as raw `MIPS:LE:32:default` at `0x80000000` with
`SeedMipsFunctions.java` as pre-script, then run `ApplyNames.java ghidra/hand_0.txt` (the name importer from
[scorcher-decomp](https://github.com/indieindie7/scorcher-decomp)).

## License

The notes, names and tools are released under the license in `LICENSE`. Ducati is a trademark of Ducati Motor
Holding; Ducati World is a trademark of its respective owners. This project is not affiliated with or endorsed by
them.
