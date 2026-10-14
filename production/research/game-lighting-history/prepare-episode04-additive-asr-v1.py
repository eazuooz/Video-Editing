"""Prepare measured 24 whole/24 splice-context windows after successful TTS.

Only an unmixed review assembly is produced. Every byte of the current87 PCM,
including its silence, is retained exactly. No final timing/QA is approved.
"""
from pathlib import Path
import datetime, hashlib, json, os, wave

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
REQUEST=BASE/'additive-asr-selected-request-v4.json'
EXECUTION=BASE/'additive-tts-selected-execution-v2.json'
PLAN=BASE/'additive-asr-plan-v1.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,j):
    p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+'.writing-'+str(os.getpid()))
    t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def rel(p):return p.relative_to(ROOT).as_posix()
def wav(p):
    with wave.open(str(p),'rb') as f:
        fmt=(f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getcomptype())
        count=f.getnframes();raw=f.readframes(count)
    if fmt!=(1,2,24000,'NONE') or len(raw)!=count*2:
        raise RuntimeError('Expected exact mono PCM16/24k: '+str(p))
    return raw,count

def main():
    if PLAN.exists():raise RuntimeError('Existing assembly/ASR plan preserved')
    request=read(REQUEST);execution=read(EXECUTION)
    if execution.get('generationComplete') is not True or execution.get('exitCode')!=0:
        raise RuntimeError('24 successful generation results required')
    history=read(ROOT/'shared/output/gpu-handoff'/f"{execution['leaseToken']}.json")
    if history.get('state')!='research_resume_verified':
        raise RuntimeError('Actual original research restoration required before CPU ASR preparation')
    for x in request['protectedInputs']:
        if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Reviewed input changed: '+x['path'])
    if len(execution['results'])!=24 or any(x['technicalTailGatePassed'] is not True for x in execution['results']):
        raise RuntimeError('All24 technical tail records required; ASR approval remains separate')
    original=read(BASE/'current-unmixed-assembly-v4.json');timing=read(ROOT/original['timing']['path'])
    en=read(ROOT/'projects/game-lighting-history-04/script/narration.en.json')
    raw,total=wav(ROOT/original['audio']['path']);sr=24000
    if sha(ROOT/original['audio']['path'])!=original['audio']['sha256'] or total!=30429121:
        raise RuntimeError('Original approved current87 PCM changed')
    insertions=[];inputs=[]
    for s in request['scenes']:
        result=next(x for x in execution['results'] if x['id']==s['id'])
        p=ROOT/s['path'];data,n=wav(p)
        if sha(p)!=result['sha256'] or n!=result['samples']:raise RuntimeError('New take changed: '+s['id'])
        when,line=s['position'].split('-line-');entry=next(e for e in timing['entries'] if e['scene_id']==s['originalScene'] and e['paragraph']==int(line))
        boundary=round(entry['start' if when=='before' else 'end']*sr)
        insertions.append(dict(boundary=boundary,scene=s,data=data,samples=n,result=result))
        inputs.append(dict(path=rel(p),sha256=sha(p)))
    insertions.sort(key=lambda x:(x['boundary'],x['scene']['id']))
    pieces=[];audit=[];newentries=[];cursor=0;output_cursor=0
    for item in insertions:
        stop=item['boundary']
        if stop<cursor:raise RuntimeError('Insertion order regression')
        if stop>cursor:
            part=raw[cursor*2:stop*2];pieces.append(part)
            audit.append(dict(kind='preserved-original',sourceSampleRange=[cursor,stop],currentSampleRange=[output_cursor,output_cursor+stop-cursor],pcm16Sha256=hashlib.sha256(part).hexdigest(),byteIdentical=True))
            output_cursor+=stop-cursor;cursor=stop
        s=item['scene'];n=item['samples'];pieces.append(item['data'])
        newentries.append(dict(id=s['id'],kind=s['kind'],originalScene=s['originalScene'],position=s['position'],text=s['text'],en=s['en'],sourcePath=s['path'],sourceSha256=item['result']['sha256'],startSample=output_cursor,endSample=output_cursor+n,start=output_cursor/sr,end=(output_cursor+n)/sr))
        audit.append(dict(kind='new-addition',id=s['id'],sourceSampleRange=[0,n],currentSampleRange=[output_cursor,output_cursor+n],pcm16Sha256=hashlib.sha256(item['data']).hexdigest(),byteIdentical=True))
        output_cursor+=n
    if cursor<total:
        part=raw[cursor*2:];pieces.append(part);audit.append(dict(kind='preserved-original',sourceSampleRange=[cursor,total],currentSampleRange=[output_cursor,output_cursor+total-cursor],pcm16Sha256=hashlib.sha256(part).hexdigest(),byteIdentical=True));output_cursor+=total-cursor
    combined=b''.join(pieces)
    restored=b''.join(combined[x['currentSampleRange'][0]*2:x['currentSampleRange'][1]*2] for x in audit if x['kind']=='preserved-original')
    if restored!=raw:raise RuntimeError('Original87 full PCM byte preservation failed')
    entries=[]
    for e in timing['entries']:
        first=round(e['start']*sr);last=round(e['end']*sr)
        # At a shared boundary, insert-before shifts the following start while
        # insert-after does not extend the preceding paragraph's end.
        start=first+sum(x['samples'] for x in insertions if x['boundary']<=first)
        end=last+sum(x['samples'] for x in insertions if x['boundary']<last)
        if end-start!=last-first:raise RuntimeError('An addition splits an original paragraph')
        entries.append(dict(id='original-'+e['scene_id']+'-'+str(e['paragraph']),kind='preserved-original',originalScene=e['scene_id'],paragraph=e['paragraph'],text=e['text'],en=next(s for s in en['scenes'] if s['id']==e['scene_id'])['lines'][e['paragraph']-1],startSample=start,endSample=end,start=start/sr,end=end/sr))
    entries=sorted(entries+newentries,key=lambda x:x['startSample'])
    folder=ROOT/'shared/output/narration/game-lighting-history-04/additive-review-v1'
    folder.mkdir(parents=True,exist_ok=True);audio=folder/'game-lighting-history-04-additive-unmixed-review-v1.wav'
    if audio.exists():raise RuntimeError('Existing review media preserved')
    with wave.open(str(audio),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(combined)
    audio_record=dict(path=rel(audio),sha256=sha(audio),sampleRate=sr,samples=output_cursor,durationSeconds=output_cursor/sr)
    jobs=[]
    for e in newentries:
        p=ROOT/e['sourcePath'];r=next(x for x in execution['results'] if x['id']==e['id'])
        jobs.append(dict(label='whole-'+e['id'],mode='whole',audio=dict(path=rel(p),sha256=sha(p)),sourceSampleRange=[0,r['samples']],expectedKo=[e['text']],expectedEn=[e['en']],targetId=e['id']))
    for e in newentries:
        i=next(i for i,x in enumerate(entries) if x['id']==e['id']);context=entries[max(0,i-1):min(len(entries),i+2)]
        jobs.append(dict(label='context-'+e['id'],mode='context',audio=audio_record,sourceSampleRange=[context[0]['startSample'],context[-1]['endSample']],expectedKo=[x['text'] for x in context],expectedEn=[x['en'] for x in context],targetId=e['id'],contextEntryIds=[x['id'] for x in context],scope='Complete neighboring paragraphs across actual additive PCM splice; sequential recognition without recognizer text prompt.'))
    write(BASE/'additive-unmixed-review-assembly-v1.json',dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),audio=audio_record,originalAudio=original['audio'],entries=entries,pcmAudit=audit,original87FullPcmByteIdentical=True,original87ParagraphsPreserved=True,newParagraphs=24,reviewAssemblyOnly=True,finalTimingApproved=False,wholeNewAsrApproved=False,independentContextsApproved=False,finalMixedAsrApproved=False,humanWholeListeningApproved=False,finalVideoProduced=False))
    write(PLAN,dict(schemaVersion=1,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),audio=audio_record,inputs=[*inputs,dict(path=rel(REQUEST),sha256=sha(REQUEST)),dict(path=rel(EXECUTION),sha256=sha(EXECUTION))],jobs=jobs,cpuThreads=2,gpuJobs=0,expectedTextUsedAsPrompt=False,allDirectlyReviewed=False,finalMixedAsr=False))
    print(json.dumps(dict(windows=len(jobs),newParagraphs=24,originalParagraphs=87,durationSeconds=output_cursor/sr,finalTimingApproved=False)))

if __name__=='__main__':main()
