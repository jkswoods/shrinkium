---
title: Shrinkium for Hytale 0.7
---

::: hero
# A smaller point of view
Carry a crystal-powered ray, choose a size and explore familiar spaces at a different scale.
::: button title:"Start here" url:"installation" icon:download
::: /hero

![Shrink Ray held in the world](/assets/hytale0.7/screenshots/ray-and-ore.png)

*Native Hytale 0.7.4. The brass cage, violet crystal reactor and walnut grip are the
current in-game ray model.*

The Shrink Ray can set a living target to **75%, 50% or 25%** of its captured original
size. Primary fires at one visible target; Secondary opens the controls, including an
explicit **SELF** button. Each successful ray change costs one Shrinkium Crystal.
Misses, walls and no-ops consume none.

The implemented starting loop is cave crystal → Workbench recipe → shrinking → safe
restoration. See [first steps](getting-started.md) for the full route and its current
playtest limits, [recipes](recipes.md) for quantities, and [safe restoration](restoration.md)
before trying a narrow passage.

::: callout type:warning title:"Before you play"
Keep world and player backups. The ray and corrected ore have been playtested in
single-player. The full ordinary survival acquisition route and real second-client
behavior remain unverified.
After free restoration the ray may be hidden; change hotbar slots and select it again.
::: /callout

The declared range is **>=0.7.4 <0.8.0**. Native observations cover **0.7.4**; a range
is not evidence that every future patch works. [Compatibility details](compatibility.md)
explain how to choose a file and which checks are still open.
