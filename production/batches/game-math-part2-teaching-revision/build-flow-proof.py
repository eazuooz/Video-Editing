"""Internal narrated/captioned continuity QA only, ineligible for publication."""
from pathlib import Path
import json,math,importlib.util,hashlib
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision/flow-proof';O.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('caption_tools',ROOT/'projects/game-math-polar-sample/production/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.BASE=O;b.WORK=O;b.MF=O/'proof.json'
original_ff=b.ff
def ff(args,log=None):
    args=[str(x) for x in args]
    for i,arg in enumerate(args[:-1]):
        if arg=='-threads':args[i+1]='2'
    return original_ff(args,log)
b.ff=ff
t=b.read(ROOT/'shared/output/game-math-part2-teaching-revision/combined-addition-timing.json');baseline=b.read(B/'baselines/game-math-quaternion-operations/production/timeline.json')
old=next(s for s in baseline['scenes'] if s['id']=='03');oldwav=ROOT/'shared/output/game-math-quaternion-operations/narration-final.wav';oldsha=b.sha(oldwav);oldaudio,sr=sf.read(oldwav,dtype='float32');assert sr==24000
items=[('B03',ROOT/'shared/output/game-math-part2-teaching-revision/caption-safe-v2/videos/bridges/1080p60/B03.mp4'),('N03',ROOT/'shared/output/game-math-part2-teaching-revision/caption-safe-v2/videos/supplements/1080p60/N03.mp4'),('03',ROOT/'shared/output/game-math-quaternion-operations/clips/03.mp4')]
captions={'ko':[],'en':[]};timeline=[];parts=[];clips=[];start=0
for ident,source in items:
    if ident=='03':
        frames=old['frames'];audio=oldaudio[round(old['start']*sr):round((old['start']+old['seconds'])*sr)]
        cues={lang:[{**c,'start':c['start']-old['start'],'end':c['end']-old['start']} for c in baseline[lang+'Captions'] if c['scene']=='03'] for lang in captions}
    else:
        slot=t[ident];assert b.sha(ROOT/slot['voice'])==slot['voiceSha256'];audio,rate=sf.read(ROOT/slot['voice'],dtype='float32');assert rate==sr
        frames=math.ceil(slot['seconds']*60);cues=slot['captions']
    video=next(v for v in b.probe(source)['streams'] if v['codec_type']=='video');assert int(video['nb_frames'])>=frames-1
    target=O/(ident+'.mp4');b.ff(['-i',source,'-vf','fps=60,setsar=1,tpad=stop_mode=clone:stop_duration=0.05','-frames:v',str(frames),*b.ENC,target],ident+'-encode.log')
    assert next(v for v in b.probe(target)['streams'] if v['codec_type']=='video')['nb_frames']==str(frames)
    padded=np.zeros(round(frames/60*sr),dtype='float32');padded[:len(audio)]=audio;parts.append(padded);clips.append(target)
    for lang in captions:
        for c in cues[lang]:captions[lang].append({**c,'start':start+c['start'],'end':start+c['end'],'scene':ident})
    timeline.append({'id':ident,'start':start,'seconds':frames/60,'frames':frames,'baselineSceneExact':ident=='03'});start+=frames/60
voice=O/'narration.wav';sf.write(voice,np.concatenate(parts),sr)
b.write(O/'concat.txt','\n'.join("file '"+p.as_posix()+"'" for p in clips)+'\n')
clean=O/'flow-proof-clean.mp4';captioned=O/'flow-proof-captioned.mp4'
b.ff(['-f','concat','-safe','0','-i',O/'concat.txt','-i',voice,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(start),'-movflags','+faststart',clean],'proof-clean.log')
b.write(b.MF,{'standaloneUploadAllowed':False,'status':'internal-continuity-proof; not full lecture','paths':{'videoClean':b.rel(clean),'videoBurnedCaptions':b.rel(captioned)}})
b.write(O/'production/timeline.json',{'frames':sum(s['frames'] for s in timeline),'seconds':start,'scenes':timeline,'koCaptions':captions['ko'],'enCaptions':captions['en']})
for lang in captions:b.write(O/f'script/final.{lang}.srt',b.srt(captions[lang]))
b.burn();b.ff(['-v','error','-i',captioned,'-map','0:v:0','-map','0:a:0','-f','null','NUL'],'full-decode.log')
assert b.sha(oldwav)==oldsha
b.write(O/'qa.json',{'fullDecodePassed':True,'frames':sum(s['frames'] for s in timeline),'seconds':start,'originalAudioUnchanged':True,'scene03Exact':True,'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'directMovingPixelReview':'pending','humanListening':'pending','notACompletedLecture':True,'standaloneUploadAllowed':False})
b.write(O/'index.html','''<!doctype html><meta charset="utf-8"><title>기초 설명과 기존 장면의 연결 검토</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}</style><h1>평면 회전의 질문 → 세 성분의 의미 → 기존 계산</h1><button onclick="document.getElementById('flow').play()">연결 구간 재생</button><video id="flow" controls muted src="flow-proof-captioned.mp4"></video>''')
print(json.dumps({'seconds':start,'captionedProof':b.rel(captioned),'fullLectureComplete':False}))
