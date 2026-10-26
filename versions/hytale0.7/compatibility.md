---
title: Compatibility
---

# Match the file to your game patch

The Hytale 0.7 support branch declares **>=0.7.4 <0.8.0** in its manifest. The exact
compilation SDK/hash are separately recorded in the source build metadata. The
manifest range is not an exact SDK pin, and neither the range nor this guide proves
compatibility with every future patch. Native observations currently cover **0.7.4**.

Choose a file from the [release listing](https://github.com/jkswoods/shrinkium/releases)
whose declared requirements include your game patch. Check that file's release notes
for its included behavior. This living guide follows the **hytale0.7** source branch
independently of mod releases; a branch feature may precede a downloadable file.

## Current support status

Shrinking, charge rules, aimed animal targeting, normal miniature reload, obstructed
growth and emergency self recovery have native observations. The latest ray model's
mount, first-person framing and inventory/hotbar icon have also been checked.

The corrected ore deposits cover all six faces, and their native surfaces and
inventory/hotbar icon have been checked. Single-player playtesting is complete for
the observed ray loop. The full ordinary survival acquisition route, complete
skin/camera behavior, beam/listening coverage and real second-client behavior remain
unverified; the Release channel does not establish those additional checks.

## Settings and other mods

The current implementation uses fixed 75/50/25% choices, 16-block targeting and one
crystal per successful change. Size choice is player state. There is no documented
player configuration file for changing these rules. The server owns the scale and
charge decisions; real multi-user operation still needs testing.

Foreign scale effects and unsupported baselines are refused. Other mods that change
camera, model scale, collision or player appearance may interact with Shrinkium.
Back up saves and test combinations separately.

[Return to the Hytale version chooser](../)
