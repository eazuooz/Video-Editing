"""Repair an omitted scene head with separately verified full script lines.

Keep the approved narrator, model, precision, quality thresholds and old takes.
The local alternate manifest changes only scene batching and intermediate paths.
"""
from pathlib import Path
import sys, json, subprocess, shutil, hashlib, datetime
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
slug, sid = sys.argv[1:3]
sid = sid.zfill(2)
read = lambda p: json.loads(p.read_text(encoding='utf8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = read(ROOT / f'projects/{slug}/project.json')
script = read(ROOT / manifest['paths']['script'])
scene = next(s for s in script['scenes'] if s['id'] == sid)
work = ROOT / f'shared/output/{slug}/line-repair-{sid}'
work.mkdir(parents=True, exist_ok=True)
write = lambda p, v: p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
write(work/'script.ko.json', {**script, 'scenes': [scene]})
alternate = json.loads(json.dumps(manifest))
alternate['paths']['script'] = (work/'script.ko.json').relative_to(ROOT).as_posix()
alternate['tts'].update(renderMode='line', lineGapSeconds=.28,
    outputDir=(work/'voice').relative_to(ROOT).as_posix())
write(work/'manifest.json', alternate)
command = [sys.executable, '-X', 'utf8', str(Path(__file__).parent/'render-voice.py'),
    '--project', slug, '--manifest', (work/'manifest.json').relative_to(ROOT).as_posix(),
    '--batch-size', '1', '--device', 'cpu']
subprocess.run(command, cwd=ROOT, check=True)
sys.path.insert(0, str(ROOT/'qwen3-tts'))
import render_narration as r
# Shared renderer initializes these globals in main(); assembly also uses them.
r.np=np; r.sf=sf
r.configure_project(slug)
pieces=[]; line_records=[]
for index, text in enumerate(scene['lines'], 1):
    source=work/f'voice/chunks/{sid}-{index:02d}.wav'
    samples, sr = sf.read(source, dtype='float32')
    assert sr==24000 and samples.ndim==1
    assert r._passes_quality(r._tail_ratio(samples,sr),r._tail_decay_ms(samples,sr))
    pieces.append(r._apply_edge_fades(samples,sr))
    line_records.append({'line':index,'text':text,'source':source.relative_to(ROOT).as_posix(),
        'sha256':sha(source),'seconds':len(samples)/sr})
    if index<len(scene['lines']):pieces.append(np.zeros(round(.28*sr),dtype='float32'))
target=ROOT/manifest['tts']['outputDir']/f'chunks/{sid}-scene.wav'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
previous=target.with_name(f'{sid}-scene-previous-line-repair-{stamp}.wav')
shutil.copy2(target,previous)
sf.write(target,np.concatenate(pieces),24000)
r.assemble_outputs(r.load_jobs())
write(work/'provenance.json',{'scene':sid,'method':'Complete independently synthesized script lines; no narration text removed',
    'model':manifest['tts']['model'],'reference':manifest['tts']['reference'],
    'previous':previous.relative_to(ROOT).as_posix(),'lines':line_records,
    'lineGapSeconds':.28,'currentWave':target.relative_to(ROOT).as_posix(),'sha256':sha(target),
    'rawAsrAndMeaningReview':'pending'})
print('Full scene restored; current ASR and meaning review still required.',flush=True)
