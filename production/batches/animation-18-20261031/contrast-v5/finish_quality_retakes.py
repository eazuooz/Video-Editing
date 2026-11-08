"""Finite three-passage pronunciation retake after the existing GPU pass."""
from pathlib import Path
import json,time,subprocess,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(p.read_text('utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 while read(L/'tts-coordinator-state.json')['stage']not in ['speech-generated-needs-asr-and-ending-review','speech-pass-needs-attention']:time.sleep(5)
 assert read(H/'gpu-authorization.json')['gpuTtsAuthorizedNow'],'User screen-share gate must remain released'
 subprocess.run([str(PY),'-X','utf8',str(H/'prepare_reviewed_tts.py')],cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 mapping=read(H/'narration/released-tts-map.json')['entries'];targets={tuple(q)for q in read(H/'narration/quality-retake-targets.json')['targets']};rows=[m for m in mapping if(m['episode'],m['sentence'])in targets];assert len(rows)==len(targets)
 script=L/'quality-retakes.ko.json';save(script,{'scenes':[{'id':m['key'],'title':m['episode']+' pronunciation retake '+m['sentence'],'lines':[m['text']]}for m in rows]})
 manifest=read(H/'narration/released-tts-manifest.json');manifest['paths']['script']=script.relative_to(R).as_posix();manifest['tts']['filenameStem']='quality-retakes';mf=L/'quality-retakes-manifest.json';save(mf,manifest)
 log=L/'tts-reviewed-final-gpu.log';state=L/'quality-retakes-state.json';save(state,{'stage':'finite-targeted-retakes','keys':[m['key']for m in rows],'originalTakesPreserved':True,'humanListened':False})
 with log.open('ab')as stream:
  rc=subprocess.call([str(PY),'-X','utf8',str(R/'qwen3-tts/render_narration.py'),'--project','animation-contrast-v5','--manifest',str(mf.relative_to(R)),'--device','cuda:0','--batch-size','1','--force-scenes',','.join(m['key']for m in rows)],cwd=R,stdout=stream,stderr=stream,creationflags=subprocess.CREATE_NO_WINDOW)
 save(state,{'stage':'retakes-rendered-needs-independent-asr'if rc==0 else'scoped-retakes-failed','returncode':rc,'keys':[m['key']for m in rows],'humanListened':False})
if __name__=='__main__':main()
