"""Read completed replacement chunks and quantify edit capacity. Never approves a plan."""
import json,pathlib,math,datetime,re,hashlib
import soundfile as sf
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
base=rd(P/'production/local/threejs-revision-v1/pair-caption-decoder-v3/plan.json')
changes=rd(P/'production/beginner-revision-v1/changes.json')
rows=[]
log=(P/'production/local/beginner-revision-v1/tts/job.log').read_text(encoding='utf-8',errors='replace')
finished=set(re.findall(r'Rendered (b\d+)-scene',log))
for r in changes['rows']:
 key=r['key'];file=R/r['replacementAudioPath'] if r.get('replacementAudioPath') else R/f"shared/output/narration/game-lighting-history-01/beginner-revision-v1/chunks/{r['ttsSceneId']}-scene.wav"
 vs=[v for v in base['voice'] if v['key']==key];old=sum(v['samples'] for v in vs)
 exp=0
 for v in vs:
  a=v['startFrame'];z=a+v['samples']/400
  exp+=sum(max(0,min(z,n['endFrame'])-max(a,n['startFrame'])) for n in base['nodes'] if n['role']=='explanation')
 complete=file.exists() and r['ttsSceneId'] in finished
 row=dict(key=key,oldSeconds=old/24000,oldExplanationSpeechFrames=exp,ttsComplete=complete,estimatedSeconds=r['ttsEstimatedSeconds'])
 if complete:
  m=sf.info(file);assert m.samplerate==24000
  row.update(samples=m.frames,seconds=m.duration,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),deltaSeconds=m.duration-old/24000,
             naiveExplanationAdditionFrames=max(0,math.ceil(m.frames/400)-math.ceil(old/400)) if exp else 0)
 rows.append(row)
known=[r for r in rows if r['ttsComplete']]
report=dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),completed=len(known),total=len(rows),knownOldSeconds=sum(r['oldSeconds'] for r in known),knownNewSeconds=sum(r['seconds'] for r in known),naiveExplanationAdditionSeconds=sum(r['naiveExplanationAdditionFrames'] for r in known)/60,actualExtraNeededIfEveryIncreaseIsExplanationSeconds=sum(r['naiveExplanationAdditionFrames'] for r in known)/40,notes=['Read-only capacity estimate. Speech may continue across relevant retained native footage after semantic design.','Do not manufacture idle footage or approve60:40 from this estimate.','No speedup, no source voice deletion, no final timing approval.'],rows=rows)
out=P/'production/local/beginner-revision-v1/capacity.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False))
