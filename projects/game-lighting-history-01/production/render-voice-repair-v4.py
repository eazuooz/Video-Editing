"""One complete paragraph repair; preserve all other current narration PCM."""
from pathlib import Path
import hashlib,json,runpy,sys
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-01/production'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(BASE/'voice-repair-plan-v4.json')
manifest='projects/game-lighting-history-01/production/voice-repair-manifest-v4.json'
if '--manifest' not in sys.argv or sys.argv[sys.argv.index('--manifest')+1]!=manifest:raise SystemExit('Use reviewed one-paragraph v4 manifest.')
for item in plan['preservedChunks']:
    if sha(ROOT/item['from'])!=item['sha256'] or sha(ROOT/item['to'])!=item['sha256']:raise SystemExit('An unaffected scene changed.')
if sha(ROOT/plan['original07']['file'])!=plan['original07']['sha256']:raise SystemExit('Original07 changed.')
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import gpu_handoff_guard
namespace=runpy.run_path(str(BASE/'render-voice.py'),run_name='stencil_paragraph_repair_entry')
renderer=namespace['render_narration']
original_render=renderer.render_chunks
def render_selected(items,batch_size,force_scenes=None):
    selected=[item for item in items if item.key==plan['paragraphKey']]
    if len(items)!=108 or len(selected)!=1:raise RuntimeError('Exactly one of108 paragraph jobs required.')
    if selected[0].path.exists():raise RuntimeError('Inspect existing take before reexecution.')
    print('Scoped repair:07-07 only;107 paragraphs retained.',flush=True)
    original_render(selected,1,set())
renderer.render_chunks=render_selected
def assemble_selected(jobs):
    import numpy as np,soundfile as sf
    if renderer.FINAL_WAV.exists():raise RuntimeError('Preserve existing assembled candidate.')
    original,sr=sf.read(ROOT/plan['original07']['file'],dtype='int16')
    if sr!=24000 or original.ndim!=1:raise RuntimeError('Expected24k mono current scene.')
    job=next(j for j in jobs if f'{j.scene_id}-{j.line_number:02d}'==plan['paragraphKey'])
    take,take_sr=sf.read(job.path,dtype='float32')
    if take_sr!=sr or take.ndim!=1 or not np.isfinite(take).all():raise RuntimeError('Finite24k mono take required.')
    cut0,cut1=[round(s*sr) for s in plan['replaceSceneSeconds']]
    # The exact word edges put both cuts in surrounding quiet gaps.
    faded=renderer._apply_edge_fades(take,sr)
    temp=renderer.CHUNK_DIR/'07-07-faded-local.wav'
    sf.write(temp,faded,sr,subtype='PCM_16')
    replacement,_=sf.read(temp,dtype='int16')
    patched=np.concatenate([original[:cut0],replacement,original[cut1:]])
    scene_path=renderer.CHUNK_DIR/'07-scene.wav'
    if scene_path.exists():raise RuntimeError('Preserve existing patched scene.')
    sf.write(scene_path,patched,sr,subtype='PCM_16')
    written,_=sf.read(scene_path,dtype='int16')
    if not np.array_equal(written[:cut0],original[:cut0]) or not np.array_equal(written[cut0+len(replacement):],original[cut1:]):raise RuntimeError('Unaffected07 PCM changed.')
    previous=read(ROOT/read(BASE/'tts-repair-completion-v3.json')['timing']['file'])
    grouped={}
    for entry in previous['entries']:grouped.setdefault(entry['scene_id'],[]).append(entry)
    groups={}
    for j in jobs:groups.setdefault(j.scene_id,[]).append(j)
    delta=(len(replacement)-(cut1-cut0))/sr;boundaries={}
    for sid,scene_jobs in groups.items():
        rows=grouped[sid];origin=rows[0]['start']
        b=[r['start']-origin for r in rows]+[rows[-1]['end']-origin]
        if sid=='07':
            b[6]=cut0/sr;b[7]=(cut0+len(replacement))/sr
            b[8]+=delta
        boundaries[tuple(j.text for j in scene_jobs)]=b
    renderer._line_boundaries=lambda pcm,sr,lines:boundaries[tuple(lines)]
    for item in plan['preservedChunks']:
        if sha(ROOT/item['to'])!=item['sha256']:raise RuntimeError('Unaffected scene changed.')
    renderer.assemble_scene_outputs(jobs)
    evidence=dict(schemaVersion=1,paragraphKey=plan['paragraphKey'],take=str(job.path.relative_to(ROOT)).replace('\\','/'),takeSha256=sha(job.path),originalSceneSha256=plan['original07']['sha256'],sceneSha256=sha(scene_path),cutSamples=[cut0,cut1],replacementSamples=len(replacement),durationDeltaSeconds=delta,preservedPrefixAndSuffixByteIdentical=True,preservedOtherSceneCount=12,paragraphs=108,knownReplacementPlacement=True,automaticWordAlignment=False,currentNarrationApproved=False,humanListening='pending')
    (BASE/'line-repair-patch-map-v4.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
renderer.assemble_outputs=assemble_selected
if __name__=='__main__':renderer.main()
