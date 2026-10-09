"""Review current repair waves as they finish, keeping the approved CPU ASR."""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys,time
R=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('slug');ap.add_argument('--baseline',required=True)
a=ap.parse_args();slug=a.slug
from production_control import require_current_authorization
require_current_authorization(slug,'replacement narration read-back')
baseline=(R/a.baseline).resolve();baseline.relative_to((R/'shared/output'/slug).resolve())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original={p.name.split('-')[0]:sha(p) for p in baseline.glob('*-scene.wav')}
assert original,'Preserved original repair waves required'
m=read(R/f'projects/{slug}/project.json');out=R/m['tts']['outputDir'];pending=set(original)
deadline=time.monotonic()+14400
while pending:
    for sid in sorted(pending):
        wave=out/f'chunks/{sid}-scene.wav';provenance=R/f'shared/output/{slug}/line-repair-{sid}/provenance.json'
        if not wave.exists() or not provenance.exists():continue
        try:v=read(provenance)
        except (json.JSONDecodeError,PermissionError):continue
        digest=sha(wave)
        if digest==original[sid] or digest!=v['sha256']:continue
        print('Review complete replacement scene',sid,'onCPU',flush=True)
        subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).parent/'review-voice.py'),'--project',slug,'--device','cpu','--scenes',sid],cwd=R,check=True)
        raw=read(out/f'asr/{sid}.json')
        assert raw['audio_sha256']==sha(wave)==digest
        pending.remove(sid)
    if not pending:break
    if time.monotonic()>deadline:raise TimeoutError('Preserved repair checkpoints remain; wait for missing replacements')
    time.sleep(15)
print('All replacement rawcaches are current; direct meaning/number review and humanlistening remain separate.',flush=True)
