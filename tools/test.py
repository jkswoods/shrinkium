#!/usr/bin/env python3
"""Run the pure shrinking-rule assertions; no game installation is needed."""
from pathlib import Path
import subprocess
from build import ROOT, java_tool

classes = ROOT / 'build/test'
classes.mkdir(parents=True, exist_ok=True)
subprocess.run([java_tool('javac'), '--release', '25', '-d', str(classes),
                str(ROOT / 'src/main/java/dev/shrinkium/ShrinkRules.java'),
                str(ROOT / 'src/test/java/dev/shrinkium/ShrinkRulesTests.java')], check=True)
subprocess.run([java_tool('java'), '-cp', str(classes), 'dev.shrinkium.ShrinkRulesTests'], check=True)
