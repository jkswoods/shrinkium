---
title: Installation
---

# Install in a backed-up test world

Choose a file from the [repository's file listing](https://github.com/jkswoods/shrinkium/releases)
whose requirements include your exact Hytale patch. The source branch and guide do
not promise that a downloadable release is already available.

1. Back up the world and player data, then stop the game or server normally.
2. Put the chosen compatible mod JAR in the Hytale **UserData/Mods** directory used
   by that installation. Remove an older Shrinkium JAR first so only one copy loads.
3. Start a separate test world and enable Shrinkium in its mod selection. For a hosted
   test server, install it through that server's normal mod-loading setup.
4. Load the world and check the [first-session guide](getting-started.md).

No extra runtime library mod is required. Asset authoring tools and the build SDK
are only needed when building from source.

## Updating or removing

Keep a backup before changing the installed file. Restore affected players and
animals to their original sizes before removing Shrinkium. The emergency command
restores only the player who uses it; animals require the ray's restoration mode.
Do not assume removing the JAR restores saved scale automatically.

Stop normally before replacing or removing a mod. Keep the backup and matching old
file until you have checked the updated world. Newly generated caves can receive
deposits; installing an update does not rewrite already generated caves.

## Build from source

The [hytale0.7 source branch](https://github.com/jkswoods/shrinkium/tree/hytale0.7)
contains portable build instructions. It requires JDK 25, Python and a legally obtained
SDK matching the separately recorded checksum. Outputs and their exact filenames are
reported in build/libs and build/build.json. The proprietary SDK is not in Git.
