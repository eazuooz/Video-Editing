"""Exact lecture40:60 plan from preserved baseline and current aligned new audio.

No footage loops, freezes or slow motion. Extra observation time is inserted
only at measured quiet sentence seams using the unchanged shared placer.
"""
from pathlib import Path
import json,sys,math,hashlib,copy,argparse
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision/planes'
sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
from observations import observation_capacity_seconds,place_observation_pauses,mapped_time,source_group_capacity_seconds,place_source_group_pauses
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def stamp(t):
    h,rest=divmod(round(t*1000),3600000);mi,rest=divmod(rest,60000);s,ms=divmod(rest,1000)
    return f'{h:02}:{mi:02}:{s:02},{ms:03}'
def srt(cues):return '\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(cues,1))+'\n'
flow=read(B/'planes-episode-flow-audit.json');assert flow['allOriginalSceneDictionariesExact'] and flow['originalOrderAndContractExact']
timing=read(O/'combined-addition-timing.json');old=read(B/'baselines/game-math-planes-barycentric/production/timeline.json')
old_by_id={s['id']:s for s in old['scenes']}
original_wav=ROOT/'shared/output/game-math-planes-barycentric/narration-final.wav'
original_sha=hashlib.sha256(original_wav.read_bytes()).hexdigest()
original_audio,sr=sf.read(original_wav,dtype='float32');assert sr==24000 and original_audio.ndim==1
parser=argparse.ArgumentParser();parser.add_argument('--only',choices=[e['slug'] for e in flow['episodes']]);parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
summaries=[]
for episode in flow['episodes']:
    if args.only and episode['slug']!=args.only:continue
    slug=episode['slug'];P=ROOT/'projects'/slug;m=read(P/'project.json');lesson=read(P/'production/lesson.json')
    missing=[s['id'] for s in lesson['scenes'] if s['id'] not in old_by_id and s['id'] not in timing]
    if missing:raise RuntimeError(f'{slug}: current-hash passing alignment still required for '+','.join(missing))
    rows=[];raw={};minimum={};maximum={};groups={'actual':[],'explanation':[]}
    for scene in lesson['scenes']:
        ident=scene['id'];kind=scene['kind'];groups[kind].append(ident)
        if ident in old_by_id:
            base=old_by_id[ident];assert scene['ko']=={s['id']:s for s in read(B/'baselines/game-math-planes-barycentric/lesson.json')['scenes']}[ident]['ko']
            a=original_audio[round(base['start']*sr):round((base['start']+base['seconds'])*sr)]
            assert len(a)==round(base['seconds']*sr)
            slot={'id':ident,'title':scene['title'],'classification':kind,'preservedOriginal':True,'frames':base['frames'],'seconds':base['seconds'],'lineStarts':base['lineStarts'],'cues':copy.deepcopy(base['cues']),'baselineStart':base['start'],'baselineClip':f'shared/output/game-math-planes-barycentric/clips/{ident}.mp4','baselineAudioSha256':original_sha,'preservedSamplesSha256':hashlib.sha256(a.tobytes()).hexdigest()}
            if kind=='actual':slot['cut']=copy.deepcopy(base['cut'])
            raw[ident]=a;minimum[ident]=maximum[ident]=base['frames']
            slot['captions']={lang:[{**c,'start':c['start']-base['start'],'end':c['end']-base['start']} for c in old[lang+'Captions'] if c['scene']==ident] for lang in ['ko','en']}
        else:
            t=copy.deepcopy(timing[ident]);wav=ROOT/t['voice'];assert hashlib.sha256(wav.read_bytes()).hexdigest()==t['voiceSha256']
            a,rate=sf.read(wav,dtype='float32');assert rate==sr and a.ndim==1
            minimum[ident]=math.ceil((len(a)/sr+.6)*60);maximum[ident]=minimum[ident]
            slot={**t,'title':scene['title'],'classification':kind,'preservedOriginal':False,'cues':[{'start':x,'end':y,'line':i,'text':scene['ko'][i]} for i,(x,y) in enumerate(zip(t['lineStarts'],t['lineEnds']))]}
            raw[ident]=a
            if kind=='actual':
                segments=[{'in':x,'maxSeconds':y-x} for x,y in scene['intervals']]
                if scene.get('segmentSourceIds'):
                    assert len(scene['segmentSourceIds'])==len(segments)
                    for seg,source_id in zip(segments,scene['segmentSourceIds']):
                        seg['sourceId']=source_id
                        seg['sourceFile']=('shared/output/game-math-part2-teaching-revision/sources/' if source_id=='TPkvx2W8CV8' else 'shared/output/game-math-part2-full-series/sources/')+source_id+'.mp4'
                group_lines=scene.get('sourceGroupStartsAtLines')
                if group_lines:
                    assert len(group_lines)==len(segments)
                    for seg,line in zip(segments,group_lines):
                        if line is not None:seg['startsAtLine']=line
                sentence_cues=slot['sentenceCues']
                capacity=source_group_capacity_seconds(a,sr,slot['cues'],segments,sentence_cues=sentence_cues) if group_lines else observation_capacity_seconds(a,sr,sentence_cues)
                maximum[ident]=min(math.floor(scene['maximumSeconds']*60),math.floor(capacity*60))
                assert minimum[ident]<=maximum[ident],f'{ident}: secure more clear footage or useful narration, not speed changes'
                slot['cut']={'sourceId':scene['sourceId'],'sourceFile':('shared/output/game-math-part2-teaching-revision/sources/' if scene['sourceId']=='TPkvx2W8CV8' else 'shared/output/game-math-part2-full-series/sources/')+scene['sourceId']+'.mp4','sourceSegments':segments,'maximumSeconds':scene['maximumSeconds'],'sourceAudioUsed':False,'sourceSpeed':1,'annotationPlan':scene['annotation']}
        rows.append(slot)
    min_actual=sum(minimum[i] for i in groups['actual']);min_explanation=sum(minimum[i] for i in groups['explanation'])
    body=math.ceil((min_explanation/.6)/5)*5
    print(json.dumps({'slug':slug,'minimumActualSeconds':min_actual/60,'minimumExplanationSeconds':min_explanation/60,'actualTargetSeconds':round(body*.4)/60,'usefulExplanationRequiredSeconds':max(0,(min_actual*1.5-min_explanation)/60),'sourceMaximumSeconds':sum(maximum[i] for i in groups['actual'])/60}),flush=True)
    assert min_actual<=round(body*.4),f'{slug}: new gameplay voice exceeds40% around the preserved useful explanations; tighten only new repetition or add necessary explained calculations, never static padding'
    targets={'actual':int(body*.4),'explanation':int(body*.6)}
    print(json.dumps({'slug':slug,'actualMinimumSeconds':min_actual/60,'actualMaximumSeconds':sum(maximum[i] for i in groups['actual'])/60,'actualTargetSeconds':targets['actual']/60,'newActualSlots':[{'id':i,'min':minimum[i]/60,'max':maximum[i]/60} for i in groups['actual'] if i not in old_by_id]}),flush=True)
    assert sum(maximum[i] for i in groups['actual'])>=targets['actual'],f'{slug}: actual capacity {sum(maximum[i] for i in groups["actual"])/60:.2f}s below exact target {targets["actual"]/60:.2f}s; add clear concept-matched source and useful narration'
    frames=minimum.copy()
    for kind in groups:
        for _ in range(targets[kind]-sum(frames[i] for i in groups[kind])):
            available=[i for i in groups[kind] if i not in old_by_id and (kind=='explanation' or frames[i]<maximum[i])]
            assert available,'Original timing must remain intact; acquire useful new material'
            ident=min(available,key=lambda i:frames[i]/minimum[i]);frames[ident]+=1
    assert sum(frames.values())==body
    if args.dry_run:continue
    voice=np.zeros(round((body/60+12)*sr),dtype='float32');start=2;captions={'ko':[],'en':[]}
    for slot in rows:
        ident=slot['id'];slot.update(start=start,frames=frames[ident],seconds=frames[ident]/60)
        a=raw[ident];pauses=[]
        if not slot['preservedOriginal'] and slot['classification']=='actual':
            if any('startsAtLine' in seg for seg in slot['cut']['sourceSegments']):
                a,pauses,review,source_groups=place_source_group_pauses(a,sr,slot['cues'],slot['seconds'],slot['cut']['sourceSegments'],sentence_cues=slot['sentenceCues'])
            else:
                a,pauses,review=place_observation_pauses(a,sr,slot['sentenceCues'],slot['seconds']);source_groups=None
            slot['observationPauses']=pauses;slot['observationReview']=review
            slot['lineStarts']=[mapped_time(x,pauses) for x in slot['lineStarts']]
            slot['cues']=[{**c,'start':mapped_time(c['start'],pauses),'end':mapped_time(c['end'],pauses)} for c in slot['cues']]
            segments=[]
            for group in source_groups or [{'frames':slot['frames'],'segments':slot['cut']['sourceSegments']}]:
                remaining=group['frames']
                for seg in group['segments']:
                    count=min(remaining,math.floor(seg['maxSeconds']*60));remaining-=count
                    if count:segments.append({**seg,'frames':count,'seconds':count/60,'sourceGroupStartsAtLine':group.get('startsAtLine')})
                assert remaining==0
            assert sum(seg['frames'] for seg in segments)==slot['frames'];slot['cut']['segments']=segments
        at=round(start*sr);assert len(a)<=round(slot['seconds']*sr)
        voice[at:at+len(a)]=a
        for lang in captions:
            for c in slot['captions'][lang]:captions[lang].append({**c,'start':start+mapped_time(c['start'],pauses),'end':start+mapped_time(c['end'],pauses),'scene':ident})
        start+=slot['seconds']
    assert abs(start+10-(body/60+12))<1e-8
    for lang in captions:
        assert all(a['end']<=b['start']+.004 for a,b in zip(captions[lang],captions[lang][1:])), 'Caption overlap after insertions'
        (P/f'script/final.{lang}.srt').write_text(srt(captions[lang]),encoding='utf8')
    assert [(c['start'],c['end']) for c in captions['ko']]==[(c['start'],c['end']) for c in captions['en']]
    narration_path=ROOT/m['paths']['narration'];narration_path.parent.mkdir(parents=True,exist_ok=True)
    sf.write(narration_path,voice,sr)
    timeline={'fps':60,'frames':body+720,'seconds':body/60+12,'bodyFrames':body,'bodySeconds':body/60,'actualFrames':targets['actual'],'explanationFrames':targets['explanation'],'actualShare':.4,'explanationShare':.6,'ratioErrorFrames':0,'introSeconds':2,'outroSeconds':10,'backgroundMusic':False,'sourceAudioUsed':False,'scenes':rows,'koCaptions':captions['ko'],'enCaptions':captions['en'],'baselineAudioSha256':original_sha,'newSourcePixelAndListeningApproval':False}
    write(P/'production/timeline.json',timeline)
    m['video']['durationSeconds']=timeline['seconds'];m['editing'].update(timingStatus='measured-preserved-audio-and-current-hash-alignment; pixels pending',actualGameplaySeconds=targets['actual']/60,actualExplanationSeconds=targets['explanation']/60,actualGameplayShare=.4)
    m['editing']['finalBodyFrames']={'total':body,'actual':targets['actual'],'explanation':targets['explanation'],'ratioErrorFrames':0}
    write(P/'project.json',m)
    summaries.append({'slug':slug,'seconds':timeline['seconds'],'actualSeconds':targets['actual']/60,'explanationSeconds':targets['explanation']/60,'preservedOriginalScenes':len(episode['originalIds']),'captionCount':len(captions['ko'])})
assert hashlib.sha256(original_wav.read_bytes()).hexdigest()==original_sha
if not args.dry_run:write(B/'planes-measured-episode-plan.json',{'episodes':summaries,'originalAudioUnchanged':True,'newRenderAndPublishingComplete':False})
print(json.dumps(summaries))
