---
title: Troubleshooting
---

# Common questions

## The ray disappears after restoring

Change to another hotbar slot, then select the ray again. This recovers the held
model in the observed free-restoration case. It is a known camera/held-item defect,
not a missing item or a reason to craft a second ray.

## A shot does nothing

Carry crystals in your hotbar or main inventory. Select a size, close the panel and
aim at a visible living target within 16 blocks. A wall, unloaded terrain, invalid
target, active transition or same-size no-op can refuse the action. Those cases
should not consume a crystal. SELF is an explicit panel action.

## I cannot return to normal size

Move into open space and try again. Use **/shrinkium restore** for free self recovery;
it does not need a ray or crystals. A checked pre-shrink anchor is used only when
safe and loaded in the same world. See [safe restoration](restoration.md).

## I cannot find crystal ore

Try newly generated default-world stone caves. Existing explored caves are not
rewritten. Deposits are not guaranteed in every cave. The full ordinary discovery
and mining route still needs native playtesting.

## There is a pause while exploring new terrain

The cave decoration hook has shown initial generation pauses. Performance acceptance
is unfinished. Use a test world and include whether terrain was newly generated
when reporting a slowdown; do not assume a first-generation pause measures steady
server performance.

## Can I shrink blocks or grow beyond my original size?

No. The ray affects supported living entities at 75/50/25% or their original baseline.
It does not resize terrain, structures or blocks.

## Reporting a problem

Use [GitHub issues](https://github.com/jkswoods/shrinkium/issues). Include your Hytale
patch, chosen file version, singleplayer/server context, steps and expected/actual
behavior. For growth problems, describe the surrounding clearance. Remove account
details, addresses and unrelated private data from screenshots and logs before sharing.
