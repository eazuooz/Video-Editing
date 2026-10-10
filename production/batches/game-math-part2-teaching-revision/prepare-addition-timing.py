"""Use current-hash read-back timing, never paragraph-length guesses, for new scenes."""
from pathlib import Path
import json,sys,hashlib,re,importlib.util
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-quaternion-teaching-additions-v2';P=ROOT/'projects'/slug
m=json.loads((P/'project.json').read_text(encoding='utf8'));out=ROOT/m['tts']['outputDir']
sys.argv=[sys.argv[0],slug];sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
spec=importlib.util.spec_from_file_location('revision_alignment',ROOT/'production/batches/game-math-part2-full-series/align.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
import soundfile as sf
script=json.loads((P/'script/narration.ko.json').read_text(encoding='utf8'))
mapping=json.loads((B/'quaternion-addition-tts-map.json').read_text(encoding='utf8'))
supplements={};bridges={};pending=[];rejected=[]
for s,ref in zip(script['scenes'],mapping):
    wav=out/f'chunks/{s["id"]}-scene.wav';asr=out/f'asr/{s["id"]}.json'
    if not asr.exists():pending.append(ref['additionId']);continue
    raw=json.loads(asr.read_text(encoding='utf8'));sha=hashlib.sha256(wav.read_bytes()).hexdigest()
    if raw['audio_sha256']!=sha:pending.append(ref['additionId']);continue
    samples,rate=sf.read(wav);duration=len(samples)/rate
    try:starts,ends,coverage=mod.a.align_characters(' '.join(s['lines']),raw['words'],duration)
    except ValueError as error:
        pending.append(ref['additionId']);rejected.append({'id':ref['additionId'],'ttsScene':s['id'],'reason':str(error)});continue
    cursor=0;line_starts=[];line_ends=[]
    for line in s['lines']:
        count=len(mod.normalized(line));line_starts.append(float(starts[cursor]));line_ends.append(float(ends[cursor+count-1]));cursor+=count
    slot={'id':ref['additionId'],'ttsScene':s['id'],'voice':wav.relative_to(ROOT).as_posix(),'voiceSha256':sha,'voiceSeconds':duration,'seconds':duration+.6,'lineStarts':line_starts,'lineEnds':line_ends,'matchingCharacterCoverage':coverage,'alignment':'current-hash Whisper word timestamps matched to approved Korean script; raw meaning review remains separate'}
    if ref['sourceType']=='bridge':
        first=re.split(r'(?<=[.!?])\s+',s['lines'][0])[0];count=len(mod.normalized(first))
        slot['questionStart']=min(duration-1.8,float(starts[count]) if count<len(starts) else duration*.46)
        slot['questionStart']=max(.7,slot['questionStart']);bridges[ref['additionId']]=slot
    else:supplements[ref['additionId']]=slot
O=ROOT/'shared/output/game-math-part2-teaching-revision'
for name,data in [('supplement-timing',supplements),('bridge-timing',bridges)]:
    (O/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
result={'alignedSupplements':len(supplements),'alignedBridges':len(bridges),'pending':pending,'rejected':rejected,'fullMeaningOrPixelQaComplete':False}
(B/'quaternion-addition-alignment-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result))
