"""Bind workflow highlights to actual recognized phrases, not guessed durations."""
import json,re,hashlib,math
from pathlib import Path
from assemble_documentary import PROJECT,load,save,digest,now
OUT=PROJECT/'production/local/workflow-v4';AUDIO=PROJECT/'production/local/audio-v4'
def norm(s):return re.sub(r'[^0-9a-z가-힣]','',s.lower())
QUERIES={
 '01-02':('workflow-overview',{'source':['출발점은'],'logic':['한쪽에서는'],'resources':['다른쪽에서는'],
    'agent':['이분석을바탕으로'],'assets':['새로운외형을'],'engine':['마지막으로'],'result':['직접조작할수있는']}),
 '02-01':('rea-role',{'agent':['에이전트는목표에맞춰'],'toolbox':['기존프로그램의파일과'],
    'inspect':['에이전트가어떤파일이'],'evidence':['목록을반환하고'],'verify':['그결과를읽은']}),
 '02-02':('workflow-overview',{'source':0,'logic':['기계어분석이'],'resources':['모델과애니메이션은'],
    'agent':0,'assets':['새외형을만들때는'],'engine':['완성한규칙과'],'result':['이제이번실험에서']}),
 '08-01':('actual-route',{'source':0,'rea':['게임의구조를찾고'],'script':['읽을수있는코드에서'],
    'code':['그규칙으로새코드를'],'models':['블렌더에서만든'],'engine':['고도엔진에','고도엔진의'],'result':['직접플레이할수있는']})}
def main():
    timing=load(AUDIO/'narration.timing.json');asr=load(AUDIO/'review/source-full-asr.timestamps.json')
    assert asr['audio_sha256']==digest(AUDIO/'narration.wav')
    items=timing['entries'];positions={f'{x["scene_id"]}-{x["paragraph"]:02}':(i,x) for i,x in enumerate(items)}
    # Preserve all old body cut frame counts. New edges absorb only sub-frame rounding.
    reuse_start=positions['02-03'][1]['start'];prefix_end=round(reuse_start*60)
    old=load(PROJECT/'production/local/revision-v3-inputs/timeline.json')
    body_frames=sum(b['frames'] for b in old['beats'] if 4<=int(b['id'][1:3])<=30)
    total=math.ceil(timing['duration_seconds']*60);closing_start=prefix_end+body_frames
    required=load(PROJECT/'production/local/documentary-v4/required-clips.json')
    boundaries={row['id']:row for row in required['newClips']}
    assert required['bodyFrames']==total and required['retainedBodyFrames']==body_frames
    result=[]
    thumbs={name:{'path':f'production/local/workflow-v4/{file}','sha256':digest(OUT/file),
            'reviewEvidence':'production/local/workflow-v4/thumbnail-review.json'}
            for name,file in [('original','original-still.png'),('prototype','prototype-still.png')]}
    for ident,(mode,queries) in QUERIES.items():
        i,p=positions[ident];start=round(p['start']*60) if ident!='08-01' else closing_start
        end=round(items[i+1]['start']*60) if i+1<len(items) else total
        if ident=='02-02':end=prefix_end
        # The edit wrapper checks every preserved body boundary and owns rounding.
        start=boundaries[ident]['startFrame'];end=start+boundaries[ident]['frames']
        local_origin=start/60; chars=''; times=[]
        for word in asr['chunks']:
            stamp=word.get('timestamp')
            if not stamp or stamp[0] is None:continue
            if stamp[0]<p['start']-.05 or stamp[0]>p['end']+.05:continue
            text=norm(word['text']);chars+=text;times.extend([float(stamp[0])]*len(text))
        cue={};evidence={}
        for key,options in queries.items():
            if isinstance(options,int):cue[key]=options;evidence[key]={'method':'existing context visible at paragraph start','absoluteFrame':start};continue
            hit=next(((chars.find(norm(q)),q) for q in options if norm(q) in chars),None)
            if hit is None:raise ValueError(f'Missing inspected phrase {ident}/{key}: {options}. ASR={chars}')
            at,phrase=hit;absolute=times[at];cue[key]=max(0,absolute-local_origin)
            evidence[key]={'method':'actual ASR word onset for verified phrase','phrase':phrase,'absoluteSeconds':absolute,
              'asrSha256':digest(AUDIO/'review/source-full-asr.timestamps.json')}
        result.append({'id':ident,'mode':mode,'durationSeconds':(end-start)/60,'frames':end-start,
          'speechEndSeconds':min(p['end'],(items[i+1]['start'] if i+1<len(items) else timing['duration_seconds']))-local_origin,
          'timingVerified':True,'cueTimes':cue,'cueEvidence':evidence,'thumbnails':thumbs,'bodyStartFrame':start})
    save(OUT/'timings.json',{'schemaVersion':1,'kind':'measured-workflow-v4-timings','createdAt':now(),
      'sourceWavSha256':asr['audio_sha256'],'sourceAsrSha256':digest(AUDIO/'review/source-full-asr.timestamps.json'),
      'entries':result,'priorBodyFramesPreserved':body_frames,'totalBodyFrames':total})
    print(json.dumps([{'id':x['id'],'frames':x['frames'],'cues':x['cueTimes']} for x in result],ensure_ascii=False))
if __name__=='__main__':main()
