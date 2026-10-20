"""Bounded CPU review material for existing V6 captures; never Unity/GPU/ASR.

Extracts one midpoint from each short clip once, reuses captured endpoints,
checks actual model-space anchor directions, and composes native/mobile boards.
Boards are sampled motion evidence, not a claim of whole-motion playback.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[4]
H=Path(__file__).parent
O=ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v6'
CAP=O/'spatial-clips'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def v(p):return np.array([p['x'],p['y'],p['z']],dtype=float)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');args=ap.parse_args()
    if not args.run:ap.print_help();return
    control=read(ROOT/'shared/publishing/video-production-control.json')
    assert control['selectedVideo']=='game-math-euler-axis-angle' and control['newProductionAuthorization']['fullProductionAuthorized']
    receipt=read(CAP/'spatial-capture-receipt.json')
    assert not receipt['sampleOnly'] and len(receipt['outputs'])==49 and sum(c['frames'] for c in receipt['outputs'])==19200
    readout=read(CAP/'readouts/outputs.json');assert len(readout['outputs'])==49
    assert readout['inputs']['captureReceiptSha256']==sha(CAP/'spatial-capture-receipt.json')
    spec=importlib.util.spec_from_file_location('readout_review',H/'spatial-readouts.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    shots={s['id']:s for s in read(m.CATALOG)['shots']}
    q=CAP/'review';q.mkdir(exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',22)
    displays=[];proof=[];state_count=0;maximum=0.;png_count=0
    for item in receipt['outputs']:
        key=item['id'];n=item['frames'];shot=shots[key]
        paths={k:Path(s['path']) for k,s in item['files'].items()}
        for k,p in paths.items():assert sha(p)==item['files'][k]['sha256'],(key,k,'source changed')
        states=[json.loads(s) for s in paths['anchors'].read_text(encoding='utf8').splitlines()]
        assert len(states)==n
        # Check actual geometry anchors against the actual recorded row basis,
        # independently of readout input parameter formatting.
        for f,state in enumerate(states):
            assert state['frame']==f and state['shotId']==key
            anchors={a['name']:a for a in state['anchors']}
            for side in ['a','b']:
                if not shot.get(side):continue
                r=np.array(state['rowMatrix'+side.upper()]).reshape(3,3)
                for name,basis in [('nose',2),('up',1),('bodyX',0),('bodyY',1),('bodyZ',2)]:
                    a=anchors[side+'.'+name];p=v(a['positionInUpright']);length=np.linalg.norm(p)
                    assert length>0,(key,f,side,name)
                    error=float(np.max(np.abs(p/length-r[basis]/np.linalg.norm(r[basis]))))
                    maximum=max(maximum,error);assert error<2e-5,(key,f,side,name,error)
                for axis in range(3):
                    p=v(anchors[side+'.upright'+'XYZ'[axis]]['positionInUpright']);p/=np.linalg.norm(p)
                    assert np.max(np.abs(p-np.eye(3)[axis]))<2e-5,(key,f,side,'upright',axis)
            state_count+=1
        images=[]
        for kind in ['firstFrame','lastFrame']:
            with Image.open(paths[kind]) as src:
                rgb=src.convert('RGB');assert rgb.size==(1920,1080)
                ar=np.array(rgb);delta=np.max(np.abs(ar.astype(np.int16)-ar[0,0].astype(np.int16)),axis=2)
                assert int((delta>25).sum())>2000,(key,kind,'blank image')
                png_count+=1
        mid=q/(key+'.mid.png');meta=mid.with_suffix('.json');signature={'clipSha256':sha(paths['clip']),'frame':n//2}
        if not(mid.exists() and meta.exists() and read(meta).get('inputs')==signature and read(meta).get('sha256')==sha(mid)):
            # Exactly one selected frame from a CPU decoder; no full decode claim.
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-i',str(paths['clip']),
                '-vf',f'select=eq(n\\,{n//2})','-frames:v','1','-threads','1','-y',str(mid)],check=True)
            meta.write_text(json.dumps({'inputs':signature,'sha256':sha(mid)},indent=2)+'\n',encoding='utf8')
        for label,f,source in [('first',0,paths['firstFrame']),('mid',n//2,mid),('last',n-1,paths['lastFrame'])]:
            dest=q/(key+'.'+label+'.display.png')
            m.still(source,dest,m.layout(shot,m.evaluated(shot,states[f]['normalizedTime'],states[f])))
            images.append(dest)
        displays.append((key,images))
        proof.append({'id':key,'frames':n,'sampleFrames':[0,n//2,n-1],'clipSha256':sha(paths['clip']),
            'displays':[{'path':rel(p),'sha256':sha(p)} for p in images]})
    pages=[]
    for start in range(0,len(displays),4):
        group=displays[start:start+4];page_no=start//4
        for mobile in [False,True]:
            w=375 if mobile else 640;hh=211 if mobile else 360;label_h=32
            board=Image.new('RGB',(w*3,(hh+label_h)*len(group)),'#080b0d');draw=ImageDraw.Draw(board)
            for row,(key,files) in enumerate(group):
                for col,path in enumerate(files):
                    top=row*(hh+label_h)
                    draw.text((col*w+8,top+2),key+' '+['first','middle','last'][col],font=font,fill='#e8cf83')
                    with Image.open(path) as im:board.paste(im.resize((w,hh),Image.Resampling.LANCZOS),(col*w,top+label_h))
            dest=q/(('mobile-' if mobile else 'native-')+f'{page_no:02}.jpg');board.save(dest,quality=94)
            pages.append({'path':rel(dest),'sha256':sha(dest),'mobile375':mobile,'shotIds':[key for key,_ in group]})
    result={'schemaVersion':1,'captureReceiptSha256':sha(CAP/'spatial-capture-receipt.json'),
        'readoutOutputsSha256':sha(CAP/'readouts/outputs.json'),'implementationSha256':sha(Path(__file__)),
        'checks':{'clips':49,'frames':19200,'actualAnchorFramesChecked':state_count,'maximumActualGeometryDirectionVersusRowMatrixError':maximum,
            'capturedEndpointPNGDimensionsAndNonblankChecked':png_count,'noUnityGPUASRStarted':True},
        'clips':proof,'pages':pages,'directImageReview':'pending actual viewing of all listed native/mobile pages',
        'limits':['One midpoint and existing endpoints per finite clip; does not claim whole-motion playback.',
            'Root final term chips, captions and joins remain outside these intermediate boards.']}
    dest=q/'outputs.json';dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'clips':49,'endpointPNGs':png_count,'actualAnchorFrames':state_count,'pages':len(pages),'output':str(dest)}),flush=True)

if __name__=='__main__':main()
