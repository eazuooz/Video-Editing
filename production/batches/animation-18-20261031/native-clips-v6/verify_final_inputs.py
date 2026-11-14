"""Bind final masters to the exact reviewed body, recap pictures and narration."""
import argparse,subprocess
from pathlib import Path
import numpy as np
from prepare import HERE,ROOT,WORK,OUTPUT,read,save
from finish_episode import sha
from sample_final_outputs import frame

def payload(movie,count):
    return subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(movie),'-map','0:v:0','-an',
        '-frames:v',str(count),'-c:v','copy','-bsf:v','filter_units=remove_types=6|7|8|9',
        '-f','hash','-hash','sha256','-']).decode().strip()

def audio(movie,at,duration):
    raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-threads','2','-ss',str(at),'-i',str(movie),
        '-t',str(duration),'-vn','-ar','48000','-ac','2','-f','f32le','-'])
    return np.frombuffer(raw,dtype='<f4').astype('float64')

def main(ep):
    selected=next(r for r in read(HERE/'plan.json')['episodes'] if r['id']==ep)
    path=OUTPUT/ep/'delivery.json';delivery=read(path);files={r['kind']:r for r in delivery['files']}
    reviewed=read(WORK/ep/'native-picture-review.json') if ep!='A06' else None
    pictures=reviewed['pictures'] if reviewed else {f['kind']:{'path':str(ROOT/f['path']),'sha256':f['sha256']} for f in selected['baseline']['files'] if f['kind'].endswith('.mp4')}
    pcm=Path(reviewed['audioPcm']) if reviewed and reviewed.get('audioPcm') else Path(delivery['sourcePcm'])
    prefix=[]
    for kind in ('clean.mp4','captioned.mp4'):
        assert sha(Path(pictures[kind]['path']))==pictures[kind]['sha256']
        cut=files[kind].get('pictureSplice',{}).get('copiedOriginalFrames')
        if cut:
            first=payload(files[kind]['path'],cut);second=payload(pictures[kind]['path'],cut)
            assert first==second,(ep,kind,'Final body is not the exact reviewed encoded prefix')
            prefix.append({'kind':kind,'copiedFrames':cut,'reviewedVclPayloadHash':first})
    master=Path(files['captioned.mp4']['path']);at=round(delivery['summaryAt']*60)
    recap=[]
    for n in (0,90,390):
        a=np.asarray(frame(master,at+n),dtype=np.float32)
        b=np.asarray(frame(WORK/ep/'assembly/summary-captioned.mp4',n),dtype=np.float32)
        error=float(np.mean(abs(a-b)));assert error<3,(ep,n,error)
        recap.append({'frame':n,'meanAbsolutePixelError':error})
    windows=[(3.,1.),(min(30.,delivery['summaryAt']-3),1.),(delivery['summaryAt']-1.5,1.)]
    windows += [(r['voiceAt']+.10,min(1.5,r['voiceSeconds']-.12)) for r in read(WORK/'narration-patches-checked.json')['records'] if r['episode']==ep]
    proof=[]
    for start,length in windows:
        a,b=audio(master,start,length),audio(pcm,start,length)
        assert len(a)==len(b)
        energy=float(np.dot(b,b))
        similarity=float(np.dot(a,b)/np.sqrt(np.dot(a,a)*energy)) if energy>1e-8 else None
        if similarity is None:assert float(np.max(abs(a)))<.003
        else:assert similarity>.97,(ep,start,'Final narration does not match the reviewed PCM',similarity)
        proof.append({'at':start,'seconds':length,'similarity':similarity})
    summary=read(WORK/ep/'assembly/summary-components.json')
    evidence={'episode':ep,'captionedMasterSha256':files['captioned.mp4']['sha256'],'bodyPictures':pictures,
        'prefixIdentity':prefix,'recapPictureErrors':recap,'reviewedNarrationWindows':proof,
        'sourcePcmSha256':sha(pcm),'humanReviewed':False}
    save(WORK/ep/'final-input-identity.json',evidence)
    delivery.update(bodyPictures=pictures,sourcePcmSha256=sha(pcm),
        bodyReviewSignature=reviewed.get('configurationSignature') if reviewed else None,
        summaryPictureSha256=sha(Path(summary['cleanPicture'])),summaryAudioSha256=sha(Path(summary['audio'])),
        inputIdentityEvidence=str(WORK/ep/'final-input-identity.json'))
    save(path,delivery);print(ep,'exact reviewed body, recap and narration identity passed.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('episodes',nargs='+')
    for ep in p.parse_args().episodes:main(ep)
