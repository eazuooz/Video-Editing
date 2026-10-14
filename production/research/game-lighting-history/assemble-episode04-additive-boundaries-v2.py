"""Reassemble review-only PCM at measured, explicitly reviewed quiet boundaries.

Does not change the running v1 recognizer's media, plan, results or session.
All original87 samples and all24 selected takes are copied byte-for-byte.
"""
from pathlib import Path
import datetime,hashlib,json,os,wave
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def record(p):return dict(path=rel(p),sha256=sha(p))
def write(p,j):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.writing-'+str(os.getpid()))
    tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
def pcm(p):
    with wave.open(str(p),'rb') as f:
        if (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getcomptype())!=(1,2,24000,'NONE'):raise RuntimeError('PCM24k format changed')
        n=f.getnframes();raw=f.readframes(n)
    if len(raw)!=n*2:raise RuntimeError('Incomplete PCM')
    return raw,n
def main():
    destination=BASE/'additive-unmixed-review-assembly-v2.json';plan_path=BASE/'additive-context-plan-v2.json'
    if destination.exists() or plan_path.exists():raise RuntimeError('Existing v2 assembly and plan preserved')
    review_path=BASE/'additive-splice-boundary-review-v2.json';review=read(review_path)
    if not review['all24TechnicalBoundariesReadyForReviewReassembly']:raise RuntimeError('Explicit measured splice review required')
    for item in [review['originalAudio'],review['anchors'],review['gapMeasurements'],review['selectedRequest']]:
        if sha(ROOT/item['path'])!=item['sha256']:raise RuntimeError('Reviewed input changed: '+item['path'])
    anchors=read(ROOT/review['anchors']['path']);gaps=read(ROOT/review['gapMeasurements']['path']);request=read(ROOT/review['selectedRequest']['path'])
    generation_path=BASE/'additive-tts-selected-execution-v2.json';generation=read(generation_path)
    if generation.get('exitCode')!=0 or not generation['generationComplete'] or not generation['original24TakeFilesPreserved']:raise RuntimeError('Successful selected24 and preserved original takes required')
    old_path=BASE/'additive-unmixed-review-assembly-v1.json';old=read(old_path)
    if sha(ROOT/old['audio']['path'])!=old['audio']['sha256']:raise RuntimeError('Historical v1 review audio changed')
    old_frozen=[record(p) for p in [old_path,BASE/'additive-asr-plan-v1.json']]
    original,total=pcm(ROOT/review['originalAudio']['path']);sr=24000
    if total!=30429121:raise RuntimeError('Original87 complete PCM required')
    original_entries=[]
    en=read(ROOT/'projects/game-lighting-history-04/script/narration.en.json')
    for chapter in anchors['chapters']:
        first,last=chapter['currentOriginalSampleRange'];bounds=[first]
        for left,right in zip(chapter['paragraphs'],chapter['paragraphs'][1:]):
            gap=next(r for r in gaps['records'] if r['leftId']==left['id'])
            # No addition is made at22 paragraph1/2. Its label boundary only
            # uses the observed-word midpoint; it is never an audio splice.
            boundary=gap['candidates'][0]['middleSample'] if gap['candidates'] else first+round(sum(gap['asrGapSeconds'])/2*sr)
            bounds.append(boundary)
        bounds.append(last)
        for i,p in enumerate(chapter['paragraphs']):
            original_entries.append(dict(id=p['id'],kind='preserved-original',originalScene=chapter['scene'],paragraph=p['paragraph'],text=p['text'],en=next(s for s in en['scenes'] if s['id']==chapter['scene'])['lines'][p['paragraph']-1],originalSampleRange=[bounds[i],bounds[i+1]],actualSpokenOriginalSeconds=p['originalMasterSpokenSeconds'],recognition=chapter['recognition'],wordIndices=p['wordIndices'],legacyEstimatedAllocation=p['legacyAllocationSeconds']))
    if len(original_entries)!=87:raise RuntimeError('All87 original paragraphs required')
    insertions=[]
    for s in request['scenes']:
        cut=next(c for c in review['cuts'] if c['id']==s['id']);result=next(r for r in generation['results'] if r['id']==s['id'])
        path=ROOT/s['path'];raw,n=pcm(path)
        if sha(path)!=result['sha256'] or n!=result['samples'] or not result['technicalTailGatePassed']:raise RuntimeError('Selected current take changed: '+s['id'])
        original_entry=next(e for e in original_entries if e['originalScene']==s['originalScene'] and e['paragraph']==int(s['position'].split('-line-')[1]))
        boundary=original_entry['originalSampleRange'][0 if s['position'].startswith('before-') else 1]
        if boundary!=cut['selectedOriginalBoundarySample']:raise RuntimeError('Explicit sample choice differs from original paragraph boundary')
        insertions.append(dict(boundary=boundary,scene=s,raw=raw,samples=n,sha256=result['sha256']))
    insertions.sort(key=lambda x:(x['boundary'],x['scene']['id']))
    pieces=[];audit=[];newentries=[];source_cursor=0;out_cursor=0
    for x in insertions:
        stop=x['boundary']
        if stop>source_cursor:
            part=original[source_cursor*2:stop*2];pieces.append(part)
            audit.append(dict(kind='preserved-original',sourceSampleRange=[source_cursor,stop],currentSampleRange=[out_cursor,out_cursor+stop-source_cursor],pcm16Sha256=hashlib.sha256(part).hexdigest(),byteIdentical=True))
            out_cursor+=stop-source_cursor;source_cursor=stop
        s=x['scene'];pieces.append(x['raw']);n=x['samples']
        newentries.append(dict(id=s['id'],kind=s['kind'],originalScene=s['originalScene'],position=s['position'],text=s['text'],en=s['en'],sourcePath=s['path'],sourceSha256=x['sha256'],startSample=out_cursor,endSample=out_cursor+n,start=out_cursor/sr,end=(out_cursor+n)/sr))
        audit.append(dict(kind='new-addition',id=s['id'],sourceSampleRange=[0,n],currentSampleRange=[out_cursor,out_cursor+n],pcm16Sha256=hashlib.sha256(x['raw']).hexdigest(),byteIdentical=True));out_cursor+=n
    if source_cursor<total:
        part=original[source_cursor*2:];pieces.append(part);audit.append(dict(kind='preserved-original',sourceSampleRange=[source_cursor,total],currentSampleRange=[out_cursor,out_cursor+total-source_cursor],pcm16Sha256=hashlib.sha256(part).hexdigest(),byteIdentical=True));out_cursor+=total-source_cursor
    combined=b''.join(pieces)
    if b''.join(combined[r['currentSampleRange'][0]*2:r['currentSampleRange'][1]*2] for r in audit if r['kind']=='preserved-original')!=original:raise RuntimeError('Original87 full PCM bytes changed')
    for x in insertions:
        r=next(r for r in audit if r.get('id')==x['scene']['id'])
        if combined[r['currentSampleRange'][0]*2:r['currentSampleRange'][1]*2]!=x['raw']:raise RuntimeError('Selected addition PCM changed')
    for entry in original_entries:
        first,last=entry['originalSampleRange'];start=first+sum(x['samples'] for x in insertions if x['boundary']<=first);end=last+sum(x['samples'] for x in insertions if x['boundary']<last)
        if end-start!=last-first:raise RuntimeError('New addition splits a measured original paragraph')
        entry.update(startSample=start,endSample=end,start=start/sr,end=end/sr)
    entries=sorted(original_entries+newentries,key=lambda e:e['startSample'])
    if len(entries)!=111 or out_cursor!=40330563:raise RuntimeError('Complete111 duration changed')
    folder=ROOT/'shared/output/narration/game-lighting-history-04/additive-review-v2';audio=folder/'game-lighting-history-04-additive-unmixed-review-v2.wav'
    if audio.exists():raise RuntimeError('Existing review media preserved')
    folder.mkdir(parents=True,exist_ok=True)
    with wave.open(str(audio),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(combined)
    audio_record=dict(path=rel(audio),sha256=sha(audio),sampleRate=sr,samples=out_cursor,durationSeconds=out_cursor/sr)
    jobs=[]
    for target in newentries:
        index=next(i for i,e in enumerate(entries) if e['id']==target['id'])
        left=next((i for i in range(index-1,-1,-1) if entries[i]['kind']=='preserved-original'),None)
        right=next((i for i in range(index+1,len(entries)) if entries[i]['kind']=='preserved-original'),None)
        if left is None or right is None:raise RuntimeError('Complete original neighboring paragraphs required')
        context=entries[left:right+1]
        jobs.append(dict(label='context-v2-'+target['id'],mode='context',audio=audio_record,sourceSampleRange=[context[0]['startSample'],context[-1]['endSample']],expectedKo=[e['text'] for e in context],expectedEn=[e['en'] for e in context],targetId=target['id'],contextEntryIds=[e['id'] for e in context],scope='Complete original paragraphs on both sides, including adjacent additions. Measured quiet PCM cuts; sequential recognition without expected text prompt.'))
    if len(jobs)!=24:raise RuntimeError('Exactly24 corrected independent contexts required')
    for frozen in old_frozen:
        if sha(ROOT/frozen['path'])!=frozen['sha256']:raise RuntimeError('Running v1 frozen input changed')
    write(destination,dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),audio=audio_record,originalAudio=review['originalAudio'],entries=entries,pcmAudit=audit,boundaryReview=record(review_path),historicalV1=record(old_path),historicalV1Audio=old['audio'],original87FullPcmByteIdentical=True,new24SelectedPcmByteIdentical=True,paragraphs=111,reviewAssemblyOnly=True,originalWholeAsrRepeated=False,newWholeAsrRepeated=False,allCorrectedIndependentContextsApproved=False,finalTimingApproved=False,finalMixedAsrApproved=False,humanWholeListeningApproved=False,finalVideoProduced=False))
    write(plan_path,dict(schemaVersion=2,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),audio=audio_record,inputs=[record(destination),record(review_path),record(generation_path)],jobs=jobs,cpuThreads=2,gpuJobs=0,previousExecution=record(BASE/'additive-asr-execution-v1.json'),original87AsrRepeated=False,new24WholeAsrRepeated=False,allDirectlyReviewed=False,finalMixedAsr=False))
    print(json.dumps(dict(audio=audio_record,paragraphs=111,contexts=len(jobs),original87FullPcmByteIdentical=True,new24SelectedPcmByteIdentical=True,finalTimingApproved=False)))
if __name__=='__main__':main()
