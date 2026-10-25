"""Prepare synchronized official comparison frames; preserve prior outputs and PCM."""
from pathlib import Path
import hashlib, json, subprocess
from PIL import Image

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
L = P / 'production/local/layered-comparison-v2'
S = R / 'production/batches/distinctive-ten-shorts-20261025/local/d2r-official/comparison'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def prepare():
    captions=read(P/'script/captions.json')
    assert captions['frames']==2620
    assert sha(P/'production/local/audio-v1/voice/narration.wav')=='9809f48b8a8dfbf0fc20c80e3f6c2acd4d7d8020ec1a3e69962e122f328d96be'
    sources={
      'tristram-old':('tristram_old_comparison_slider.mp4','21afb1cceabd9258acb7cdda8da513fb776356b64626ccd4fb38916a1897648f',322),
      'tristram-new':('tristram_new_comparison_slider.mp4','6584287286c16bbef1c44a088a14549195034d5097de78a02f7576f3fb11df0a',322),
      'barracks-old':('barracks_old_comparison_slider.mp4','3165c9b43c62f168d3b888d05176a2558478b03022c164c6b5b8825a0377eab2',360),
      'barracks-new':('barracks_new_comparison_slider.mp4','813ee8aefe64098ed1244115e004a43f619bff56856a191220880a7925323f35',360),
    }
    spec={'revision':'layered-comparison-v2','fps':60,'frames':2620,'nativeSpeed':1,'sourceStart':0,'crop':[240,240,1440,540],'decodedSource':[1920,1080],
          'builderSha256':sha(__file__),'captionsSha256':sha(P/'script/captions.json'),'sources':sources}
    fingerprint=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()
    base=L/'paired-frames'/fingerprint
    receipt=base/'receipt.json'
    if receipt.exists():
        previous=read(receipt)
        for row in previous['files']:
            q=base/row['path']
            assert q.exists() and sha(q)==row['sha256'],'Changed cached source frame'
        assert len(previous['files'])==1364
    else:
        # Incomplete attempts are preserved; retries never overwrite frames.
        base.mkdir(parents=True,exist_ok=True)
        attempts=sorted(base.glob('attempt-*'))
        work=base/f'attempt-{len(attempts)+1:03d}';work.mkdir()
        records=[]
        for key,(filename,digest,count) in sources.items():
            src=S/filename;assert sha(src)==digest
            probe=read_json_command(['ffprobe','-v','error','-show_streams','-of','json',str(src)])
            stream=next(x for x in probe['streams'] if x['codec_type']=='video')
            assert (stream['width'],stream['height'],stream['r_frame_rate'])==(1920,1080,'30/1')
            dest=work/key;dest.mkdir()
            subprocess.run(['ffmpeg','-v','error','-n','-threads','2','-i',str(src),'-vf','crop=1440:540:240:240,fps=60,scale=960:360:flags=lanczos',
              '-frames:v',str(count),'-start_number','0','-threads','1','-q:v','2',str(dest/'%05d.jpg')],check=True,cwd=R)
            files=sorted(dest.glob('*.jpg'));assert len(files)==count
            for i,q in enumerate(files):
                assert q.stem==f'{i:05d}'
                with Image.open(q) as im: im.load();assert im.size==(960,360)
                records.append({'path':q.relative_to(base).as_posix(),'sha256':sha(q)})
        save(receipt,{'spec':spec,'frameRoot':work.relative_to(P/'production/local').as_posix(),'files':records,'count':len(records),'validation':'Every JPEG decoded, dimensions and contiguous frame count checked'})
        previous=read(receipt)
    timing=read(P/'production/visual-timing.json')
    timing.update(revision='layered-comparison-v2',frameRoot=previous['frameRoot'],sourceReceipt=receipt.as_posix(),sourceReceiptSha256=sha(receipt),previewOnly=False)
    for section in timing['sections']:
        if section['id'] in ['game','confirm']:
            group='tristram' if section['id']=='game' else 'barracks'
            section['simultaneousSources']=[group+'-new',group+'-old']
            section['sourceStart']=0
            section['edit']='Official paired gameplay at matching source timestamps; top Resurrected / bottom Classic. Editorial comparison, not a filmed toggle.'
            section.pop('cuts',None)
    timing['reactions']=[{'start':40.15,'end':43.55,'kind':'relief'}]
    save(P/'production/layered-comparison-v2.json',timing)
    save(L/'preparation.json',{'fingerprint':fingerprint,'receipt':receipt.as_posix(),'frames':2620,'preparedSourceFrames':1364,'unchangedPcm':sha(P/'production/local/audio-v1/voice/narration.wav')})
    print(json.dumps({'frameRoot':previous['frameRoot'],'frames':2620,'preparedSourceFrames':1364}))

def read_json_command(args): return json.loads(subprocess.check_output(args,cwd=R))
if __name__=='__main__':prepare()
