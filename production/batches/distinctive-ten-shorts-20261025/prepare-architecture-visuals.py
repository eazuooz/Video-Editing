"""PCM-bound frames with fully verified immutable attempts; no jobs run on import."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, uuid
from PIL import Image

R=Path(__file__).resolve().parents[3]
B=Path(__file__).parent
SLUGS=['shorts-d2r-renderer-logic-separation','shorts-d2r-controller-input-adapter']

def read(p): return json.loads(Path(p).read_text(encoding='utf8'))
def encoded(v): return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(p):
    with Path(p).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def fingerprint(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')).hexdigest()
def write_new(p,content):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as stream: stream.write(content)
def publish_preserving(p,v,history):
    content=encoded(v)
    if p.exists():
        old=p.read_bytes()
        if old==content: return
        snapshot=history/(hashlib.sha256(old).hexdigest()+'.json')
        if snapshot.exists():
            if snapshot.read_bytes()!=old: raise RuntimeError('History differs; preserve all files: '+str(snapshot))
        else: write_new(snapshot,old)
    temporary=p.with_name(p.name+'.'+uuid.uuid4().hex+'.partial')
    write_new(temporary,content)
    os.replace(temporary,p)

def inspect_frames(attempt,sections,dimensions):
    records=[]
    for section in sections:
        count,name=section['frames'],section['id'];directory=attempt/name
        expected=[f'{i:05d}.jpg' for i in range(count)]
        actual=sorted(p.name for p in directory.iterdir()) if directory.is_dir() else []
        if actual!=expected: raise RuntimeError('Frame sequence is not exact and contiguous: '+str(directory))
        files=[]
        for filename in expected:
            p=directory/filename
            with Image.open(p) as picture:
                if picture.format!='JPEG' or picture.size!=dimensions: raise RuntimeError('Invalid frame: '+str(p))
                picture.load()  # JPEG verify() alone does not decode the payload.
            files.append(dict(name=filename,bytes=p.stat().st_size,sha256=sha(p)))
        records.append(dict(id=name,frames=count,files=files))
    return records

def verified_attempt(attempt,input_id,inputs,sections,dimensions):
    p=attempt/'receipt.json'
    if not p.is_file(): return None
    try:
        receipt=read(p)
        if (receipt.get('status')!='complete' or receipt.get('inputFingerprint')!=input_id
            or receipt.get('inputs')!=inputs or receipt.get('sections')!=sections
            or receipt.get('dimensions')!=list(dimensions)): return None
        if receipt.get('frameFiles')!=inspect_frames(attempt,sections,dimensions): return None
        return receipt
    except (OSError,ValueError,RuntimeError): return None

def ensure_frames(base,inputs,sections,dimensions,extract):
    input_id=fingerprint(inputs);family=base/input_id;family.mkdir(parents=True,exist_ok=True)
    for attempt in sorted(family.glob('attempt-*')):
        if attempt.is_dir():
            receipt=verified_attempt(attempt,input_id,inputs,sections,dimensions)
            if receipt: return attempt,receipt,True
    number=1
    while True:
        attempt=family/f'attempt-{number:04d}'
        try: attempt.mkdir();break
        except FileExistsError: number+=1
    write_new(attempt/'inputs.json',encoded(inputs))
    for section in sections: (attempt/section['id']).mkdir()
    extract(attempt)
    records=inspect_frames(attempt,sections,dimensions)
    receipt=dict(kind='native-speed-architecture-source-frames',status='complete',inputFingerprint=input_id,
                 inputs=inputs,sections=sections,dimensions=list(dimensions),frameFiles=records,
                 fpsConversion='60fps source unchanged; 30fps comparison duplicated at60 without slowdown',
                 movingPlaybackReview='pending',audioListening='pending')
    write_new(attempt/'receipt.json',encoded(receipt))
    return attempt,receipt,False

def prepare(slug,actual):
    p=R/'projects'/slug
    auth=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['explicit-ten-distinctive-shorts-20261025']
    if not (auth.get('status')=='active' and auth.get('fullProductionAuthorized') and slug in auth.get('slugs',[])):
        raise RuntimeError('Finite project authorization changed.')
    plan=read(p/'planning/production-plan.json')
    if not (plan.get('scriptFinalized') and plan.get('independentFootageViewed') and plan.get('directReview')):
        raise RuntimeError('Inspect source and finalize script before preparation.')
    script_path=p/'script/narration.spoken.ko.json';spec_path=p/'production/section-plan.json';source_record=p/'sources/selected-footage.json'
    lines=read(script_path)['scenes'][0]['lines'];spec=read(spec_path);captions=None;voice_inputs=None
    if actual:
        voice_path=p/'production/local/audio-v1/voice/narration.wav';voice_timing_path=voice_path.with_suffix('.timing.json');caption_path=p/'script/captions.json'
        voice=read(voice_timing_path);captions=read(caption_path);voice_sha=sha(voice_path)
        if (captions.get('revision')!='distinctive-ten-v1' or captions['timingInputs']['voiceSha256']!=voice_sha
            or voice.get('voiceSha256')!=voice_sha or captions['timingInputs']['narrationSha256']!=sha(script_path)
            or captions['timingInputs']['clausesSha256']!=sha(p/'script/clauses.json')):
            raise RuntimeError('Actual PCM, script, clauses and timing hashes disagree.')
        offset=float(captions['voiceOffsetSeconds']);entries=[dict(start=float(r['start'])+offset,end=float(r['end'])+offset) for r in voice['entries']]
        entries[0]['start']=0;frames=int(captions['frames']);duration=frames/60
        if captions.get('fps')!=60 or abs(duration-float(captions['durationSeconds']))>1e-8:
            raise RuntimeError('Actual caption frame count differs from duration.')
        voice_inputs=dict(voiceSha256=voice_sha,voiceTimingSha256=sha(voice_timing_path),captionsSha256=sha(caption_path),captionTimingInputs=captions['timingInputs'])
    else:
        entries=[];end=0
        for line in lines:
            seconds=max(4,len(line)/7.0);entries.append(dict(start=end,end=end+seconds));end+=seconds+.28
        frames=round((entries[-1]['end']+.35)*60);duration=frames/60
    if len(entries)!=len(spec): raise RuntimeError('Paragraph and section counts differ.')
    sections=[]
    for i,s in enumerate(spec):
        start=round(entries[i]['start']*60);end=round(entries[i+1]['start']*60) if i+1<len(entries) else frames
        if not 0<=start<end<=frames: raise RuntimeError('Invalid paragraph interval.')
        row=dict(**s,start=start/60,end=end/60,startFrame=start,endFrame=end)
        # Only six source seconds were inspected. Longer speech continues on its diagram.
        if row['kind']=='game' and end-start>360:
            boundary=start+360
            sections.extend([{**row,'endFrame':boundary,'end':boundary/60},
                             {**row,'id':row['id']+'-explain','kind':'diagram','startFrame':boundary,'start':boundary/60}])
        else: sections.append(row)
    renderer=slug.endswith('logic-separation')
    config=dict(topic='renderer' if renderer else 'controller',head=['그래픽을 바꿨는데','전투는 그대로?'] if renderer else ['마우스로 만들었는데','패드는 어떻게?'])
    timing=dict(revision='distinctive-ten-v1',previewOnly=not actual,frames=frames,durationSeconds=duration,sections=sections,sources={},
                cues=captions['cues'] if actual else [],reactions=[dict(kind='realize',start=.2,end=min(2.7,sections[0]['end']))])
    source_records={r['path']:r for r in read(source_record)['sources']}
    media=B/'local/d2r-official';source_inputs={};jobs=[]
    def register(key,source,audio):
        path=source.relative_to(R).as_posix();record=source_records.get(path);digest=sha(source)
        if not record or digest!=record.get('sha256') or (record.get('width'),record.get('height'))!=(1920,1080):
            raise RuntimeError('Current source differs from inspected FHD source: '+path)
        timing['sources'][key]=dict(path=path,sourceSHA256=digest,originalOffsetSeconds=0,nativeAudioAdopted=audio)
        if audio: timing['sources'][key]['audioListening']='pending'
        source_inputs[path]=dict(path=path,sha256=digest,bytes=source.stat().st_size)
    for s in sections:
        if s['kind']!='game': continue
        count=s['endFrame']-s['startFrame']
        if count>360: raise RuntimeError('Inspect more source before extending this interval.')
        if renderer:
            pair='tristram' if s['id']=='game' else 'barracks';cursor=0;s['cuts']=[]
            for index,variant in enumerate(('old','new')):
                segment=count//2 if index==0 else count-count//2
                if not segment: continue
                source=media/'comparison'/f'{pair}_{variant}_comparison_slider.mp4';start=cursor/60;key=pair+'-'+variant
                register(key,source,False)
                s['cuts'].append(dict(source=key,sourceStart=start,sourceEnd=start+segment/60,start=s['start']+cursor/60,end=s['start']+(cursor+segment)/60,rate=1,nativeAudioAdopted=False))
                jobs.append(dict(section=s['id'],source=key,sourceStart=start,startNumber=cursor,frames=segment));cursor+=segment
            s.update(source=pair+'-old',nativeAudioAdopted=False,edit='editorial old/new comparison, not live keypress capture')
        else:
            key='launch-pc';register(key,media/'D2R_Launch_Broll_.mp4',True)
            jobs.append(dict(section=s['id'],source=key,sourceStart=23,startNumber=0,frames=count))
            s.update(source=key,sourceStart=23,sourceEnd=23+count/60,rate=1,nativeAudioAdopted=True)
    expected=[dict(id=s['id'],frames=s['endFrame']-s['startFrame']) for s in sections if s['kind']=='game']
    inputs=dict(schemaVersion=2,slug=slug,actual=actual,builderSha256=sha(Path(__file__)),narrationSha256=sha(script_path),
                sectionPlanSha256=sha(spec_path),sourceRecordSha256=sha(source_record),actualVoice=voice_inputs,
                sourceFiles=sorted(source_inputs.values(),key=lambda r:r['path']),timing=timing,jobs=jobs,
                decoder=subprocess.run(['ffmpeg','-version'],check=True,capture_output=True,text=True).stdout.splitlines()[0],
                decodeSettings=dict(fps=60,jpegQuality=3,dimensions=[1920,1080]))
    def extract(attempt):
        for job in jobs:
            source=R/timing['sources'][job['source']]['path']
            subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(job['sourceStart']),'-i',str(source),'-vf','fps=60',
                            '-frames:v',str(job['frames']),'-start_number',str(job['startNumber']),'-threads','1','-q:v','3','-n',
                            str(attempt/job['section']/'%05d.jpg')],check=True)
    attempt,receipt,reused=ensure_frames(p/'production/local/game-frames',inputs,expected,(1920,1080),extract)
    timing['frameRoot']=attempt.relative_to(p/'production/local').as_posix()
    timing['inputFingerprint']=receipt['inputFingerprint']
    timing['frameReceipt']=(attempt/'receipt.json').relative_to(p/'production/local').as_posix()
    history=p/'production/local/timing-history'
    publish_preserving(p/'production/visual-config.json',config,history)
    publish_preserving(p/'production/visual-timing.json',timing,history)
    publish_preserving(p/'production/local/visual-timing.json',timing,history)
    return dict(slug=slug,frames=frames,frameRoot=timing['frameRoot'],reusedFrames=reused,inputFingerprint=receipt['inputFingerprint'],timing='actual' if actual else 'preview-only')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--actual',action='store_true');parser.add_argument('--slug',choices=SLUGS);args=parser.parse_args()
    for slug in [args.slug] if args.slug else SLUGS: print(json.dumps(prepare(slug,args.actual),ensure_ascii=False),flush=True)
if __name__=='__main__': main()
