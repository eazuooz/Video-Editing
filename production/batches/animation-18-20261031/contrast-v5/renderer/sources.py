"""Read-only adapters for recorded UE/Manim plates and their actual pose data."""
from pathlib import Path
from functools import lru_cache
import json,gzip,hashlib,sys,subprocess
from PIL import Image
import numpy as np
H=Path(__file__).resolve().parent; B=H.parent.parent; R=B.parents[2]
N=B/'local/real-clips-v2'
sys.path.insert(0,str(N/'python-deps'))
from scipy.spatial.transform import Rotation
from scipy.ndimage import label as components
read=lambda p:json.loads(Path(p).read_text('utf-8-sig'))
ROWS={r['id']:r for r in read(B/'real-clips-v2/revision-plan.json')['episodes'] if r['id']!='A03'}
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def project(ep):return R/'projects'/ROWS[ep]['slug']

@lru_cache(None)
def source(ep,key):
    assert ep in ROWS, 'A03 is immutable and outside this adapter'
    p=project(ep); metadata=None; movie=None; kind='actual-UE-authored-demonstration'
    realkey='A02-combat' if ep=='A01' and key=='strike' else ep+'-'+key
    real=N/'studies'/(realkey+'.json')
    if ep=='A08':
        local=B/'local/contrast-v5/a08-cumulative';metadata=local/'poses'/(key+'.json');d=read(metadata)
        receipt=read(local/'capture-receipt.json');assert receipt.get('definitionHashes',{}).get(key)==sha(metadata),('A08 actual capture not current',key)
        folder=local/'frames'/key;original=False
    elif real.is_file() and not (ep=='A04' and key=='jab' or ep=='A11' and key=='upper'):
        metadata=real; folder=N/'study-frames'/realkey; d=read(real); original=True
    elif ep=='A01':
        local=p/'production/local/unreal-kit-v2/unreal'
        folder=local/('final-renders' if key in ('stop','turn') else 'locked-renders')/key
        metadata=local/(key+'-build.json'); raw=read(metadata)
        d={'frames':raw['frames'],'cameraWidth':raw['camera']['widthCm'],'cameraHeight':raw['camera']['positionCm'][2],
           'cameraYaw':raw['camera']['yaw'],'sourceClip':raw['sourceAnimation']};original=True
    else:
        local=p/'production/local/series-v1';metadata=local/'poses'/(key+'.json')
        if metadata.is_file():d=read(metadata);folder=local/'frames'/key;original=False
        else:
            movie=local/(key+'.mp4');assert movie.is_file(),(ep,key,'missing source')
            meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_streams','-of','json',str(movie)]))['streams'][0]
            assert (meta['width'],meta['height'])==(1920,1080)
            d={'frames':int(meta['nb_frames'])};folder=None;kind='authored-Manim-illustration' if ep=='A09' else 'authored-diagram';original=False
    if folder:
        files=tuple(sorted(folder.glob('*.png')));assert len(files)>=d['frames'],(ep,key,len(files),d['frames'])
        with Image.open(files[0]) as im:assert im.size==(1920,1080)
    else:files=()
    return {'episode':ep,'key':key,'definition':d,'metadata':metadata,'files':files,'movie':movie,'kind':kind,'importedMotion':original}

@lru_cache(maxsize=90)
def image(ep,key,n):
    s=source(ep,key);n=min(s['definition']['frames']-1,max(0,int(n)))
    if s['files']:
        with Image.open(s['files'][n]) as im:return im.convert('RGB')
    data=subprocess.check_output(['ffmpeg','-v','error','-threads','2','-ss',str(n/60),'-i',str(s['movie']),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
    return Image.frombytes('RGB',(1920,1080),data)

def projected(d,p,side=0,world=False):
    p=np.array(p,dtype=float)
    if not world:
        yaw=np.radians(d.get('sideYaws',[d.get('yaw',-73)]*2)[side]);x,y,z=p
        p=np.array([x*np.cos(yaw)-y*np.sin(yaw),x*np.sin(yaw)+y*np.cos(yaw),z])
        spacing=d.get('actorSpacing',125)
        locations=d.get('actorLocations')
        if locations is None:
            animations=d.get('animations',[{},{}]);locations=[a.get('location',[spacing*(-1 if i==0 else 1)+d.get('shiftX',0),0,0]) for i,a in enumerate(animations)]
        p+=locations[side]
    camera=d.get('cameraLocation',[0,900,d.get('cameraHeight',85)]);yaw=d.get('cameraYaw',-90);pitch=d.get('cameraPitch',0)
    if d.get('cameraView')=='top':camera=[0,35,720];yaw=-90;pitch=-88
    yaw,pitch=np.radians([yaw,pitch]);rel=p-np.array(camera)
    right=np.array([-np.sin(yaw),np.cos(yaw),0]);up=np.array([-np.sin(pitch)*np.cos(yaw),-np.sin(pitch)*np.sin(yaw),np.cos(pitch)])
    # The old series templates inherit the A01 walk camera (ortho width500).
    # Its value is explicit in unreal-kit-v2/build_stages.py, not inferred from
    # pixels. Newer captures carry cameraWidth in their own saved definition.
    scale=1920/d.get('cameraWidth',500);return np.array([960+np.dot(rel,right)*scale,540-np.dot(rel,up)*scale])

@lru_cache(None)
def hierarchy(ep,key):
    s=source(ep,key);d=s['definition'];clip=d.get('sourceClip')
    if clip:
        if isinstance(clip,list):clip=clip[0]
        candidate=N/'source-motion'/(clip.split('/')[-1]+'.json.gz')
        if candidate.is_file():
            with gzip.open(candidate,'rt',encoding='utf8') as f:data=json.load(f)
            return {b['name']:b['parent'] for b in data['bones']}
    if ep in ('A12','A18'):
        data=read(R/'projects/animation-facial-animations/production/local/series-v1/reference-pose.json')
        return {n:b['parent'] for n,b in data['bones'].items()}
    data=read(R/'projects/animation-exaggeration/production/local/fighters-v3/unreal/asset-inspection.json')
    return {b['name']:b['parent'] for b in data['referenceBones'] if not b['name'].startswith('VB ')}

@lru_cache(maxsize=2000)
def world(ep,key,n,side):
    """Forward kinematics of the exact pose written to the recorded AnimSequence."""
    d=source(ep,key)['definition'];n=int(np.clip(n,0,d['frames']-1))
    if 'animations' not in d:return {}
    tracks=d['animations'][side]['tracks'];parents=hierarchy(ep,key);out={};scales={}
    def visit(name):
        if name in out:return out[name]
        t=tracks[name];p=np.asarray(t['p'][min(n,len(t['p'])-1)]);q=Rotation.from_quat(t['q'][min(n,len(t['q'])-1)])
        scale=np.asarray(t.get('s',[1,1,1]),dtype=float)
        if scale.ndim>1:scale=scale[min(n,len(scale)-1)]
        par=parents.get(name)
        if par in tracks:
            pp,pq=visit(par);p=pp+pq.apply(scales[par]*p);q=pq*q;scale=scales[par]*scale
        out[name]=(p,q);scales[name]=scale;return out[name]
    for name in tracks:visit(name)
    return out

def points(ep,key,n,side):return {k:v[0] for k,v in world(ep,key,n,side).items()}

def panel_offset(ep,key,side):
    d=source(ep,key)['definition']
    if side==0:return 0
    if 'cameraWidth' not in d:return 960
    return float(projected(d,[0,0,0],side)[0]-projected(d,[0,0,0],0)[0])

@lru_cache(None)
def bounds(ep,key):
    """One shared source crop for both variants; never normalize model size separately."""
    if ep=='A09' and key=='fist':return (300,180,765,575)
    if ep=='A18' and key=='wrist':return (250,220,850,850)
    if ep=='A15' and key=='keys':return (420,500,675,840)
    if ep=='A17' and key in ('fkik','hint'):return (220,210,785,750)
    if ep=='A18' and key!='wrist':return (205,220,790,850)
    if ep=='A12' and key!='distance':return (170,180,805,855)
    s=source(ep,key)
    if not s['files']:return (0,100,960,850)
    boxes=[]
    for n in np.linspace(0,s['definition']['frames']-1,7).astype(int):
        arr=np.asarray(image(ep,key,int(n)))
        for side in (0,1):
            a=arr[70:990,20+960*side:940+960*side]
            # Grey grid/floor excluded. Retain meaningful connected body/prop regions.
            mask=a.mean(axis=2)<145
            lab,count=components(mask);sizes=np.bincount(lab.ravel());sizes[0]=0
            keep=np.flatnonzero(sizes>max(120,sizes.max(initial=0)*.02))
            yy,xx=np.nonzero(np.isin(lab,keep))
            offset=960*side-panel_offset(ep,key,side)
            if len(xx)>100:boxes.append([xx.min()+20+offset,yy.min()+70,xx.max()+20+offset,yy.max()+70])
    if not boxes:return (20,130,940,850)
    a=np.array(boxes);x0,y0=a[:,:2].min(axis=0)-35;x1,y1=a[:,2:].max(axis=0)+35
    return (int(max(0,x0)),int(max(0,y0)),int(min(960,x1)),int(min(1080,y1)))

def input_receipt(ep,key):
    s=source(ep,key);n=s['definition']['frames'];sample=sorted(set([0,n//4,n//2,3*n//4,n-1]))
    return {'episode':ep,'key':key,'kind':s['kind'],'metadata':str(s['metadata'].relative_to(R)).replace('\\','/') if s['metadata'] else None,
            'metadataSHA256':sha(s['metadata']) if s['metadata'] else None,'frameCount':n,'fps':60,'resolution':[1920,1080],
            'sourceClip':s['definition'].get('sourceClip'),'sampleFrames':[{'frame':i,'path':str(s['files'][i].relative_to(R)).replace('\\','/'),'sha256':sha(s['files'][i])}for i in sample] if s['files'] else [],
            'movie':str(s['movie'].relative_to(R)).replace('\\','/') if s['movie'] else None,'movieSHA256':sha(s['movie']) if s['movie'] else None,
            'sameComparisonCrop':bounds(ep,key),'fullSequenceHashNotComputed':True,
            'sequenceStatDigest':hashlib.sha256(json.dumps([(f.name,f.stat().st_size,f.stat().st_mtime_ns)for f in s['files']]).encode()).hexdigest()}
