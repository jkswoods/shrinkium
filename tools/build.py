#!/usr/bin/env python3
"""Build with a legally obtained, hash-verified Hytale SDK and JDK 25."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()

def java_tool(name):
    home = os.environ.get('JAVA_HOME')
    candidate = str(Path(home) / 'bin' / name) if home else shutil.which(name)
    if not candidate:
        raise SystemExit('Install JDK 25 and set JAVA_HOME or add its bin directory to PATH.')
    return candidate

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', default=os.environ.get('HYTALE_SERVER_JAR'))
    args = parser.parse_args()
    if not args.server:
        parser.error('Supply --server or HYTALE_SERVER_JAR; the proprietary SDK is not distributed here.')
    config = json.loads((ROOT / 'release.json').read_text())
    server = Path(args.server)
    if sha(server) != config['sdkSha256']:
        raise SystemExit('SDK checksum differs from release.json. Use the pinned SDK; do not change compatibility to bypass this check.')
    manifest = {
        'Group': 'Shrinkium', 'Name': 'Shrinkium', 'Version': config['version'],
        'ServerVersion': config['serverVersion'],
        'Description': 'Private crystal-powered shrinking ray prototype; native acceptance pending.',
        'Main': 'dev.shrinkium.ShrinkiumPlugin', 'IncludesAssetPack': True,
    }
    resources = ROOT / 'src/main/resources'
    (resources / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    classes = ROOT / 'build/classes'
    shutil.rmtree(classes, ignore_errors=True)
    classes.mkdir(parents=True)
    sources = sorted((ROOT / 'src/main/java').rglob('*.java'))
    subprocess.run([java_tool('javac'), '--release', '25', '-cp', str(server), '-d', str(classes), *map(str, sources)], check=True)
    output = ROOT / 'build/libs' / f'Shrinkium-hytale{config["hytaleFamily"]}-{config["version"]}.jar'
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in [classes, resources]:
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    info = zipfile.ZipInfo(path.relative_to(folder).as_posix(), (2026, 10, 26, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, path.read_bytes())
    report = {'artifact': str(output.relative_to(ROOT)), 'sha256': sha(output),
              'declaredCompatibility': config['serverVersion'], 'buildSdk': config['sdkVersion'],
              'sdkSha256': config['sdkSha256']}
    (ROOT / 'build/build.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
