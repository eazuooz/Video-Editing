"""Keep both directional claims; avoid a repeated phrase skipped in synthesis."""
from pathlib import Path
import json,hashlib,shutil,datetime
R=Path(__file__).resolve().parents[3];slug='game-math-mesh-uv';P=R/f'projects/{slug}';W=R/f'shared/output/{slug}'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'shared/output/GPU_HANDOFF.json').exists()
m=read(P/'project.json');out=R/m['tts']['outputDir'];recordfile=P/'production/narration-number-correction.json';record=read(recordfile)
assert not record['scene13ScriptChanged'],'This correction is already prepared.'
isolated=read(W/'line-repair-13/isolated-lines-cpu-asr.json')
assert isolated['lines'][0]['recognized'].strip()=='위쪽 레코드에는 옆쪽 법선을 저장합니다 인덱스도 해당 레코드를 가리키게 바꿉니다'
baseline=W/'before-hard-edge-clarification';baseline.mkdir(exist_ok=True)
scriptfile=R/m['paths']['script'];datafile=R/m['paths']['productionData'];script=read(scriptfile);data=read(datafile)
for f in [scriptfile,datafile,out/'chunks/13-scene.wav',out/'asr/13.json',W/'voice-job.log',W/'voice-job-result.json',W/'line-repair-13/provenance.json',W/'line-repair-13/isolated-lines-cpu-asr.json']:
 shutil.copy2(f,baseline/f.name)
s=next(x for x in script['scenes'] if x['id']=='13');d=next(x for x in data['scenes'] if x['id']=='13');assert s['lines']==d['ko']
before=s['lines'][3]
after='위쪽 면의 레코드에는 위를 향한 법선을 저장합니다. 옆면의 레코드에는 옆을 향한 법선을 저장합니다. 인덱스도 각 면의 레코드를 가리키게 바꿉니다.'
s['lines'][3]=after;d['ko'][3]=after
record['paragraphClarifications'].append({'scene':'13','language':'ko','lineIndex':3,'before':before,'after':after,'meaningReview':'passed-distinct-top-normal-and-side-normal-records-and-matching-indices','removedUsefulClaim':False,'valuesPreserved':[]})
record['scene13ScriptChanged']=True
record['secondRetake']={'preparedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':baseline.relative_to(R).as_posix(),'reason':'Whole-scene and independently isolated line readbacks both omit the top-normal clause. Preserve other six passing line WAVs and rewrite this paragraph as two distinct complete directional sentences.','previousWaveSha256':sha(out/'chunks/13-scene.wav'),'isolatedLastLineReview':'Full final line matches; whole-scene zero-duration subtitle-credit phrase remains raw ASR evidence, not a proven audible extra phrase.'}
write(scriptfile,script);write(datafile,data);write(recordfile,record)
print('One hard-edge paragraph clarified; both directions and changed indices preserved; only13 requires a changed-line take.')
