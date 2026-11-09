"""Finite selected17 local delivery worker; no scheduling or platform work.

Waits for actual rendered plates and independently checked speech. A16 is
owned by the parallel integration worker. One CPU4 encoder at a time here.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys,time,traceback
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def invoke(args,log):
 with Path(log).open('wb')as f:subprocess.run([str(PY),'-X','utf8',*map(str,args)],cwd=R,stdout=f,stderr=f,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--once',action='store_true');ap.add_argument('--episode');ap.add_argument('--episodes',nargs='+');ap.add_argument('--state-key',default='');v=ap.parse_args()
 control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];ids=[e for e in control['episodes']if e!='A16'];assert len(ids)==16 and 'A03'not in ids
 if v.episode:assert v.episode in ids;ids=[v.episode]
 if v.episodes:assert not v.episode and set(v.episodes)<=set(ids)and len(v.episodes)==len(set(v.episodes));ids=[ep for ep in ids if ep in v.episodes]
 assert not v.state_key or(v.state_key.isalnum()and len(v.state_key)<20)
 status=L/(f'local-finish-{v.state_key}-state.json'if v.state_key else'local-finish-state.json')
 prior=status if status.exists()else L/'local-finish-state.json'
 state=read(prior)if prior.exists()else{'completed':{},'failed':{},'waiting':{}}
 for k in ['completed','failed','waiting']:state[k]={ep:d for ep,d in state[k].items()if ep in ids}
 state.update(scope=ids,platformChanged=False,gpuUsed=False)
 while True:
  if(L/'finish-queue-pause.json').exists():state.update(active=None,stage='paused-at-episode-boundary');save(status,state);return
  pending=[];did=False;sourceHash=sha(H/'narration/source-verified-revisions.json')
  gameManifest=H/'game-plates-caption-safe.json'
  if not gameManifest.exists():gameManifest=H/'game-plates-manifest.json'
  plates={e['id']:e for e in read(gameManifest)['episodes']};audio={e['id']:e for e in read(L/'final-audio/audio-preparation.json')['episodes']}
  for ep in ids:
   if(L/'finish-queue-pause.json').exists():state.update(active=None,stage='paused-at-episode-boundary');save(status,state);return
   integration=H/'renderer/integration-caption-safe.json'
   if not integration.exists():integration=H/'renderer/integration-manifest.json'
   correction=H/'visual-corrections'/(ep+'.json')
   p=plates[ep];a=audio[ep];sig=hashlib.sha256(json.dumps({'plates':p,'audio':a,'sourceHash':sourceHash,'integrationSha256':sha(integration),'visualCorrectionSha256':sha(correction)if correction.exists()else None,'codeHashes':{f:sha(H/f)for f in ['build_final_extensions.py','assemble_explanations.py','prepare_final_audio.py','finalize_episode.py']}},sort_keys=True).encode()).hexdigest()
   if state['completed'].get(ep,{}).get('inputSignature')==sig:continue
   why=[]
   if not p['ready']:why.append('gameplay-plates')
   if a['sourceRevisionsSha256']!=sourceHash:why.append('current-script-mix')
   if any(g['status']=='waiting-for-takes'or not g.get('technicalMixVerified')for g in a['groups']):why.append('speech-asr-and-mix-checks')
   if state['failed'].get(ep,{}).get('inputSignature')==sig:why.append('same-input-failure-needs-correction')
   if why:state['waiting'][ep]=why;pending.append(ep);continue
   state.update(active=ep,stage='rendering-speech-pictures',updatedAt=time.time());save(status,state)
   try:
    builder=module('final_extension_builder',H/'build_final_extensions.py');assembly=builder.assembly
    ext=builder.build(ep,True);assert ext['readyForAssembly']
    extension=L/'final-extensions'/ep/'extensions.json';assembly.plan_all(extension,selected=ep)
    edl=assembly.L/ep/'edl.json';plan=read(edl);state['stage']='assembling-full-picture';save(status,state);assembly.render_plan(plan)
    state['stage']='aligning-final-captions';save(status,state)
    invoke([H/'prepare_final_audio.py','captions','--episode',ep,'--assembly',edl],L/f'{ep}-final-captions.log')
    state['stage']='encoding-four-delivery-files';save(status,state)
    invoke([H/'finalize_episode.py','--episode',ep,'--assembly',edl],L/f'{ep}-final-delivery.log')
    delivery=read(Path('C:/Users/1/Videos/YamyamCoding/animation-contrast-v5-review')/ep/'delivery.json')
    state['completed'][ep]={'inputSignature':sig,'delivery':delivery,'finishedAt':time.time()};state['waiting'].pop(ep,None);state['failed'].pop(ep,None);did=True
   except Exception as e:
    state['failed'][ep]={'inputSignature':sig,'error':repr(e),'traceback':traceback.format_exc(),'at':time.time()};pending.append(ep)
   state.update(active=None,stage='checking-next-ready-episode',updatedAt=time.time());save(status,state)
  if not pending:state['stage']='selected-local-files-ready-integrated-qa-pending';save(status,state);return
  state.update(active=None,stage='waiting-for-inspected-inputs',updatedAt=time.time());save(status,state)
  if v.once:return
  time.sleep(15)
if __name__=='__main__':main()
