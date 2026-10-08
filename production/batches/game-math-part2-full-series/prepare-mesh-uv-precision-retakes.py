"""Preserve the completed first batch and clarify one numeric paragraph."""
from pathlib import Path
import json,hashlib,shutil,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug='game-math-mesh-uv'
P=R/f'projects/{slug}';W=R/f'shared/output/{slug}';A=W/'before-precision-retakes'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not (R/'shared/output/GPU_HANDOFF.json').exists(),'Wait for the current handoff finally/resume verification.'
result=read(W/'voice-job-result.json');assert result['exitCode']==0
recordfile=P/'production/narration-number-correction.json'
assert not recordfile.exists(),'Already prepared; preserve current replacement checkpoints.'
m=read(P/'project.json');out=R/m['tts']['outputDir'];scriptfile=R/m['paths']['script'];datafile=R/m['paths']['productionData']
script=read(scriptfile);data=read(datafile);A.mkdir(parents=True,exist_ok=True)
for f in [scriptfile,datafile,W/'voice-job.log',W/'voice-job-result.json']:
 shutil.copy2(f,A/f.name)
originals=[]
for sid,reason in [('04','Raw readback confuses the local twelve-byte index total with eleven; explicitly speak six two-byte indices and separate units.'),('13','Raw readback omits the side-record/side-normal clause and adds an unrequested farewell. Restore every original full line with independent line synthesis.')]:
 wave=out/f'chunks/{sid}-scene.wav';raw=out/f'asr/{sid}.json'
 assert sha(wave)==read(raw)['audio_sha256']
 shutil.copy2(wave,A/wave.name);shutil.copy2(raw,A/f'{sid}-original-asr.json')
 originals.append({'scene':sid,'reason':reason,'originalWave':(A/wave.name).relative_to(R).as_posix(),'originalWaveSha256':sha(wave),'originalRawAsr':(A/f'{sid}-original-asr.json').relative_to(R).as_posix(),'originalRawAsrSha256':sha(raw)})
s=next(x for x in script['scenes'] if x['id']=='04');d=next(x for x in data['scenes'] if x['id']=='04');assert s['lines']==d['ko']
before=s['lines'][5]
after='한 정점을 여섯 번 쓰는 국소 예도 보겠습니다. 정점 데이터는 삼십이 바이트입니다. 인덱스는 여섯 개에 이 바이트씩, 합이 십이 바이트입니다. 둘을 더한 사십사 바이트는 사각형 전체 백사십과 계산 범위가 다릅니다.'
s['lines'][5]=after;d['ko'][5]=after
write(scriptfile,script);write(datafile,data)
write(recordfile,{'status':'required-numeric-and-omission-retakes-pending','preparedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'retakeScenes':['04','13'],'originalAudio':originals,'preservedBatchLog':(A/'voice-job.log').relative_to(R).as_posix(),'preservedScript':(A/scriptfile.name).relative_to(R).as_posix(),'preservedScriptSha256':sha(A/scriptfile.name),'preservedLesson':(A/datafile.name).relative_to(R).as_posix(),'preservedLessonSha256':sha(A/datafile.name),'paragraphClarifications':[{'scene':'04','language':'ko','lineIndex':5,'before':before,'after':after,'meaningReview':'passed-independent-32-plus-6-times-2-equals44-versus-whole-quad140','removedUsefulClaim':False,'valuesPreserved':[32,6,2,12,44,140]}],'scene13ScriptChanged':False,'audioReplacements':{'status':'pending','scenes':[]},'humanListening':'pending'})
print('Original04/13 takes preserved. One paragraph clarified; full-line replacements pending.')
