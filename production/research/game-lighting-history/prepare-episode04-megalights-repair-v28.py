"""Seal observed reviews and prepare only three changed cuts; preserve PCM/other cuts."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production';L=R/'production/research/game-lighting-history/local'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
h=L/'episode04-hair-native-v27/execution.json';hj=read(h)
assert hj['status']=='samples-ready' and len(hj['samples'])==38 and len(hj['boards'])==10
assert not psutil.pid_exists(79492) or abs(psutil.Process(79492).create_time()-1791690076.879737)>1
write(h.with_name('session.json'),{'sessionId':97865,'observedExitCode':0,'sessionClosed':True,'worker':hj['worker'],'observedAt':now(),'execution':rel(h),'executionSha256':sha(h),'basis':'Actual write_stdin returned exit0; actual worker identity absent. No rerun.'})
write(P/'hair-native-direct-review-v27.json',{'reviewedAt':now(),'scope':'38 exact half-second still samples, all10 boards directly viewed; continuous playback remains pending','execution':{'path':rel(h),'sha256':sha(h)},'boards':hj['boards'],'samples':hj['samples'],'allSamplesDirectlyRead':True,'allMovingFramesReviewed':False,'observations':[{'interval':[808,811.5],'decision':'exclude','reason':'Static model followed by material-window loading; does not teach input/result.'},{'interval':[812,816.5],'decision':'prerequisite UI only','reason':'MelaninMainColor/Secondary, Redness, Roughness, Scatter and Specular visible; window repositioning is not strand-generation evidence.'},{'interval':[817,826.32],'decision':'selected for material color input/result','reason':'Same model/camera, MelaninMainColor changes; hair becomes pale then dark again. Preserve control and model together; do not infer new strands or renderer replacement.'}],'newGitImages':0,'finalPixelApproval':False,'wholeEpisode60to40Approved':False})
e=L/'episode04-megalights-encoded-v26/execution.json';ej=read(e)
assert ej['status']=='encoded-samples-ready' and len(ej['items'])==202 and len(ej['boards'])==51
write(P/'megalights-encoded-direct-review-v26.json',{'reviewedAt':now(),'execution':{'path':rel(e),'sha256':sha(e)},'all202SamplesDirectlyRead':True,'all51BoardsDirectlyRead':True,'boards':ej['boards'],'items':ej['items'],'decision':'correct before final use','defects':[{'cut':6,'reason':'Yellow region marks railing rather than emitter; teal region covers display/structure rather than claimed table. Old overlays persist beyond source camera change near54.3s.'},{'cuts':[7,8],'reason':'New explanation-source label overlaps old tiny breadcrumb in top strip.'}],'captionSampleLayoutApproved':True,'all22CueSampleTextsRead':True,'fixedCenter':[960,970],'movingAlignmentApproved':False,'allFinalPixelsReviewed':False,'newGitImages':0})
p=P/'megalights-chapter-review-plan-v26.json';j=read(p);b=read(P/'megalights-chapter-review-execution-v26.json')
j['preparedAt']=now();j['scope']='MegaLights repair v28: retain7 exact completed cut files, rebuild only native markers and two explanation header strips'
j['baselinePlan']={'path':rel(p),'sha256':sha(p)}
for i,c in enumerate(j['cuts']):
 if i not in [5,6,7]:
  c['reuseEncodedCut']=b['results'][i]
  assert sha(R/c['reuseEncodedCut']['path'])==c['reuseEncodedCut']['sha256']
j['cuts'][5]['annotation']={'type':'tracked-observed-light-surface','from':1.2,'to':4.0,'sourceInterval':[51,53.8],'note':'Observed screen-space emitter and metal pipe only; interpolated markers stop before54.3s camera transition; no causal world ray or sample-count inference','lightTrack':[[1.2,850,75],[1.7,849,82],[2.7,854,102],[3.2,852,120],[4.0,846,150]],'surfaceTrack':[[1.2,596,386],[1.7,597,399],[2.7,596,426],[3.2,596,441],[4.0,590,470]],'allMovingAlignmentReviewed':False}
for i in [6,7]:j['cuts'][i]['opaqueHeaderStrip']=True
j['next']='Run one CPU2 corrective pair; inspect changed markers at dense intervals and unchanged-content hashes. Keep continuous playback and whole episode gates pending.'
write(P/'megalights-chapter-review-plan-v28.json',j)
src=R/'production/research/game-lighting-history/build-episode04-megalights-chapter-v26.py';s=src.read_text('utf-8').replace('v26','v28').replace('V26','V28')
anchor="  file=OUT/f'cut-{i+1:02d}-{c[\"id\"]}.mp4';frames=c['frames'];vf=[]"
replacement=anchor+"\n  if c.get('reuseEncodedCut'):\n   ref=c['reuseEncodedCut'];file=ROOT/ref['path'];assert sha(file)==ref['sha256'];pieces.append(file);state['results'].append({**ref,'reusedByteIdentical':True});save();continue"
assert anchor in s;s=s.replace(anchor,replacement)
anchor="   if a['type']=='native-light-surface':"
replacement="""   if a['type']=='tracked-observed-light-surface':
    def track_expr(track,col):
     result=str(track[-1][col]-35)
     for left,right in reversed(list(zip(track,track[1:]))):
      expr=f"({left[col]-35}+({right[col]-left[col]})*(t-{left[0]})/{right[0]-left[0]})"
      result=f"if(lt(t,{right[0]}),{expr},{result})"
     return result
    for key,color in [('lightTrack','0xF6D872'),('surfaceTrack','0x43D7CC')]:
     # Hollow Unicode marker follows measured screen coordinates frame by frame.
     f=OUT/(key+'.txt');f.write_text('○','utf-8')
     x=track_expr(a[key],1);y=track_expr(a[key],2)
     vf.append(f"drawtext=fontfile='C\\\\:/Windows/Fonts/malgun.ttf':textfile='{rel(f)}':expansion=none:x='{x}':y='{y}':fontsize=80:fontcolor={color}:enable='gte(t,{a['from']})*lt(t,{a['to']})'")
    vf.append(label('노랑: 광원 · 청록: 금속 표면',1150,130,size=26,color='white',name='observed-object-role')+f":enable='gte(t,{a['from']})*lt(t,{a['to']})'")
   elif a['type']=='native-light-surface':"""
assert anchor in s;s=s.replace(anchor,replacement)
anchor="  if c.get('label'):vf.append(label(c['label'],32,24,name='source-identity'))"
assert anchor in s;s=s.replace(anchor,"  if c.get('opaqueHeaderStrip'):vf.append('drawbox=x=0:y=0:w=iw:h=76:color=black:t=fill')\n"+anchor)
anchor="'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2'"
assert anchor in s;s=s.replace(anchor,"'-i',ROOT/'production/research/game-lighting-history/local/episode04-megalights-chapter-v26/game-lighting-history-04-megalights-chapter.clean.mp4','-map','0:v:0','-map','1:a:0','-c','copy'")
write_path=src.with_name('build-episode04-megalights-chapter-v28.py');assert not write_path.exists();write_path.write_text(s,'utf-8')
compile(s,str(write_path),'exec')
print(json.dumps({'prepared':rel(write_path),'changedCuts':3,'reusedCuts':7,'newTts':0,'audioReencode':0,'newGitImages':0}))
