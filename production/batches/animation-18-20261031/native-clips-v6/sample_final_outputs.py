"""Check exact recap splices and sample the encoded captions at desktop/mobile size."""
import argparse
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image,ImageDraw
from prepare import HERE,ROOT,WORK,OUTPUT,read,save
from finish_episode import sha


def frame(path,n):
    raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-threads','2','-ss',f'{n/60:.9f}',
         '-i',str(path),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
    assert len(raw)==1920*1080*3
    return Image.frombytes('RGB',(1920,1080),raw)


def main(ep):
    delivery=read(OUTPUT/ep/'delivery.json')
    selected=next(r for r in read(HERE/'plan.json')['episodes'] if r['id']==ep)
    base=selected['baseline']
    files={r['kind']:r for r in delivery['files']}
    master=Path(files['captioned.mp4']['path'])
    prior=ROOT/next(r['path'] for r in base['files'] if r['kind']=='captioned.mp4')
    body_review=WORK/ep/'native-picture-review.json'
    if ep!='A06' and body_review.is_file():
        reviewed=read(body_review)
        assert reviewed['visualReviewPassed']
        prior=Path(reviewed['pictures']['captioned.mp4']['path'])
        assert sha(prior)==reviewed['pictures']['captioned.mp4']['sha256']
    assert sha(master)==files['captioned.mp4']['sha256']
    folder=WORK/ep/'encoded-final-check';folder.mkdir(parents=True,exist_ok=True)
    at=base['frames']-600
    cut=files['captioned.mp4'].get('pictureSplice',{}).get('copiedOriginalFrames',at-120)
    evidence=[]
    for n in (cut-1,cut,cut+1,at-1,at+600):
        new=np.asarray(frame(master,n),dtype=np.float32)
        old=np.asarray(frame(prior,n if n<at else n-600),dtype=np.float32)
        error=float(np.mean(abs(new-old)))
        assert error<3.0,(ep,n,'GOP or insertion boundary differs from preserved picture',error)
        evidence.append({'frame':n,'originalFrame':n if n<at else n-600,'meanAbsolutePixelError':error})
    contact=Image.new('RGB',(1500,600),'#080c0a')
    for j,delta in enumerate((0,90,390)):
        image=frame(master,at+delta)
        path=folder/f'summary-{delta:03}.png';image.save(path)
        mobile=folder/f'summary-{delta:03}-375.png';image.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
        contact.paste(image.resize((500,281)),(j*500,0))
        contact.paste(Image.open(mobile),(j*500+62,315))
    contact.save(folder/'summary-contact.jpg')
    audio=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-ss',str(at/60),'-i',str(master),
                '-t','10','-vn','-ar','48000','-ac','2','-f','f32le','-'])
    reference=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(WORK/ep/'assembly/summary-decoded.wav'),
                '-vn','-ar','48000','-ac','2','-f','f32le','-'])
    a=np.frombuffer(audio,dtype='<f4');b=np.frombuffer(reference,dtype='<f4')
    assert len(a)==len(b)==960000
    a,b=a[4800:-4800].astype('float64'),b[4800:-4800].astype('float64')
    similarity=float(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b)))
    assert similarity>.97,(ep,'Encoded recap audio mismatch',similarity)
    save(folder/'evidence.json',{'episode':ep,'captionedMasterSha256':files['captioned.mp4']['sha256'],
        'boundaryFrames':evidence,'encodedSummaryAudioSimilarity':similarity,'summaryFrames':600,
        'visualReviewPending':True,'humanReviewed':False})
    print(ep,'boundary and encoded audio checks passed',round(similarity,5),folder/'summary-contact.jpg',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('episodes',nargs='+')
    for ep in p.parse_args().episodes:main(ep)
