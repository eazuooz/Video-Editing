"""One CPU-only canonical heading patch; default prepares metadata only."""
from pathlib import Path
import argparse,copy,hashlib,json,os,subprocess
from PIL import Image
import numpy as np
H=Path(__file__).resolve().parent.parent;R=H.parents[3]
L=H/'local/a11-term-chip';OUT=Path('C:/Users/1/Videos/YamyamProduction/animation-contrast-v5-work/a11-term-chip')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.pending');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(t,p)
def run(args):subprocess.run([str(x)for x in args],check=True,cwd=H,creationflags=subprocess.CREATE_NO_WINDOW)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');ap.add_argument('--adopt',action='store_true');args=ap.parse_args()
    c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert c['renderAuthorized']and 'A11'in c['episodes']
    manifest=H/'game-plates-caption-safe.json';e=next(e for e in read(manifest)['episodes']if e['id']=='A11');r=next(r for r in e['pictureEdits']if(r['startFrame'],r['endFrame'])==(1188,1722))
    source=Path(r['picture']);assert source.is_absolute()and sha(source)==r['pictureSha256']and r['newFrames']==534
    L.mkdir(parents=True,exist_ok=True);title=L/'title.txt';title.write_text('Interpolation (보간)','utf8')
    dest=OUT/'A11-first-canonical-heading.mp4'
    filt="drawbox=x=30:y=26:w=1480:h=84:color=0x080c0a:t=fill,drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':textfile='local/a11-term-chip/title.txt':x=64:y=34:fontsize=72:fontcolor=0xf2d787"
    plan={'episode':'A11','startFrame':1188,'endFrame':1722,'frames':534,'source':str(source),'sourceSha256':sha(source),'output':str(dest),
        'title':'Interpolation (보간)','rectangle':[30,26,1480,84],'filter':filt,'scope':'Canonical term heading only. Preserve UE source-kind/current-picture labels, two panels, comparison labels, footer, captions area, native source timing and all audio.',
        'gpuUsed':False,'threads':4,'renderStarted':args.render,'sourceManifestSha256':sha(manifest)}
    save(L/'plan.json',plan)
    if args.render:
        OUT.mkdir(parents=True,exist_ok=True)
        run(['ffmpeg','-v','error','-nostdin','-y','-threads','4','-i',source,'-filter_threads','1','-vf',filt,'-frames:v','534','-an',
            '-c:v','libx264','-preset','veryfast','-crf','0','-threads','4','-bf','0','-g','120','-sc_threshold','0','-pix_fmt','yuv420p','-r','60',
            '-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',dest])
        spec=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(dest)]))['streams'];assert len(spec)==1
        v=spec[0];assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',534)
        checks=[]
        for n in(0,267,533):
            files=[]
            for label,file in [('before',source),('after',dest)]:
                png=L/f'{label}-{n:04d}.png';run(['ffmpeg','-v','error','-nostdin','-y','-threads','2','-i',file,'-vf',f'select=eq(n\\,{n})','-frames:v','1',png]);files.append(png)
            aa=np.array(Image.open(files[0]).convert('RGB'));bb=np.array(Image.open(files[1]).convert('RGB'));mask=np.ones((1080,1920),bool);mask[24:112,28:1512]=False
            delta=abs(aa.astype('int16')-bb.astype('int16'));outside=int(delta[mask].max());assert outside==0,('Unexpected non-heading pixel change',n,outside)
            Image.open(files[1]).resize((375,211),Image.Resampling.LANCZOS).save(L/f'after-{n:04d}-375.png')
            checks.append({'frame':n,'outsideHeadingPixelDifferenceMaximum':outside,'before':str(files[0]),'after':str(files[1])})
        save(L/'encoded-checks.json',{'outputSha256':sha(dest),'frames':534,'sampledPixelChecks':checks,'noAudio':True,'fps':'60/1','humanViewed':False})
    if args.adopt:
        checks=read(L/'encoded-checks.json');assert sha(dest)==checks['outputSha256']
        review=read(L/'visual-review.json');assert review['outputSha256']==checks['outputSha256']and review['sampledModelVisualReviewPassed']
        q=copy.deepcopy(r);q.update(id='A11-canonical-interpolation-heading',picture=str(dest),pictureSha256=sha(dest),sourceVerified=True)
        q['canonicalTermPatch']={'plan':str(L/'plan.json'),'encodedChecks':str(L/'encoded-checks.json'),'visualReview':str(L/'visual-review.json'),'title':'Interpolation (보간)'}
        patch=H/'visual-corrections/A11.json';assert not patch.exists()or read(patch).get('scope')=='canonical-first-heading-only'
        save(patch,{'episode':'A11','scope':'canonical-first-heading-only','readyForAssembly':True,'pictureEdits':[q],
            'originalSourcePreserved':True,'lengthChangeFrames':0,'audioChanged':False,'humanFinalReview':False})
    print(json.dumps({'plan':str(L/'plan.json'),'rendered':args.render,'adopted':args.adopt},ensure_ascii=False))
if __name__=='__main__':main()
