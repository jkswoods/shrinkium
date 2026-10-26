"""Make DocMD's mobile navigation toggle a keyboard-accessible native button."""
from pathlib import Path
import re

pattern = re.compile(r'<span class="mobile-view sidebar-menu-button float-right">(.*?)</span>', re.S)
changed = 0
for page in Path('site').rglob('*.html'):
    source = page.read_text()
    result, count = pattern.subn(
        r'<button type="button" aria-label="Toggle navigation" class="mobile-view sidebar-menu-button float-right">\1</button>', source)
    if count:
        page.write_text(result)
        changed += count
assert changed >= 9, 'DocMD mobile menu markup changed; inspect the generated navigation.'
print(f'Added keyboard-accessible mobile menu buttons to {changed} pages.')
