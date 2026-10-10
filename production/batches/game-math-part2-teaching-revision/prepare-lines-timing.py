"""Merge current-hash new audio; retakes supersede v2 without deleting its files.

The unchanged93% gate is for timing only. Raw transcript/numeric meaning,
ending quality, moving pixels and listening remain separate review records.
"""
from pathlib import Path
import json,sys,hashlib,re,importlib.util
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
sys.argv=[sys.argv[0],'game-math-lines-bounds-teaching-additions-v2']
sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
spec=importlib.util.spec_from_file_location('revision_alignment',ROOT/'production/batches/game-math-part2-full-series/align.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
import soundfile as sf
original_normalized=mod.normalized
def normalized(s):
    # The explicitly defined alphabet C may be transcribed as Latin C.
    # This is pronunciation equivalence, never a numeral/sign substitution.
    return original_normalized(re.sub(r'(?<![가-힣])씨(?=\s|[,.;:]|는|를|이고|의|입니다|$)','c',s))
mod.normalized=normalized;mod.a.normalized=normalized
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
combined={};pending=[];rejected=[]
for slug,name in [('game-math-lines-bounds-teaching-additions-v2','lines-addition-tts-map.json'),('game-math-lines-narration-retakes-v3','lines-retake-tts-map-v3.json'),('game-math-lines-opening-retake-v4','lines-opening-tts-map-v4.json'),('game-math-lines-numeric-retakes-v5','lines-numeric-tts-map-v5.json'),('game-math-lines-unit-retake-v6','lines-unit-tts-map-v6.json')]:
    P=ROOT/'projects'/slug
    m=read(P/'project.json');out=ROOT/m['tts']['outputDir']
    ko=read(P/'script/narration.ko.json')['scenes'];en=read(P/'script/narration.en.json')['scenes']
    for s,translation,ref in zip(ko,en,read(B/name)):
        ident=ref['additionId'];combined.pop(ident,None)
        pending=[x for x in pending if x!=ident];rejected=[x for x in rejected if x['id']!=ident]
        wav=out/f'chunks/{s["id"]}-scene.wav';asr=out/f'asr/{s["id"]}.json'
        if not wav.exists() or not asr.exists():pending.append(ident);continue
        raw=read(asr);sha=hashlib.sha256(wav.read_bytes()).hexdigest()
        if raw['audio_sha256']!=sha:pending.append(ident);continue
        samples,rate=sf.read(wav);duration=len(samples)/rate
        try:
            starts,ends,coverage=mod.a.align_characters(' '.join(s['lines']),raw['words'],duration)
            cursor=0;line_starts=[];line_ends=[];captions={'ko':[],'en':[]}
            for i,(line,english) in enumerate(zip(s['lines'],translation['lines'])):
                length=len(normalized(line));line_starts.append(float(starts[cursor]));line_ends.append(float(ends[cursor+length-1]))
                count=max(len(mod.a.split_caption(line,32)),len(mod.a.split_caption(english,46)))
                chunks=mod.a.partition_fixed(line,32,count);translated=mod.a.partition_fixed(english,46,count);offset=cursor
                for chunk,english_chunk in zip(chunks,translated):
                    n=len(normalized(chunk));begin=float(starts[offset]);end=float(ends[offset+n-1])
                    if end<=begin:raise ValueError('Zero-length recognized caption; inspect its word boundaries')
                    for lang,text,width in [('ko',chunk,32),('en',english_chunk,46)]:captions[lang].append({'start':begin,'end':end,'text':'\n'.join(mod.a.wrapped_lines(text,width)),'line':i})
                    offset+=n
                assert offset==cursor+length,'Caption token boundaries changed';cursor+=length
        except (ValueError,AssertionError) as error:
            pending.append(ident);rejected.append({'id':ident,'project':slug,'ttsScene':s['id'],'reason':str(error)});continue
        slot={'id':ident,'ttsProject':slug,'ttsScene':s['id'],'sourceType':ref['sourceType'],'voice':wav.relative_to(ROOT).as_posix(),'voiceSha256':sha,'voiceSeconds':duration,'seconds':duration+.6,'lineStarts':line_starts,'lineEnds':line_ends,'matchingCharacterCoverage':coverage,'captions':captions,'alignment':'current-hash word timestamps; raw meaning and listening reviewed separately'}
        offset=0;sentences=[]
        for line in s['lines']:
            for sentence in re.split(r'(?<=[.!?])\s+',line):
                n=len(normalized(sentence));sentences.append({'start':float(starts[offset]),'end':float(ends[offset+n-1]),'text':sentence});offset+=n
        assert offset==len(starts)
        slot['sentenceCues']=sentences
        if ref['sourceType']=='bridge':
            first=re.split(r'(?<=[.!?])\s+',s['lines'][0])[0];n=len(normalized(first))
            slot['questionStart']=max(.7,min(duration-1.8,float(starts[n]) if n<len(starts) else duration*.46))
        combined[ident]=slot
split_spec=importlib.util.spec_from_file_location('split_lines_reminder',B/'split-lines-game-reminder.py');split_mod=importlib.util.module_from_spec(split_spec);split_spec.loader.exec_module(split_mod);split_mod.split(combined,pending)
O=ROOT/'shared/output/game-math-part2-teaching-revision/lines';O.mkdir(parents=True,exist_ok=True)
for name,types in [('supplement-timing',['supplement','framing']),('bridge-timing',['bridge']),('game-timing',['actual-footage'])]:write(O/f'{name}.json',{k:v for k,v in combined.items() if v['sourceType'] in types})
write(O/'combined-addition-timing.json',combined)
progress={'aligned':len(combined),'pending':pending,'rejected':rejected,'timingGate':.93,'fullMeaningOrPixelQaComplete':False}
write(B/'lines-alignment-progress.json',progress);print(json.dumps(progress))
