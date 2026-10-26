from pathlib import Path
import argparse,json,zipfile,hashlib,subprocess,re,os,shutil
parser=argparse.ArgumentParser();parser.add_argument('--assets',default=os.environ.get('HYTALE_ASSETS_ZIP'));args=parser.parse_args();
if not args.assets:parser.error('Supply --assets or HYTALE_ASSETS_ZIP')
R=Path(__file__).resolve().parents[1];res=R/'src/main/resources';stock=set(zipfile.ZipFile(args.assets).namelist());ours={str(p.relative_to(res)) for p in res.rglob('*') if p.is_file()};checks=0
keys={'Icon','Model','Texture','All','CustomModel','TexturePath'}
def exists(v):return 'Common/'+v in ours or 'Common/'+v in stock
for path in res.rglob('*.json'):
 o=json.loads(path.read_text())
 def walk(n):
  global checks
  if isinstance(n,dict):
   for k,v in n.items():
    if k in keys and isinstance(v,str) and v.endswith(('.png','.blockymodel')):assert exists(v),(path,k,v);checks+=1
    if k=='Files':
     for f in v:assert exists(f),(path,f);checks+=1
    walk(v)
  elif isinstance(n,list):
   for v in n:walk(v)
 walk(o)
for p in res.rglob('*.blockymodel'):
 o=json.loads(p.read_text());atlas=res/'Common/Items/Shrinkium/Atlas.png'
 def nodes(tree):
  for n in tree:
   yield n
   yield from nodes(n.get('children',[]))
 for n in nodes(o['nodes']):
  assert n['shape']['visible']
  for face in n['shape']['textureLayout'].values():assert 0<=face['offset']['x']<=224 and 0<=face['offset']['y']<=224;checks+=1
for p in (res/'Common/Sounds/Shrinkium').glob('*.ogg'):
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))['streams'][0];assert meta['codec_name']=='vorbis' and meta['sample_rate']=='44100';assert meta['channels']==(2 if p.stem=='handlingcue' else 1);checks+=1
for p in (res/'Common/UI/Custom').rglob('*.ui'):
 text=p.read_text()
 assert all(c in ['\\','"'] for c in re.findall(r'\\(.)',text)),('Unsupported native UI string escape',p)
 for ref in re.findall(r'TexturePath: "([^"]+)"',text):
  assert (p.parent/ref).exists() or (res/'Common/UI/Custom'/ref).exists(),('Missing native UI texture',p,ref)
  checks+=1
 checks+=1
b=json.loads((R/'build/build.json').read_text());z=zipfile.ZipFile(R/b['artifact']);manifest=json.loads(z.read('manifest.json'));assert manifest['ServerVersion']=='>=0.7.4 <0.8.0';assert not any('Probe' in n or n.startswith(('project/','audio/','art/')) for n in z.namelist());checks+=2
record={'checks':checks,'package_sha256':hashlib.sha256((R/b['artifact']).read_bytes()).hexdigest(),'scope':'Packaged references/UV bounds/audio channels/range metadata; native rendering and listening pending'};print(json.dumps(record,indent=2))
