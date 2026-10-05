"""Assemble lossless inspection PCM with byte-identical base/new components."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v4'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dest=WORK/'inspection-pcm';assert not dest.exists();dest.mkdir()
plan=read(WORK/'plan.json');rows=[];cache={}
for s in plan['scenes']:
    out=np.zeros(s['frames']*400,dtype='int16');checks=[]
    for p in s['pcmPlacement']:
        if p['kind']=='inserted-silence':continue
        assert sha(ROOT/p['audio'])==p['audioSha256']
        if p['audio'] not in cache:
            pcm,rate=sf.read(ROOT/p['audio'],dtype='int16');assert rate==24000 and pcm.ndim==1;cache[p['audio']]=pcm
        piece=cache[p['audio']][p['fromSample']:p['toSample']]
        assert len(piece)==p['outputToSample']-p['outputFromSample']
        out[p['outputFromSample']:p['outputToSample']]=piece
        checks.append({'kind':p['kind'],'paragraph':p['paragraph'],'guideId':p['guideId'],'source':p['audio'],'sourceSamples':[p['fromSample'],p['toSample']],'outputSamples':[p['outputFromSample'],p['outputToSample']],'identical':np.array_equal(piece,out[p['outputFromSample']:p['outputToSample']])})
    path=dest/(s['id']+'.wav');sf.write(path,out,24000,subtype='PCM_16');back,rate=sf.read(path,dtype='int16');assert rate==24000 and np.array_equal(out,back)
    rows.append({'scene':s['id'],'audio':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'samples':len(out),'sampleRate':24000,'seconds':len(out)/24000,'allComponentsSampleIdentical':True,'checks':checks,'finalMix':False})
save(WORK/'inspection-pcm-index-v4.json',{'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'planSha256':sha(WORK/'plan.json'),'kind':'voice-only-inspection-PCM-no-BGM-no-final-mix-approval','scenes':rows,'all554_584SpeechSecondsPreserved':True,'finalMixBuilt':False,'newJoinAsrApproved':False,'humanWholeListening':'pending'})
contexts=[]
for sid,fromp,top in [('02',4,5),('06',4,6),('13',1,2),('13',3,5),('12',2,4),('12',4,6)]:
    s=next(x for x in plan['scenes'] if x['id']==sid);r=next(x for x in rows if x['scene']==sid)
    ps=[p for p in s['speechEvidence'] if fromp<=p['paragraph']<=top]
    contexts.append({'id':f'{sid}-p{fromp}-p{top}-current-join','audio':r['audio'],'audioSha256':r['sha256'],'fromSample':ps[0]['outputSpeechFromSample'],'toSample':ps[-1]['outputSpeechToSample'],'sampleRate':24000,'expectedKo':' '.join(p['ko'] for p in ps),'paragraphs':list(range(fromp,top+1)),'guideIds':[p['guideId'] for p in ps if p.get('guideId')],'technicalReview':False})
assert len(set(g for c in contexts for g in c['guideIds']))==8
inputs=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [WORK/'plan.json',BASE.parent/'script/narration.ko.json',BASE.parent/'script/narration.en.json',BASE/'narration-guided60-index-v3.json']]
save(BASE/'guided-joins-readback-request-v4.json',{'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'contexts':contexts,'protectedInputs':inputs,'expectedTextIsRecognizerPrompt':False,'finalMixApproved':False})
print(json.dumps({'scenes':13,'componentsIdentical':True,'newJoinContexts':6,'coveredGuides':8,'finalMixBuilt':False}))
