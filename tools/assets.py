#!/usr/bin/env python3
"""Original Shrinkium geometry, painted atlases, texture-mapped previews and native assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,random,zipfile,os,numpy as np
R=Path(__file__).resolve().parents[1];A=R/'src/main/resources';P=R/'art/previews';S=R/'art/source';P.mkdir(parents=True,exist_ok=True)
def write(path,value):
 p=A/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def png(path,image):p=A/path;p.parent.mkdir(parents=True,exist_ok=True);image.save(p)
# Broad painted light/shadow facets and chipped metal edges at native texel density.
colours={'brass':(156,111,45),'plum':(65,40,63),'wood':(96,56,33),'crystal':(139,77,193),'aperture':(199,140,239),'steel':(53,62,71)}
atlas=Image.new('RGBA',(256,256));draw=ImageDraw.Draw(atlas);tiles={}
for i,(name,c) in enumerate(colours.items()):
 x=(i%4)*64;y=(i//4)*64;tiles[name]=(x,y);rng=random.Random(i+546)
 def col(k):return tuple(max(0,min(255,round(v*k))) for v in c)+(255,)
 draw.rectangle((x,y,x+63,y+63),fill=col(.9))
 draw.polygon([(x,y),(x+63,y),(x+50,y+22),(x+13,y+43),(x,y+30)],fill=col(1.22))
 draw.polygon([(x+13,y+43),(x+50,y+22),(x+63,y+14),(x+63,y+63),(x+23,y+63)],fill=col(.72))
 draw.polygon([(x+4,y+6),(x+25,y+3),(x+39,y+15),(x+20,y+25),(x+1,y+20)],fill=col(1.42 if name=='crystal' else 1.1))
 for j in range(11):
  u=rng.randrange(0,60);v=rng.randrange(0,60);draw.line([(x+u,y+v),(x+min(63,u+rng.randrange(2,9)),y+v-1)],fill=col(1.58 if j%3==0 else .8),width=1)
 draw.line((x,y,x+63,y),fill=col(1.5),width=2);draw.line((x,y,x,y+63),fill=col(1.32),width=1)
 if name=='crystal':
  draw.polygon([(x+10,y),(x+23,y+16),(x+12,y+30),(x+35,y+43),(x+28,y+63),(x+32,y+42),(x+9,y+30),(x+20,y+16)],fill=col(1.65))
 # Paint the complete 32x32 UV region actually used by each exported face.
 draw.rectangle((x,y,x+31,y+31),fill=col(.95))
 draw.polygon([(x,y),(x+31,y),(x+26,y+9),(x+12,y+14),(x,y+8)],fill=col(1.36))
 draw.polygon([(x,y+8),(x+12,y+14),(x+21,y+30),(x,y+31)],fill=col(.86))
 draw.polygon([(x+26,y+9),(x+31,y),(x+31,y+31),(x+21,y+30),(x+12,y+14)],fill=col(.66))
 draw.line([(x,y),(x+31,y)],fill=col(1.65),width=1)
 if name=='crystal':
  draw.polygon([(x+4,y+3),(x+20,y+1),(x+12,y+14)],fill=col(1.65))
  draw.polygon([(x+12,y+14),(x+26,y+9),(x+23,y+24),(x+20,y+17)],fill=col(1.15))
  draw.line([(x+3,y+26),(x+10,y+19),(x+12,y+14),(x+17,y+8)],fill=col(1.85),width=1)
 else:
  draw.line([(x+2,y+5),(x+6,y+3),(x+15,y+3)],fill=col(1.4),width=1)
  draw.line([(x+25,y+25),(x+29,y+21)],fill=col(.46),width=2)
  if name=='wood':
   draw.line([(x+5,y+8),(x+9,y+14),(x+8,y+27)],fill=col(.6),width=1)
   draw.line([(x+22,y+2),(x+18,y+12)],fill=col(1.25),width=1)
 png(Path('Common/Items/Shrinkium/Atlas.png'),atlas)
# Node sizes intentionally use meaningful painted regions through texture stretch.
def quat(rx,ry,rz):
 x,y,z=[math.radians(t)/2 for t in (rx,ry,rz)];sx,cx=math.sin(x),math.cos(x);sy,cy=math.sin(y),math.cos(y);sz,cz=math.sin(z),math.cos(z)
 return {'x':sx*cy*cz-cx*sy*sz,'y':cx*sy*cz+sx*cy*sz,'z':cx*cy*sz-sx*sy*cz,'w':cx*cy*cz+sx*sy*sz}
def node(name,pos,size,mat,rot=(0,0,0)):
 # settings size spans 32px UV tiles; stretch sets geometry dimensions, preserving full painted facets.
 x,y=tiles[mat];return {'id':name,'name':name,'position':dict(zip('xyz',pos)),'orientation':quat(*rot),'shape':{'type':'box','offset':{'x':0,'y':0,'z':0},'stretch':dict(zip('xyz',[v/32 for v in size])),'settings':{'size':{'x':32,'y':32,'z':32}},'textureLayout':{f:{'offset':{'x':x,'y':y},'mirror':{'x':False,'y':False},'angle':0} for f in ['front','back','left','right','top','bottom']},'unwrapMode':'custom','visible':True,'doubleSided':False,'shadingMode':'standard'}}
crystal=[node('shard',(0,8,0),(10,19,9),'crystal',(10,25,-13)),node('tip',(-1,18,0),(6,8,6),'crystal',(10,25,-30)),node('fracture',(4,5,1),(5,10,5),'aperture',(18,-20,15))]
ore=[node('outcrop-top',(-6,32,1),(12,15,11),'crystal',(14,25,-15)),node('outcrop-front',(7,19,-15),(12,13,11),'crystal',(35,10,-15)),node('outcrop-left',(-15,9,4),(12,14,10),'crystal',(12,30,-25))]
# Rotate each existing deposit around the stone cube's centre to cover its opposite face.
# Left-multiply the half-turn so both placement and local crystal orientation rotate together.
from copy import deepcopy
for original,name,axis in [(ore[0],'outcrop-bottom','x'),(ore[1],'outcrop-back','y'),(ore[2],'outcrop-right','y')]:
 opposite=deepcopy(original);opposite['id']=opposite['name']=name;p=opposite['position'];q=opposite['orientation'];x,y,z,w=[q[k] for k in 'xyzw']
 if axis=='x':
  p['y'],p['z']=32-p['y'],-p['z'];values=(w,-z,y,-x)
 else:
  p['x'],p['z']=-p['x'],-p['z'];values=(z,w,-x,-y)
 opposite['orientation']=dict(zip('xyzw',values));ore.append(opposite)
# Render actual exported face UV regions, not a separate artist's illustration.
def rotation(q):
 x,y,z,w=[q[k] for k in 'xyzw'];return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def render(nodes,tex,size=384):
 camera=np.array([1.15,.8,-1.5]);camera/=np.linalg.norm(camera);right=np.cross(camera,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,camera);polys=[]
 face={'front':([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1]],[0,0,-1]),'back':([[1,-1,1],[-1,-1,1],[-1,1,1],[1,1,1]],[0,0,1]),'left':([[-1,-1,1],[-1,-1,-1],[-1,1,-1],[-1,1,1]],[-1,0,0]),'right':([[1,-1,-1],[1,-1,1],[1,1,1],[1,1,-1]],[1,0,0]),'top':([[-1,1,-1],[1,1,-1],[1,1,1],[-1,1,1]],[0,1,0]),'bottom':([[-1,-1,1],[1,-1,1],[1,-1,-1],[-1,-1,-1]],[0,-1,0])}
 for n in nodes:
  shape=n['shape'];dims=np.array([shape['settings']['size'][k]*shape['stretch'][k] for k in 'xyz']);rot=rotation(n['orientation']);pos=np.array([n['position'][k] for k in 'xyz'])
  for key,(verts,normal) in face.items():
   norm=rot @ np.array(normal)
   if norm @ camera<=0:continue
   vs=(np.array(verts)*dims/2) @ rot.T+pos;pts=np.array([[v @ right,-v @ up] for v in vs]);off=shape['textureLayout'][key]['offset'];tile=tex.crop((off['x'],off['y'],off['x']+32,off['y']+32));polys.append((np.mean(vs @ camera),pts,tile,float(.72+.28*max(0,norm @ np.array([.3,.8,-.5])))))
 allpts=np.concatenate([p[1] for p in polys]);low=allpts.min(axis=0);high=allpts.max(axis=0);scale=(size-28)/max(high-low);center=(low+high)/2;out=Image.new('RGBA',(size,size))
 for _,pts,tile,shade in sorted(polys,key=lambda x:x[0]):
  q=(pts-center)*scale+size/2;uv=np.array([[0,31],[31,31],[31,0]]);matrix=np.linalg.solve(np.column_stack([q[:3],np.ones(3)]),uv).T.flatten();paint=tile.transform((size,size),Image.Transform.AFFINE,tuple(matrix),resample=Image.Resampling.NEAREST);arr=np.array(paint);arr[:,:,:3]=(arr[:,:,:3]*shade).astype('uint8');paint=Image.fromarray(arr);mask=Image.new('L',(size,size));ImageDraw.Draw(mask).polygon([tuple(p) for p in q],fill=255);out.paste(paint,(0,0),mask)
 return out
for name,nodes in [('Crystal',crystal),('OreOutcrops',ore)]:
 model={'nodes':nodes,'format':'character','lod':'auto'};write(Path('Common/Items/Shrinkium')/(name+'.blockymodel'),model);(S/(name+'.parts.json')).write_text(json.dumps(model,indent=2)+'\n')
 icon=render(nodes,atlas,64);png(Path('Common/Icons/Items')/('SH_'+name+'.png'),icon);render(nodes,atlas).save(P/(name+'.png'))
# Source-only stock host reference in the preview; runtime references native texture by path.
z=zipfile.ZipFile(os.environ['HYTALE_ASSETS_ZIP']);stone=Image.open(z.open('Common/BlockTextures/Rock_Stone.png')).convert('RGBA').resize((32,32),Image.Resampling.NEAREST);previewAtlas=atlas.copy();previewAtlas.paste(stone,(0,192));host=node('native-host',(0,16,0),(32,32,32),'steel');host['shape']['textureLayout']={f:{'offset':{'x':0,'y':192},'mirror':{'x':False,'y':False},'angle':0} for f in ['front','back','left','right','top','bottom']};render([host]+ore,previewAtlas).save(P/'Ore_Stone.png');png(Path('Common/Icons/Items/SH_Ore_Stone.png'),render([host]+ore,previewAtlas,64))
# Native UI frame/button textures, painted bevels and readable states.
def panel(w,h,fill,border):
 im=Image.new('RGBA',(w,h),fill);d=ImageDraw.Draw(im)
 for inset,c in [(0,'#10151c'),(2,border),(5,'#6d7981'),(7,'#303e4b'),(9,'#151e29')]:d.rectangle((inset,inset,w-inset-1,h-inset-1),outline=c,width=2)
 d.line((10,h-10,w-10,h-10),fill='#080e17',width=2);return im
png(Path('Common/UI/Custom/Pages/Shrinkium/Panel.png'),panel(96,96,'#202b36','#4d5e6d'))
for name,fill,border in [('Button','#303e4d','#617482'),('Hover','#405264','#a6b8c5'),('Pressed','#4a385a','#c99aee')]:png(Path('Common/UI/Custom/Pages/Shrinkium/'+name+'.png'),panel(48,48,fill,border))
# Original beam dots/impact shards; finite bursts only.
glow=Image.new('RGBA',(32,32));d=ImageDraw.Draw(glow);d.polygon([(16,0),(23,10),(31,16),(23,22),(16,31),(9,22),(0,16),(9,10)],fill=(171,86,240,55));d.polygon([(16,5),(21,12),(27,16),(21,20),(16,27),(11,20),(5,16),(11,12)],fill=(208,148,255,185));d.rectangle((13,13,18,18),fill=(244,225,255,255));png(Path('Common/Particles/Shrinkium/Beam.png'),glow)
for name,count,scale,life in [('Beam',1,.13,.22),('Impact',14,.16,.5)]:
 sp={'RenderMode':'Erosion','ParticleRotationInfluence':'Billboard','LinearFiltering':False,'LightInfluence':0,'MaxConcurrentParticles':count,'ParticleLifeSpan':{'Min':life,'Max':life},'SpawnBurst':True,'TotalParticles':{'Min':count,'Max':count},'Particle':{'Texture':'Particles/Shrinkium/Beam.png','InitialAnimationFrame':{'Opacity':1,'Color':'#ffffff','Scale':{'X':{'Min':scale,'Max':scale},'Y':{'Min':scale,'Max':scale}}},'Animation':{'100':{'Opacity':0}}}}
 if name=='Impact':sp['InitialVelocity']={'Speed':{'Min':.3,'Max':1.2},'Yaw':{'Min':-180,'Max':180},'Pitch':{'Min':-180,'Max':180}}
 write(Path('Server/Particles/Shrinkium')/('SH_'+name+'.particlespawner'),sp);write(Path('Server/Particles/Shrinkium')/('SH_'+name+'.json'),{'Spawners':[{'SpawnerId':'SH_'+name}],'LifeSpan':life,'CullDistance':40})
# Items with original models and native crafting authority.
base={'MaxStack':50,'ItemSoundSetId':'SH_Handling','PlayerAnimationsId':'Block','Categories':['Items.Materials']}
write(Path('Server/Item/Items/Shrinkium/SH_Crystal.json'),dict(base,TranslationProperties={'Name':'server.items.SH_Crystal.name','Description':'server.items.SH_Crystal.description'},Icon='Icons/Items/SH_Crystal.png',Model='Items/Shrinkium/Crystal.blockymodel',Texture='Items/Shrinkium/Atlas.png',IconProperties={'Scale':1.3,'Rotation':[0,0,0]}))
write(Path('Server/Item/Items/Shrinkium/SH_Ray.json'),{'TranslationProperties':{'Name':'server.items.SH_Ray.name','Description':'server.items.SH_Ray.description'},'Icon':'Icons/Items/SH_Ray.png','Model':'Items/Shrinkium/Ray.blockymodel','Texture':'Items/Shrinkium/Atlas.png','IconProperties':{'Scale':1,'Rotation':[0,0,0]},'PlayerAnimationsId':'Crossbow','Categories':['Items.Tools'],'MaxStack':1,'ItemSoundSetId':'SH_Handling','Utility':{'Compatible':True},'Interactions':{'Primary':{'Interactions':[{'Type':'SH_Ray','RunTime':0}]},'Secondary':{'Interactions':[{'Type':'SH_Ray','RunTime':0}]}},'Recipe':{'Input':[{'ItemId':'Ingredient_Bar_Iron','Quantity':6},{'ItemId':'Ingredient_Bar_Copper','Quantity':4},{'ItemId':'SH_Crystal','Quantity':2}],'BenchRequirement':[{'Type':'Crafting','Id':'Workbench','Categories':['Workbench_Tools']}],'TimeSeconds':4}})
write(Path('Server/Item/Items/Shrinkium/SH_Ore_Stone.json'),{'TranslationProperties':{'Name':'server.items.SH_Ore_Stone.name'},'Icon':'Icons/Items/SH_Ore_Stone.png','Categories':['Blocks.Ores'],'MaxStack':25,'PlayerAnimationsId':'Block','ItemSoundSetId':'SH_Handling','BlockType':{'Material':'Solid','DrawType':'CubeWithModel','CustomModel':'Items/Shrinkium/OreOutcrops.blockymodel','CustomModelTexture':[{'Texture':'Items/Shrinkium/Atlas.png','Weight':1}],'Textures':[{'All':'BlockTextures/Rock_Stone.png','Weight':1}],'Group':'Stone','RandomRotation':'YawStep90','Gathering':{'Breaking':{'GatherType':'OreCopper','DropList':{'Container':{'Type':'Single','Item':{'ItemId':'SH_Crystal','QuantityMin':2,'QuantityMax':2}}}}},'BlockParticleSetId':'Ore','ParticleColor':'#b273e8','PhysicalMaterialId':'Stone','BlockSoundSetId':'SH_CrystalBlock'}})
write(Path('Server/Item/Block/Sounds/SH_CrystalBlock.json'),{'SoundEvents':{k:'SH_Select' for k in ['Walk','Land','Hit','Break','Build']}})
for name in ['Fire','Restore','Select','HandlingCue']:
 write(Path('Server/Audio/SoundEvents/Shrinkium')/('SH_'+name+'.json'),{'Parent':'SFX_Attn_Quiet','AudioCategory':'AudioCat_SFX','Volume':-7,'MaxInstance':4,'StartAttenuationDistance':2,'MaxDistance':16,'SpatialBlend':0 if name=='HandlingCue' else 1,'Layers':[{'Files':['Sounds/Shrinkium/'+name.lower()+'.ogg'],'Looping':False,'Volume':0}]})
write(Path('Server/Audio/ItemSounds/Shrinkium/SH_Handling.json'),{'Parent':'ISS_Default','SoundEvents':{'Drag':'SH_HandlingCue','Drop':'SH_HandlingCue'}})
lang=A/'Server/Languages/en-US/server.lang';lang.parent.mkdir(parents=True,exist_ok=True);lang.write_text('items.SH_Crystal.name = Shrinkium Crystal\nitems.SH_Crystal.description = Cave-grown crystal. One successful ray size change per crystal.\nitems.SH_Ore_Stone.name = Shrinkium Crystal Ore\nitems.SH_Ray.name = Shrink Ray\nitems.SH_Ray.description = Primary: aimed shot. Secondary: choose size or self target. One crystal per successful change. Free emergency self restore: /shrinkium restore\n')
from ray_v2 import build as build_ray
build_ray()
print('Original geometry, painted UV atlases, native item definitions, finite effects and source previews written')
