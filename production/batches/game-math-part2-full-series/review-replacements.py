"""Wait for replacement WAV hashes before CPU read-back; retain raw evidence."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
from production_control import require_current_authorization
R=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--baseline',required=True);p.add_argument('--scenes',required=True);args=p.parse_args()
require_current_authorization(args.project,'replacement narration read-back')
baseline=(R/args.baseline).resolve();assert baseline.is_relative_to(R/'shared/output'/args.project)
m=json.loads((R/f'projects/{args.project}/project.json').read_text(encoding='utf8'));out=R/m['tts']['outputDir'];selected={s.strip().zfill(2) for s in args.scenes.split(',')}
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();old={sid:sha(baseline/f'{sid}-scene.wav') for sid in selected};deadline=time.monotonic()+14400;announced=None
while True:
 ready=[];complete=True
 for sid in sorted(selected):
  wav=out/f'chunks/{sid}-scene.wav';rawp=out/f'asr/{sid}.json'
  if not wav.exists() or sha(wav)==old[sid]:complete=False;continue
  current=sha(wav);raw=json.loads(rawp.read_text(encoding='utf8')) if rawp.exists() else {}
  if raw.get('audio_sha256')!=current:ready.append(sid);complete=False
 if ready:
  print('CPU read-back of changed current WAVs: '+','.join(ready),flush=True)
  subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).parent/'review-voice.py'),'--project',args.project,'--device','cpu','--scenes',','.join(ready)],cwd=R,check=True)
 lease=R/'shared/output/GPU_HANDOFF.json'
 state=json.loads(lease.read_text(encoding='utf-8-sig')) if lease.exists() else {}
 active=state.get('project')==args.project and state.get('state') in ('tts_running','gpu_granted_to_tts','research_boundary_saved','waiting_for_research_boundary')
 if complete and not active:
  subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).parent/'review-voice.py'),'--project',args.project,'--device','cpu'],cwd=R,check=True)
  print('All selected replacement hashes have current raw CPU evidence; direct meaning and listening review remain separate.',flush=True);break
 status=(tuple(ready),complete,active)
 if status!=announced:print('Replacement wait: '+str(status),flush=True);announced=status
 if time.monotonic()>deadline:raise TimeoutError('Replacement audio/read-back checkpoint retained')
 time.sleep(15)
