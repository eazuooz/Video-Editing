"""Replace selected pictures and sentences while keeping the existing body clock."""
import argparse
from pathlib import Path
import subprocess
import sys

from prepare import BATCH,HERE,ROOT,WORK,read,save
from finish_episode import ff,sha,VENC,timestamp
from assemble_delivery import srt


def audio_and_captions(ep,base,folder,prior):
    import numpy as np
    import soundfile as sf
    original=Path('C:/Users/1/Videos/YamyamProduction/animation-review-notes-20261110')/ep/'finish/narration-mix.wav'
    assert original.is_file()
    records=[r for r in read(WORK/'narration-patches-checked.json')['records'] if r['episode']==ep]
    if not records:
        return original, {lang:prior[lang+'.srt'] for lang in ('ko','en')}, []
    pcm,rate=sf.read(original,dtype='float32',always_2d=True)
    assert rate==48000 and pcm.shape[1]==2
    before=pcm.copy();modified=np.zeros(len(pcm),dtype=bool)
    music_path=ROOT/'projects'/base['slug']/'production/local/series-v1/music.wav'
    music,music_rate=sf.read(music_path,dtype='float32',always_2d=True)
    assert music_rate==rate and music.shape[1]==2
    evidence=[]
    for r in records:
        assert sha(Path(r['audioFile']))==r['audioSha256']
        normalized=folder/(r['id']+'-normalized.wav')
        ff('-i',r['audioFile'],'-af','loudnorm=I=-18:TP=-3:LRA=7,aresample=48000',
           '-ar',48000,'-ac',1,'-c:a','pcm_f32le',normalized)
        voice,_=sf.read(normalized,dtype='float32')
        a,b=round(r['start']*rate),round(r['end']*rate)
        at=round(r['voiceAt']*rate)
        assert at>=a and at+len(voice)<=b
        bed=music[np.arange(a,b)%len(music)].copy()
        bed[at-a:at-a+len(voice)]+=voice[:,None]
        assert np.max(np.abs(bed))<1,(ep,r['id'],'new sentence clips')
        fade=min(240,len(bed)//4)
        w=np.linspace(0,1,fade)[:,None]
        bed[:fade]=before[a:a+fade]*(1-w)+bed[:fade]*w
        bed[-fade:]=bed[-fade:]*(1-w)+before[b-fade:b]*w
        pcm[a:b]=bed;modified[a:b]=True
        evidence.append(dict(r,replaceStartSample=a,replaceEndSample=b))
    assert np.array_equal(pcm[~modified],before[~modified])
    target=folder/'voice-patched.wav'
    sf.write(target,pcm,rate,subtype='FLOAT')
    captions={}
    for lang in ('ko','en'):
        old=srt(prior[lang+'.srt'])
        keep=[q for q in old if not any(q[0]<r['end'] and q[1]>r['start'] for r in records)]
        new=srt(WORK/ep/'patch-captions'/('captions.'+lang+'.srt'))
        combined=sorted(keep+new)
        assert all(x[1]<=y[0]+.002 for x,y in zip(combined,combined[1:])),(ep,lang,'caption overlap')
        dest=folder/(lang+'.srt')
        dest.write_text(''.join(f'{i}\n{timestamp(a)} --> {timestamp(b)}\n{t}\n\n' for i,(a,b,t) in enumerate(combined,1)),encoding='utf-8')
        captions[lang]=dest
    save(folder/'narration-change-evidence.json',{'episode':ep,'originalPcm':str(original),'originalPcmSha256':sha(original),
        'newPcm':str(target),'newPcmSha256':sha(target),'outsideChangedSentencesUnchanged':True,
        'speechTimeCompressed':False,'replacements':evidence})
    return target,captions,records


def main(ep):
    base=next(r['baseline'] for r in read(HERE/'plan.json')['episodes'] if r['id']==ep)
    assert ep in read(ROOT/'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']['episodes']
    folder=WORK/ep/'body';folder.mkdir(parents=True,exist_ok=True)
    prior={r['kind']:ROOT/r['path'] for r in base['files']}
    for r in base['files']:assert sha(ROOT/r['path'])==r['sha256']
    sys.path.insert(0,str(BATCH/'contrast-v5/review-notes-20261110'))
    import finish_review
    finish_review.MEDIA=WORK
    finish_review.VISUAL_REVISIONS={ep}
    clean=finish_review.make_picture(base,prior['clean.mp4'],folder,folder/'body.log')
    audio,captions,changes=audio_and_captions(ep,base,folder,prior)
    # Preserve the prior caption geometry, colour emphasis and all untouched cues.
    # The lower 180 pixels of explanation layouts are reserved for this exact strip.
    filters='[1:v]crop=1920:180:0:900[cap];[0:v][cap]overlay=0:900[v0]'
    if changes:
        chain='[v0]'
        for r in changes:
            chain+=f"drawbox=x=0:y=900:w=1920:h=180:color=0x080c0a:t=fill:enable='between(t,{r['start']},{r['end']})',"
        ass=(WORK/ep/'patch-captions/captions.ko.ass').as_posix().replace(':','\\:')
        chain+="ass='"+ass+"'[v]"
        filters+=';'+chain
    else:filters+=';[v0]null[v]'
    captioned=folder/'picture-captioned.mp4'
    ff('-threads',2,'-i',clean,'-threads',2,'-i',prior['captioned.mp4'],'-filter_complex',filters,
       '-map','[v]','-an','-frames:v',base['frames'],*VENC,captioned)
    for movie in (clean,captioned):ff('-threads',2,'-i',movie,'-f','null','NUL')
    save(WORK/ep/'native-picture-review.json',{'episode':ep,'visualReviewPassed':False,
        'status':'encoded-native-body-awaiting-moving-sample-inspection',
        'pictures':{kind:{'path':str(movie),'sha256':sha(movie)} for kind,movie in [('clean.mp4',clean),('captioned.mp4',captioned)]},
        'audioPcm':str(audio),'captions':{k:str(v) for k,v in captions.items()},
        'bodyFrameCount':base['frames'],'changedSentenceCount':len(changes),'fullDecode':'passed',
        'outsideChangedSentencesUnchanged':True,'humanReviewed':False})
    print(ep,'native body assembled; encoded visual inspection required.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('episode');main(p.parse_args().episode)
