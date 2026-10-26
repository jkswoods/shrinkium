#!/usr/bin/env python3
"""Original Crystal Focus Ray: native box geometry, painted face atlas, source renders."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import copy, json, math, random
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'src/main/resources'
PREVIEW = ROOT / 'art/previews'
MATERIALS = {
    'brass': (174, 119, 47), 'brass_edge': (212, 158, 74),
    'brass_dark': (115, 76, 35), 'plum': (62, 35, 58),
    'plum_edge': (94, 52, 78), 'steel': (35, 37, 49),
    'copper': (159, 77, 40), 'copper_edge': (200, 109, 58),
    'walnut': (104, 53, 31), 'walnut_dark': (64, 31, 25),
    'crystal': (130, 64, 190), 'crystal_light': (179, 110, 224),
    'crystal_dark': (75, 36, 126), 'lens': (162, 86, 233),
    'conduit': (150, 83, 222), 'mark': (202, 183, 217),
}
TILES = {name: ((i % 8) * 32, (i // 8) * 32) for i, name in enumerate(MATERIALS)}
FACETS = []

def paint_atlas():
    atlas = Image.new('RGBA', (256, 256))
    for i, (name, base) in enumerate(MATERIALS.items()):
        tile = Image.new('RGBA', (32, 32))
        d = ImageDraw.Draw(tile)
        def c(k): return tuple(max(0, min(255, round(v*k))) for v in base) + (255,)
        d.rectangle((0, 0, 31, 31), fill=c(.93))
        if name.startswith('crystal') or name == 'conduit':
            for verts, shade in [([(0,0),(19,0),(10,11),(0,17)],1.35),
                                 ([(19,0),(31,0),(31,17),(10,11)],1.07),
                                 ([(0,17),(10,11),(19,23),(4,31),(0,31)],.76),
                                 ([(10,11),(31,17),(19,23)],1.50),
                                 ([(19,23),(31,17),(31,31),(4,31)],.59)]:
                d.polygon(verts, fill=c(shade))
            d.line([(1,16),(10,11),(19,0)], fill=c(1.75), width=1)
            d.line([(10,11),(19,23),(30,18)], fill=c(1.30), width=1)
            d.polygon([(3,3),(14,2),(8,6)], fill=c(1.8))
        elif name == 'lens':
            d.rectangle((0,0,31,31), fill=(30,18,49,255))
            for radius, colour in [(15,(65,30,102)),(13,(124,56,181)),(10,(195,119,249)),(7,(139,64,210)),(4,(222,174,255)),(2,(249,228,255))]:
                verts=[(16+radius*math.sin(a*math.pi/4),16+radius*math.cos(a*math.pi/4)) for a in range(8)]
                d.polygon(verts, fill=colour+(255,))
            d.line((6,7,11,4), fill=(237,198,255,255), width=1)
        elif name.startswith('walnut'):
            d.polygon([(0,0),(12,0),(23,31),(0,31)],fill=c(1.1))
            d.polygon([(20,0),(31,0),(31,31),(26,31)],fill=c(.71))
            for x in [4, 13, 24]:
                d.line([(x,1),(x-2,9),(x+3,18),(x+1,30)],fill=c(.68),width=1)
                d.line([(x+2,2),(x,10),(x+5,21)],fill=c(1.3),width=1)
            d.polygon([(4,5),(7,3),(9,8),(6,12)],fill=c(1.4))
        else:
            d.polygon([(0,0),(31,0),(31,5),(24,9),(8,7),(0,14)],fill=c(1.24))
            d.polygon([(0,14),(8,7),(14,22),(7,31),(0,31)],fill=c(.93))
            d.polygon([(24,9),(31,5),(31,31),(7,31),(14,22)],fill=c(.75))
            d.line([(0,1),(31,1)],fill=c(1.55),width=1)
            rng=random.Random(844+i)
            for k in range(5):
                x=rng.randrange(2,26); y=rng.choice([2,3,27,29])
                d.line([(x,y),(min(x+4,30),max(y-1,0))],fill=c(1.6 if k%2 else .50),width=1)
            d.polygon([(3,13),(6,10),(9,11),(6,15)],fill=c(1.17))
        atlas.paste(tile,TILES[name])
    for offset, image in FACETS:
        atlas.paste(image,offset)
    return atlas

def matrix_quaternion(m):
    # Native ZYX quaternion, from the world-space basis of a planar face.
    trace=np.trace(m)
    if trace>0:
        s=math.sqrt(trace+1)*2; q=((m[2,1]-m[1,2])/s,(m[0,2]-m[2,0])/s,(m[1,0]-m[0,1])/s,s/4)
    else:
        i=int(np.argmax(np.diag(m)));j=(i+1)%3;k=(i+2)%3;s=math.sqrt(1+m[i,i]-m[j,j]-m[k,k])*2
        v=[0.,0.,0.,0.];v[i]=s/4;v[j]=(m[j,i]+m[i,j])/s;v[k]=(m[k,i]+m[i,k])/s;v[3]=(m[k,j]-m[j,k])/s;q=v
    return dict(zip('xyzw',map(float,q)))

def triangle(name,a,b,c,shade_index):
    a,b,c=map(lambda p:np.array(p,dtype=float),(a,b,c))
    x=b-a;length=np.linalg.norm(x);x/=length
    normal=np.cross(b-a,c-a);normal/=np.linalg.norm(normal);y=np.cross(normal,x)
    cx=float((c-a) @ x);cy=float((c-a) @ y);left=min(0,cx);right=max(length,cx);width=right-left
    center=a+x*(left+right)/2+y*cy/2
    uv=[((0-left)/width*31,31),((length-left)/width*31,31),((cx-left)/width*31,0)]
    tile=Image.new('RGBA',(32,32));draw=ImageDraw.Draw(tile)
    palette=[(125,59,186),(154,81,210),(99,45,164),(185,115,228),(127,54,191)]
    base=(184,110,231) if normal[1]>.45 else (150,77,209) if normal[0]>.35 else palette[shade_index%len(palette)]
    brightness=.90+.22*max(0,normal[1])
    colour=lambda s:tuple(min(255,round(v*s*brightness)) for v in base)+(255,)
    draw.polygon(uv,fill=colour(1))
    # Bleed colour beyond the alpha cut so adjoining native planar facets have no texel cracks.
    draw.line(uv+[uv[0]],fill=colour(1),width=3)
    mid=tuple((uv[0][i]+uv[1][i]+uv[2][i])/3 for i in range(2))
    draw.polygon([uv[0],uv[2],mid],fill=colour(1.12))
    if shade_index%3==0:draw.line([uv[0],uv[2]],fill=colour(1.45),width=1)
    idx=16+len(FACETS);offset=((idx%8)*32,(idx//8)*32);FACETS.append((offset,tile))
    return {'id':name,'name':name,'position':dict(zip('xyz',map(float,center))), 'orientation':matrix_quaternion(np.column_stack([x,y,normal])),
            'shape':{'type':'quad','offset':dict.fromkeys('xyz',0),'stretch':{'x':width/32,'y':cy/32,'z':1},
                     'settings':{'size':{'x':32,'y':32},'normal':'+Z'},'textureLayout':{'front':{'offset':dict(zip('xy',offset)),'mirror':{'x':False,'y':False},'angle':0}},
                     'visible':True,'doubleSided':False,'shadingMode':'standard','unwrapMode':'custom'}}

def crystal_mesh(name,front_z,rear_z,radius,center_y,tail=False):
    front=[];rear=[]
    for i in range(6):
        a=i*math.pi/3+.18;r=radius*[1,.92,1.04,.93,1.02,.96][i]
        front.append((math.sin(a)*r,center_y+math.cos(a)*r,front_z+[.2,-.3,.35,-.1,.1,-.25][i]))
        rear.append((math.sin(a+.13)*r*.85,center_y+math.cos(a+.13)*r*.85,rear_z+[.2,-.2,.15,-.2,.1,0][i]))
    start=(.3,center_y-.1,front_z-2.0);end=(-.2,center_y+.2,rear_z+2.3)
    faces=[]
    for i in range(6):
        j=(i+1)%6
        if tail:
            faces.extend([(start,front[i],front[j]),(end,front[j],front[i])])
        else:
            faces.extend([(start,front[i],front[j]),(front[i],rear[i],rear[j]),(front[i],rear[j],front[j]),(end,rear[j],rear[i])])
    return [triangle(f'{name}-facet-{i}',*vertices,i+(5 if tail else 0)) for i,vertices in enumerate(faces)]

def dial_face():
    tile=Image.new('RGBA',(32,32));d=ImageDraw.Draw(tile)
    for radius,fill in [(15,'#654523'),(13,'#c18a3e'),(11,'#a97130'),(8,'#b67e36')]:
        verts=[(16+radius*math.sin(i*math.pi/4+math.pi/8),16+radius*math.cos(i*math.pi/4+math.pi/8)) for i in range(8)]
        d.polygon(verts,fill=fill)
    d.line([(6,8),(12,4),(23,6)],fill='#e5b567',width=2)
    d.line([(8,24),(20,27),(26,21)],fill='#7c5127',width=2)
    idx=16+len(FACETS);offset=((idx%8)*32,(idx//8)*32);FACETS.append((offset,tile))
    return {'id':'selector-face','name':'selector-face','position':{'x':6.65,'y':7.,'z':8.3},'orientation':quaternion(0,90,0),
            'shape':{'type':'quad','offset':dict.fromkeys('xyz',0),'stretch':{'x':5.2/32,'y':5.2/32,'z':1},
                     'settings':{'size':{'x':32,'y':32},'normal':'+Z'},'textureLayout':{'front':{'offset':dict(zip('xy',offset)),'mirror':{'x':False,'y':False},'angle':0}},
                     'visible':True,'doubleSided':False,'shadingMode':'standard','unwrapMode':'custom'}}

def quaternion(rx=0,ry=0,rz=0):
    x,y,z=[math.radians(t)/2 for t in (rx,ry,rz)]
    sx,cx=math.sin(x),math.cos(x); sy,cy=math.sin(y),math.cos(y); sz,cz=math.sin(z),math.cos(z)
    return dict(zip('xyzw',(sx*cy*cz-cx*sy*sz,cx*sy*cz+sx*cy*sz,cx*cy*sz-sx*sy*cz,cx*cy*cz+sx*sy*sz)))

def part(name, pos, size, material, rot=(0,0,0), faces=None):
    faces=faces or {}
    layout={f:{'offset':dict(zip('xy',TILES[faces.get(f,material)])), 'mirror':{'x':False,'y':False}, 'angle':0} for f in ['front','back','left','right','top','bottom']}
    return {'id':name,'name':name,'position':dict(zip('xyz',pos)), 'orientation':quaternion(*rot),
            'shape':{'type':'box','offset':dict.fromkeys('xyz',0),'stretch':dict(zip('xyz',[v/32 for v in size])),
                     'settings':{'size':dict.fromkeys('xyz',32)},'textureLayout':layout,'unwrapMode':'custom',
                     'visible':True,'doubleSided':False,'shadingMode':'standard'}}

def make_model():
    FACETS.clear()
    p=[]
    def add(*args,**kwargs): p.append(part(*args,**kwargs))
    def ring(name,z,r,depth,material,wall=1.2,y=7):
        tangent=2*r*math.tan(math.pi/8)+.09
        for i in range(8):
            a=i*math.pi/4
            add(f'{name}-{i}',(r*math.sin(a),y+r*math.cos(a),z),(tangent,wall,depth),material,(0,0,-i*45),faces={'bottom':'brass_dark' if material.startswith('brass') else material})
    # Faceted rear receiver and a deliberately open, physically joined reactor cage.
    add('receiver-core',(0,6,8.5),(8.4,9,8.5),'plum',faces={'top':'plum_edge','bottom':'steel'})
    for sign in [-1,1]:
        add(f'receiver-bevel-{sign}',(sign*4.1,7.1,8.5),(2.2,7.5,8.5),'plum_edge',(0,0,sign*24))
        add(f'receiver-lower-bevel-{sign}',(sign*3.8,2.1,8.3),(2.4,3.5,8),'plum',(0,0,-sign*32))
    ring('rear-collar',12.8,4.8,1.7,'brass',1.5)
    ring('rear-saddle',4.3,5.6,1.7,'brass',1.25)
    ring('front-saddle',-9.8,5.6,2.1,'brass',1.4)
    # Irregular closed faceted crystals built from native alpha-cut planar triangles.
    p.extend(crystal_mesh('reactor',-7.2,2.5,4.2,7.0))
    p.extend(crystal_mesh('tail-crystal',13.3,16.1,3.7,7.0,True))
    for sign in [-1,1]:
        add(f'cage-side-rail-{sign}',(sign*5.1,3.5,-2.6),(1.4,1.7,14.7),'brass',faces={'top':'brass_edge'})
        add(f'cage-top-rail-{sign}',(sign*2.4,12.4,-2.7),(1.4,1.3,15.0),'brass',faces={'top':'brass_edge'})
        add(f'cage-heel-{sign}',(sign*5.1,4.3,4.0),(1.6,3.4,2.8),'brass',(20,0,0))
        add(f'violet-conduit-{sign}',(sign*4.9,5.0,3.2),(.85,.85,5.2),'conduit',(-28,0,0))
        add(f'conduit-coupling-{sign}',(sign*4.9,6.1,5.2),(1.3,1.3,1.5),'copper',(-28,0,0))
    add('under-chamber-keel',(0,1.9,-2.6),(3,1.2,14.8),'plum',faces={'bottom':'steel'})
    # Copper compression coils lead to the flared, open focusing head.
    add('neck',(0,7,-13.6),(5.4,5.4,6.2),'plum',(0,0,45),faces={'top':'plum_edge'})
    ring('copper-coil-a',-12.0,3.9,1.4,'copper',1.25)
    ring('copper-coil-b',-14.0,3.9,1.4,'copper_edge',1.25)
    ring('focusing-head',-17.3,5.2,2.6,'brass',1.45)
    add('lens-shroud',(0,7,-17.8),(7.5,7.5,2.4),'plum',(0,0,45))
    add('recessed-lens',(0,7,-19.12),(7.0,7.0,.22),'lens',faces={f:'steel' for f in ['back','left','right','top','bottom']})
    for i in range(4):
        a=i*math.pi/2; x=5.6*math.sin(a); y=7+5.6*math.cos(a)
        add(f'focus-prong-{i}',(x,y,-20.1),(2.5,2.6,5.2),'brass',(0,0,-i*90),faces={'top':'brass_edge'})
        add(f'focus-prong-flare-{i}',(7.0*math.sin(a),7+7.0*math.cos(a),-22.9),(2.8,2.5,3.1),'brass_edge',(-18*math.cos(a),-18*math.sin(a),-i*90))
    # Hand-shaped grip and connected open guard rather than a rectangular handle.
    add('grip-upper',(0,-1.8,8.0),(6.5,7.2,7.2),'walnut',(-24,0,0),faces={'back':'walnut_dark'})
    add('grip-palm',(0,-7.4,10.1),(6.4,8.2,7.5),'walnut',(-24,0,0),faces={'back':'walnut_dark'})
    add('grip-heel',(0,-12.3,12.3),(7.2,3.0,8.1),'brass',(-24,0,0),faces={'top':'brass_edge'})
    add('grip-backstrap',(0,-6.0,13.5),(1.5,12,1.3),'brass_dark',(-24,0,0))
    add('grip-tang',(0,.7,12.7),(7.6,1.6,5.2),'brass',(-22,0,0))
    add('trigger',(0,-1.4,1.1),(1.0,5.4,1.5),'brass_dark',(-24,0,0))
    add('guard-front',(0,-2.3,-2.8),(1.6,7.9,1.6),'brass',(25,0,0))
    add('guard-bottom',(0,-5.9,.5),(1.8,1.5,7.8),'brass',(0,0,0))
    add('guard-rear',(0,-3.5,4.7),(1.8,5.8,1.6),'brass',(24,0,0))
    # Static selector hardware has three calibration marks, no fake selected-state light.
    for i in range(8):
        a=i*math.pi/4
        add(f'dial-rim-{i}',(6.1,7+2.3*math.cos(a),8.3+2.3*math.sin(a)),(.8,.65,2*2.3*math.tan(math.pi/8)+.05),'brass_dark',(i*45,0,0))
    p.append(dial_face())
    add('selector-thumb-ridge',(6.85,7.0,8.3),(.45,3.4,1.0),'brass_edge',(35,0,0))
    for i,a in enumerate([-42,0,42]):
        angle=math.radians(a)
        add(f'selector-calibration-{i}',(5.6,7+3.7*math.cos(angle),8.3+3.7*math.sin(angle)),(.16,.65,.32),'mark',(a,0,0))
    for sign in [-1,1]:
        add(f'front-rail-fastener-{sign}',(sign*5.95,5.0,-8.4),(.6,1.7,1.7),'brass_edge',(45,0,0))
        add(f'grip-heel-rivet-{sign}',(sign*3.65,-12.2,12.2),(.4,1.8,1.8),'brass_edge',(45,0,0))
    return {'nodes':p,'format':'character','lod':'auto'}

def rotation(q):
    x,y,z,w=[q[k] for k in 'xyzw']
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                     [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                     [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])

def native_mount(model):
    """Match stock Crossbow's named hand attachment and +Z direction.

    The design is authored muzzle-first along -Z. Rotate the whole flat model
    180 degrees around Y, including each face basis, for the native hand mount.
    Keep local shape/UV data intact so crystal triangle winding is preserved.
    """
    mounted = copy.deepcopy(model)
    for node in mounted['nodes']:
        assert not node.get('children'), 'Mount conversion expects flat authored nodes'
        pos = node['position']
        # Stock Crossbow's nested Handle2 center is (0, 7.5, -6.5).
        # Align our palm center to that inspected native grip position.
        pos['x'], pos['y'], pos['z'] = -pos['x'], pos['y'] + 14.9, -pos['z'] + 3.6
        q = node['orientation']
        x, y, z, w = (q[k] for k in 'xyzw')
        # Left multiply by Y180 quaternion (0, 1, 0, 0).
        node['orientation'] = dict(zip('xyzw', (z, w, -x, -y)))
    # The client binds this named piece to the player's hand. Flat unnamed
    # roots do not provide the same native attachment contract.
    mounted['nodes'] = [{
        'id': 'ray-hand-attachment', 'name': 'R-Attachment',
        'position': dict.fromkeys('xyz', 0),
        'orientation': dict(zip('xyzw', (0, 0, 0, 1))),
        'shape': {'type': 'none', 'offset': dict.fromkeys('xyz', 0),
                  'stretch': dict.fromkeys('xyz', 1),
                  'settings': {'isPiece': True}, 'visible': True,
                  'doubleSided': False, 'shadingMode': 'flat',
                  'unwrapMode': 'custom', 'textureLayout': {}},
        'children': mounted['nodes'],
    }]
    return mounted

FACES={
 'front':([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1]],[0,0,-1]),
 'back':([[1,-1,1],[-1,-1,1],[-1,1,1],[1,1,1]],[0,0,1]),
 'left':([[-1,-1,1],[-1,-1,-1],[-1,1,-1],[-1,1,1]],[-1,0,0]),
 'right':([[1,-1,-1],[1,-1,1],[1,1,1],[1,1,-1]],[1,0,0]),
 'top':([[-1,1,-1],[1,1,-1],[1,1,1],[-1,1,1]],[0,1,0]),
 'bottom':([[-1,-1,1],[1,-1,1],[1,-1,-1],[-1,-1,-1]],[0,-1,0])}

def render(model,tex,size=1024,camera=(1.3,.65,-1.2),margin=.08,light=(.2,.8,-.6)):
    camera=np.array(camera,dtype=float);camera/=np.linalg.norm(camera)
    light=np.array(light,dtype=float);light/=np.linalg.norm(light)
    right=np.cross(camera,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,camera)
    polys=[]
    # Exported attachment root has identity transform; render its real children.
    nodes=model['nodes']
    if len(nodes)==1 and nodes[0]['shape']['type']=='none':
        assert nodes[0]['position']==dict.fromkeys('xyz',0)
        nodes=nodes[0]['children']
    for n in nodes:
        sh=n['shape']; dims=np.array([sh['settings']['size'].get(k,0)*sh['stretch'][k] for k in 'xyz'])
        rot=rotation(n['orientation']);pos=np.array([n['position'][k] for k in 'xyz'])
        faces=FACES if sh['type']=='box' else {'front':([[-1,-1,0],[1,-1,0],[1,1,0],[-1,1,0]],[0,0,1])}
        for name,(verts,normal) in faces.items():
            norm=rot @ np.array(normal)
            if norm @ camera<=.00001:continue
            vs=(np.array(verts)*dims/2) @ rot.T+pos
            pts=np.array([[v @ right,-v @ up] for v in vs])
            off=sh['textureLayout'][name]['offset'];tile=tex.crop((off['x'],off['y'],off['x']+32,off['y']+32))
            shade=.74+.26*max(0,norm @ light)
            polys.append((np.mean(vs @ camera),pts,tile,shade))
    allpts=np.concatenate([p[1] for p in polys]);low=allpts.min(axis=0);high=allpts.max(axis=0)
    scale=size*(1-margin*2)/max(high-low);center=(low+high)/2
    out=Image.new('RGBA',(size,size))
    for _,pts,tile,shade in sorted(polys,key=lambda x:x[0]):
        q=(pts-center)*scale+size/2;uv=np.array([[0,31],[31,31],[31,0]])
        coeff=np.linalg.solve(np.column_stack([q[:3],np.ones(3)]),uv).T.flatten()
        paint=tile.transform((size,size),Image.Transform.AFFINE,tuple(coeff),resample=Image.Resampling.NEAREST)
        arr=np.array(paint);arr[:,:,:3]=(arr[:,:,:3]*shade).astype('uint8');paint=Image.fromarray(arr)
        mask=Image.new('L',(size,size));ImageDraw.Draw(mask).polygon([tuple(v) for v in q],fill=255)
        alpha=Image.fromarray((np.array(mask,dtype=np.uint16)*np.array(paint.getchannel('A'),dtype=np.uint16)//255).astype('uint8'))
        paint.putalpha(alpha);out.alpha_composite(paint)
    return out

def build():
    authored=make_model();atlas=paint_atlas();model=native_mount(authored)
    target=RES/'Common/Items/Shrinkium';target.mkdir(parents=True,exist_ok=True)
    (target/'Ray.blockymodel').write_text(json.dumps(model,indent=2)+'\n')
    atlas.save(target/'RayAtlas.png')
    (ROOT/'art/source/Ray.parts.json').write_text(json.dumps(model,indent=2)+'\n')
    atlas.save(ROOT/'art/source/RayAtlas-v2.png')
    # Rotate the preview camera/light with the mount to show the same design side.
    mounted_light=(-.2,.8,.6)
    image=render(model,atlas,camera=(-1.3,.65,1.2),light=mounted_light)
    image.save(PREVIEW/'Ray.png');image.save(PREVIEW/'Ray-v2.png')
    render(model,atlas,camera=(-1,.12,0),light=mounted_light).save(PREVIEW/'Ray-v2-side.png')
    render(model,atlas,camera=(-.5,.2,1.5),light=mounted_light).save(PREVIEW/'Ray-v2-front.png')
    # The prerendered icon has its own presentation, independent of hand mounting.
    # Preserve the exact dev7 icon already verified in native hotbar/inventory.
    render(authored,atlas,size=64,margin=.04).save(RES/'Common/Icons/Items/SH_Ray.png')
    item=RES/'Server/Item/Items/Shrinkium/SH_Ray.json'
    data=json.loads(item.read_text());data['Texture']='Items/Shrinkium/RayAtlas.png';item.write_text(json.dumps(data,indent=2)+'\n')
    return model,atlas

if __name__=='__main__':
    model,atlas=build();print("Crystal Focus Ray: 137 original parts + named hand root, 256px painted atlas; source rendering only, native acceptance pending")
