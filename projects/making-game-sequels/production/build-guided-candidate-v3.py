"""Splice only new approved guides into an inspection candidate; retain base PCM."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,math
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not WORK.exists(),'Preserve earlier candidates.'
old=read(BASE/'measured-edit-v2/plan.json');request=read(BASE/'guided-observation-tts-request-v3.json')
tts=read(BASE/'guided-observation-tts-execution-v3.json');review=read(BASE/'guided-observation-direct-review-v3.json')
assert tts['exitCode']==0 and len(tts['results'])==8 and review['allEightGuidesTechnicallyCompared']
guides={x['id']:{**next(g for g in request['guides'] if g['id']==x['id']),**x} for x in tts['results']}
for g in guides.values():assert sha(ROOT/g['path'])==g['sha256'] and g['sampleRate']==24000
bank=read(ROOT/old['sourcePlanningBank']);by_id={c['id']:c for c in bank['candidates']}
def bounds(c,a,z):
    c=copy.deepcopy(c);b=by_id[c['bankCutId']]
    assert b['localFrames']['startInclusive']<=a<z<=b['localFrames']['endExclusive']
    c.update(sourceStartFrame=a,sourceEndFrameExclusive=z,frames=round((z-a)/c['nativeFps']*60),nativeSeconds=(z-a)/c['nativeFps'],id=f'{c["sceneId"]}-p{c["paragraph"]}-action-{c["bankCutId"]}-{a}-{z}')
    c.update(finalApproved=False,captionPixelsApproved=False,mediaCompiled=False)
    return c
scenes=[];cursor=120;preservation=[];all_pauses=[]
for original in old['scenes']:
    sid=original['id'];s=copy.deepcopy(original)
    assert sha(ROOT/s['audio'])==s['audioSha256']
    for c in s['segments']:c['sceneId']=sid
    groups=[]
    if all(c['classification']=='explanation' for c in s['segments']):
        groups=[{'paragraphs':[1,2,3,4],'cuts':s['segments'],'guideIds':[]}]
    else:
        for p in range(1,5):
            if sid in ['08','10'] and p==4:continue
            cuts=[c for c in s['segments'] if c['paragraph']==p]
            groups.append({'paragraphs':[3,4] if sid in ['08','10'] and p==3 else [p],'cuts':cuts,'guideIds':[g['id'] for g in request['guides'] if g['parentScene']==sid and g['afterOriginalParagraph']==p]})
    gm={g['paragraphs'][0]:g for g in groups}
    if sid=='02':
        gm[2]['cuts']=[bounds(c,17400,c['sourceEndFrameExclusive']) if c['bankCutId']==10 else bounds(c,c['sourceStartFrame'],17220) if c['bankCutId']==9 else c for c in gm[2]['cuts']]
        gm[3]['cuts']=[bounds(c,17220,c['sourceEndFrameExclusive']) if c['bankCutId']==9 else c for c in gm[3]['cuts']]
        template=next(c for os in old['scenes'] for c in os['segments'] if c.get('bankCutId')==50)
        template={**template,'sceneId':'02','paragraph':3}
        gm[3]['cuts'].append(bounds(template,30420,30465))
        gm[4]['cuts']=[bounds(c,c['sourceStartFrame'],18076) if c['bankCutId']==12 else bounds(c,18150,18211) if c['bankCutId']==13 else c for c in gm[4]['cuts']]
    if sid=='13':
        gm[1]['cuts']=[bounds(c,c['sourceStartFrame'],30070) if c['bankCutId']==49 else c for c in gm[1]['cuts']]
        gm[2]['cuts']=[bounds(c,c['sourceStartFrame'],31190) if c['bankCutId']==51 and c['sourceStartFrame']==31020 else bounds(c,33720,c['sourceEndFrameExclusive']) if c['bankCutId']==57 else c for c in gm[2]['cuts']]
        gm[4]['cuts']=[bounds(c,c['sourceStartFrame'],31583) if c['bankCutId']==52 else c for c in gm[4]['cuts']]
    if sid=='12':
        # Keep the original conclusion last; this unique combat now has its own guide.
        tail=next(c for c in gm[4]['cuts'] if c['bankCutId']==40)
        gm[4]['cuts']=[c for c in gm[4]['cuts'] if c['bankCutId']!=40]
        gm[2]['cuts'].append({**tail,'paragraph':2,'id':'12-guide-combat-action-40-11760-12210'})
        gm[3]['cuts']=[bounds(c,c['sourceStartFrame'],9919) if c['bankCutId']==38 else c for c in gm[3]['cuts']]
        gm[4]['cuts']=[bounds(c,9919,c['sourceEndFrameExclusive']) if c['bankCutId']==38 else c for c in gm[4]['cuts']]
    output=0;placements=[];segments=[];speech=[];paragraph=0
    def pcm(kind,path,hashval,a,z,p,base=None,guide=None):
        global output
        placements.append({'kind':kind,'audio':path,'audioSha256':hashval,'fromSample':a,'toSample':z,'outputFromSample':output,'outputToSample':output+z-a,'paragraph':p,'originalParagraph':base,'guideId':guide})
        output+=z-a
    def pause(samples,reason):
        global output
        assert samples>=0,(sid,reason,samples)
        if samples:
            placements.append({'kind':'inserted-silence','samples':samples,'outputFromSample':output,'outputToSample':output+samples,'reason':reason,'classificationByVisibleSegment':True,'finalApproved':False})
            all_pauses.append({'scene':sid,'samples':samples,'seconds':samples/24000,'reason':reason})
            output+=samples
    for group in groups:
        before=output;cuts=group['cuts'];ps=group['paragraphs'];duration=sum(c['frames'] for c in cuts)*400
        for c in cuts:c.update(parentOriginalParagraph=ps[0],finalApproved=False,captionPixelsApproved=False)
        segments.extend(cuts)
        for bp in ps:
            p=original['speechEvidence'][bp-1];paragraph+=1
            pcm('preserved-current-PCM',s['audio'],s['audioSha256'],p['pcmFromSample'],p['pcmToSample'],paragraph,base=bp)
            speech.append({**p,'paragraph':paragraph,'originalParagraph':bp,'guideId':None,'audio':s['audio'],'audioSha256':s['audioSha256'],'asrEvidence':s['asrEvidence'],'outputSpeechFromSample':placements[-1]['outputFromSample'],'outputSpeechToSample':placements[-1]['outputToSample']})
        for gid in group['guideIds']:
            g=guides[gid]
            if gid=='06-g2':
                at=sum(c['frames'] for c in cuts[:4])*400
                pause(before+at-output,'Brief close-attack observation before switching explicitly to the separate preparation preview.')
            if gid=='13-g1':pause(43200,'Observe the approaching group for1.8s before the new guide; keep a short active observation on both sides rather than one long silent tail.')
            if gid=='13-g2':
                at=sum(c['frames'] for c in cuts[:3])*400
                pause(before+at-output,'Complete the nearby-attack observation before the distant-route guide begins on the next separate shot.')
            if gid=='13-g3':pause(before+duration-g['samples']-output,'Short normal-speed nearby attack observation; next guide spans the close-purple shot and the separate distant shot.')
            if gid=='12-g2':
                at=sum(c['frames'] for c in cuts[:-1])*400
                pause(before+at-output,'Complete the ReadyUp preparation preview before the separate high-view combat guide.')
            paragraph+=1
            pcm('new-guided-PCM',g['path'],g['sha256'],0,g['samples'],paragraph,guide=gid)
            asr_path=BASE/'asr-guided-observation-local-v3'/f'{gid}.json'
            speech.append({'paragraph':paragraph,'originalParagraph':None,'guideId':gid,'ko':g['text'],'en':g['en'],'pcmFromSample':0,'pcmToSample':g['samples'],'speechStart':0,'speechEnd':g['seconds'],'audio':g['path'],'audioSha256':g['sha256'],'asrEvidence':{'path':asr_path.relative_to(ROOT).as_posix(),'sha256':sha(asr_path)},'outputSpeechFromSample':placements[-1]['outputFromSample'],'outputSpeechToSample':placements[-1]['outputToSample'],'technicalGuideReview':review['reviewedAt']})
        pause(before+duration-output,'Short meaningful normal-speed observation of the stated action, or at most one frame of PCM endpoint quantization. Candidate requires final direct timing/pixel review.')
    local=0
    for c in segments:
        c.update(localFromFrame=local,startFrame=cursor+local,endFrameExclusive=cursor+local+c['frames'],seconds=c['frames']/60)
        local+=c['frames']
    assert output==local*400
    kept=[p for p in placements if p['kind']=='preserved-current-PCM']
    assert kept[0]['fromSample']==0 and kept[-1]['toSample']==s['samples']
    assert all(a['toSample']==b['fromSample'] for a,b in zip(kept,kept[1:]))
    assert sum(p['toSample']-p['fromSample'] for p in kept)==s['samples']
    preservation.append({'scene':sid,'audio':s['audio'],'sha256':s['audioSha256'],'allBaseSamplesPreserved':True,'newParagraphs':len(speech),'oldParagraphs':4})
    s.update(startFrame=cursor,endFrameExclusive=cursor+local,frames=local,segments=segments,pcmPlacement=placements,speechEvidence=speech,allBasePcmSamplesPreserved=True,baseCurrentPcmSeconds=original['currentPcmSeconds'],baseSamples=original['samples'],currentSpeechSamples=sum(p['toSample']-p['fromSample'] for p in placements if p['kind']!='inserted-silence'),currentPcmSeconds=original['currentPcmSeconds']+sum(g['seconds'] for g in guides.values() if g['parentScene']==sid))
    scenes.append(s);cursor+=local
actual=[c for s in scenes for c in s['segments'] if c['classification']=='actual-existing-game']
white=[c for s in scenes for c in s['segments'] if c['classification']=='explanation']
af=sum(c['frames'] for c in actual);wf=sum(c['frames'] for c in white)
assert af==20918 and wf==13945 and sum(len(s['speechEvidence']) for s in scenes)==60
for asset in bank['assets']:
    spans=sorted((c['sourceStartFrame'],c['sourceEndFrameExclusive'],c['id']) for c in actual if c['assetId']==asset['assetId'])
    assert all(a[1]<=b[0] for a,b in zip(spans,spans[1:])),asset['assetId']
assert abs(af-.6*(af+wf))<=1
omitted=[]
for b in bank['candidates']:
    numerator,denominator=b['nativeFrameRate'].split('/');fps=int(numerator)/int(denominator)
    a,z=b['localFrames']['startInclusive'],b['localFrames']['endExclusive']
    used=sorted((max(a,c['sourceStartFrame']),min(z,c['sourceEndFrameExclusive'])) for c in actual if c['assetId']==b['assetId'] and c['sourceEndFrameExclusive']>a and c['sourceStartFrame']<z)
    end=a
    for start,stop in used:
        if start>end:omitted.append({'bankId':b['id'],'assetId':b['assetId'],'startInclusive':end,'endExclusive':start,'seconds':[end/fps,start/fps],'reason':'Not assigned in current v3; neither looped nor stretched.'})
        end=max(end,stop)
    if end<z:omitted.append({'bankId':b['id'],'assetId':b['assetId'],'startInclusive':end,'endExclusive':z,'seconds':[end/fps,z/fps],'reason':'Not assigned in current v3; neither looped nor stretched.'})
joins=[]
for s in scenes:
    voiced=[p for p in s['pcmPlacement'] if p['kind']!='inserted-silence']
    for a,z in zip(voiced,voiced[1:]):
        joins.append({'scene':s['id'],'afterParagraph':a['paragraph'],'beforeParagraph':z['paragraph'],'fromAudio':a['audio'],'fromSourceEndSample':a['toSample'],'toAudio':z['audio'],'toSourceStartSample':z['fromSample'],'outputSamples':[a['outputToSample'],z['outputFromSample']],'insertedSilenceSamples':z['outputFromSample']-a['outputToSample'],'newGuideJoin':bool(a.get('guideId') or z.get('guideId')),'newJoinAsrApproved':False,'allPcmPreserved':True})
inputs={**old['inputs']}
for p in [BASE/'measured-edit-v2/plan.json',BASE/'guided-observation-tts-request-v3.json',BASE/'guided-observation-tts-execution-v3.json',BASE/'guided-observation-direct-review-v3.json']:
    inputs[p.relative_to(ROOT).as_posix()]=sha(p)
for s in scenes:
    for p in s['speechEvidence']:
        inputs[p['audio']]=p['audioSha256'];inputs[p['asrEvidence']['path']]=p['asrEvidence']['sha256']
plan={**old,'createdAt':datetime.now(timezone.utc).isoformat(),'status':'guided60-paragraph-v3-inspection-candidate-all-final-gates-pending','scenes':scenes,'actualFrames':af,'explanationFrames':wf,'bodyFrames':af+wf,'finalFrames':cursor+600,'finalSeconds':(cursor+600)/60,'allCurrentPcmSeconds':509.624+sum(g['seconds'] for g in guides.values()),'baseCurrentPcmSeconds':509.624,'newGuidePcmSeconds':sum(g['seconds'] for g in guides.values()),'preservationAudit':preservation,'briefObservationPauses':all_pauses,'guideReview':str((BASE/'guided-observation-direct-review-v3.json').relative_to(ROOT)).replace('\\','/'),'sourceAndCaptionTrialReview':'projects/making-game-sequels/production/measured-edit-v2/caption-and-tail-direct-review-v3.json','nativeCuts':len(actual),'unrelatedRailPillarUpwardCameraTrimmed':True,'conclusionLast':True,'allNewNativeEdgesApproved':False,'newJoinAsrApproved':False,'finalTimingApproved':False,'bodyRatioApproved':False,'allCaptionPixelsReviewed':False,'finalMixBuilt':False,'rendered':False,'qaApproved':False,'collected':False,'privateUploaded':False,'newGitImages':0}
plan.update(historicalV2SourceIntervalsOmitted=old['sourceIntervalsOmitted'],historicalV2QuietJoins=old['quietJoins'],historicalV2Inputs=old['inputs'],sourceIntervalsOmitted=omitted,quietJoins=joins,inputs=inputs)
WORK.mkdir();save(WORK/'plan.json',plan)
print(json.dumps({'scenes':13,'paragraphs':60,'actualFrames':af,'whiteFrames':wf,'seconds':plan['finalSeconds'],'newGuideSeconds':plan['newGuidePcmSeconds'],'currentVoiceSeconds':plan['allCurrentPcmSeconds'],'nativeCuts':len(actual),'finalApproved':False}))
