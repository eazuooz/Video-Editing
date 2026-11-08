"""Frame-exact visual-only A03 replacement plan; no new narration or game footage."""
from pathlib import Path
import json, hashlib
H=Path(__file__).resolve().parent; P=H.parents[1]; R=P.parents[1]
B=R/'production/batches/animation-18-20261031'; L=P/'production/local/contrast-v5'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def prepare():
 control=read(R/'shared/publishing/video-production-control.json')['a03ContrastRevision20261108'];assert control['fullLocalRevisionAuthorized']
 base=read(H/'baseline-delivery.json'); pacing=read(P/'production/pacing-v3/edit-plan.json'); edl=read(P/'production/local/relations-v4/opening-edl.json')
 cuts=read(P/'production/grid-v1/edit-plan-final.json')['cuts']; events=pacing['events']; rows=[]
 def mapped(start,n,detail):
  for part in edl['pictureEdl']:
   if part['kind']!='baseline':continue
   a=max(start,part['sourceStartFrame']);z=min(start+n,part['sourceStartFrame']+part['frames'])
   if z>a:rows.append({**detail,'start':part['outputStartFrame']+a-part['sourceStartFrame'],'frames':z-a,'sourceOffset':a-start})
 for c in cuts:
  if c['kind']!='unity':continue
  start=c['startFrame']+sum(e['frames'] for e in events if e['pictureAt']<=c['startFrame'])
  mapped(start,c['frames'],{'key':f"cut-{c['index']:02d}",'mode':'analysis','paragraph':int(c['paragraph']),'chapter':int(c['chapter']),'gridStart':c['startFrame'],'gridFrames':c['frames']})
 inserted=0
 for e in events:
  if e['kind']=='explanation':
   start=e['pictureAt']+inserted; n=e['sourceEndFrame']-e['sourceStartFrame']
   for k in range(e['repeatCount']):mapped(start+k*n,n,{'key':f"{e['key']}-pass-{k+1}",'mode':'native','passIndex':k+1,'paragraph':1,'chapter':int(e['key'].split('-')[-1])})
  inserted+=e['frames']
 for part in edl['pictureEdl']:
  if part['kind']=='native-pass':rows.append({'key':f"relocated-{part['passIndex']}",'mode':'native','passIndex':part['passIndex'],'paragraph':1,'chapter':1,'start':part['outputStartFrame'],'frames':part['frames'],'sourceOffset':0})
 rows.sort(key=lambda x:x['start']);assert all(a['start']+a['frames']<=b['start'] for a,b in zip(rows,rows[1:]))
 # An insertion can split one baseline cut into two output ranges.
 counts={key:sum(r['key']==key for r in rows) for key in {r['key'] for r in rows}};seen={}
 for row in rows:
  key=row['key'];seen[key]=seen.get(key,0)+1
  if counts[key]>1:row['key']=key+'-part-'+str(seen[key])
 assert len({r['key'] for r in rows})==len(rows)
 for row in rows:row['end']=row['start']+row['frames'];row['startSeconds']=row['start']/60;row['endSeconds']=row['end']/60
 source=B/'local/real-clips-v2/studies/A03-attack.json';study=read(source)
 phases=[{'id':'standby','ko':'대기','sourceFrame':0,'clipTime':1.62,'meaning':'공격 전 기준 자세'},{'id':'lead-in','ko':'준비','sourceFrame':23,'clipTime':2.2,'meaning':'팔과 검을 들어 올림'},{'id':'attack','ko':'타격','sourceFrame':35,'clipTime':3.5833333333333335,'meaning':'검이 표적에 닿는 자세'},{'id':'follow-through','ko':'후속 동작','sourceFrame':48,'clipTime':4.583333333333333,'meaning':'몸을 굽혀 힘을 정리'}]
 assert study['trace'][0]['state']=='standby' and study['trace'][23]['state']=='lead-in' and study['trace'][35]['state']=='attack' and study['trace'][35]['hit'] and study['trace'][48]['state']=='follow-through'
 plan={'revision':'contrast-v5','episode':'A03','slug':P.name,'scope':'Only A03 UE explanatory cuts and its existing three-pass observation inserts; preserve relations map, actual gameplay, complete audio and captions.','baseline':base,'totalFrames':base['frames'],'duration':base['durationSeconds'],'fps':60,'rows':rows,'phaseFrames':phases,'source':{'study':str(source),'studySha256':sha(source),'sourceClip':study['sourceClip'],'ueFrames':str(B/'local/real-clips-v2/study-frames/A03-attack'),'sourceTiming':'Existing authored 48-frame demonstration derived from source clip interval 1.62–6.45 s; displayed 1× means demonstration playback, not original vendor-clip duration.','jointGuides':'Forward-kinematic bone positions from the exact recorded study tracks and original skeleton hierarchy, projected through the recorded orthographic camera.','hitRule':'Existing computed blade-capsule/target-sphere intersection; authored 2-frame hit-stop and 36/48 control thresholds remain separate from visual poses.'},'design':{'native':'Single large UE demonstration, no duplicate analysis pane, same normal-speed 3 passes.','fourPhases':'Four simultaneously visible real UE phase poses, then relevant panel progresses through the actual phase frames slowly.','analysis':'Single enlarged UE demo, fixed baseline skeleton ghost, actual hand/shoulder trajectory and foot guide.','controls':'Only real cancel36/cancel48/noinput alternatives retain two panes with explicitly different control states.','captionSafeY':920,'phaseColors':{'standby':'#77d7ca','lead-in':'#77d7ca','attack':'#ff8d85','follow-through':'#a4d987'},'fourPhaseLayoutReason':'Portrait crops in four columns preserve greater full-body height than two landscape rows; inspect 375px output before finalizing.'},'audioAndCaptions':'Copy original relations-v4 AAC packets and both unchanged SRTs. Preserve mix.wav hash and do not regenerate or retime speech.','humanReview':False,'platformMutation':False}
 save(H/'edit-plan.json',plan);save(H/'checkpoint.json',{'stage':'isolated-plan-ready','revision':'contrast-v5','replacementCuts':len(rows),'replacementFrames':sum(x['frames'] for x in rows),'baselinePreserved':True,'humanReview':False})
 print('planned',len(rows),'replacement ranges',sum(x['frames'] for x in rows)/60,'seconds')
 return plan
if __name__=='__main__':prepare()
