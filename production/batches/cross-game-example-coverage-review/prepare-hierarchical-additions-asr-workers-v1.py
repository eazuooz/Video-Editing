"""Prepare CPU-only ASR workers; no model execution and no repeated voice request."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
old='projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
new='projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
src=(B/'review-orientation-cross-game-voice-v2.py').read_text('utf8').replace(old,new)
src=src.replace('game-math-orientation-matrices','hierarchical-game-outlines')
names={
 'narration-cross-game-repair-execution-v1.json':'narration-additions-execution-v1.json',
 'cross-game-repair-voice-closure-verification-v1.json':'additions-voice-closure-verification-v1.json',
 'narration-cross-game-repair-session-v1.json':'narration-additions-session-v1.json',
 'cross-game-repair-batch.ko.json':'additions.ko.json','cross-game-repair-batch.en.json':'additions.en.json',
 'cross-game-{args.mode}-asr-execution-v2.json':'additions-{args.mode}-asr-execution-v1.json',
 'cross-game-{args.mode}-asr-v2':'additions-{args.mode}-asr-v1',
 'cross-game-whole-asr-execution-v2.json':'additions-whole-asr-execution-v1.json',
 'cross-game-independent-context-plan-v2.json':'additions-independent-context-plan-v1.json',
 'cross-game-contexts-v2':'additions-contexts-v1','currentOrientationReview':'currentHierarchicalReview',
 '/orientation/':'/hierarchical/'
}
for a,b in names.items():src=src.replace(a,b)
src=src.replace("tts['results'])==5","tts['results'])==4").replace("script['scenes'])==5","script['scenes'])==4")
src=src.replace("script['scenes'])==19","script['scenes'])==18").replace("plan['contexts'])==19","plan['contexts'])==18")
src=src.replace('preserve original24PCM','preserve original12PCM')
needle='sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()'
assert needle in src
src=src.replace(needle,"""def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
    return h.hexdigest()""")
out=B/'review-hierarchical-additions-voice-v1.py';assert not out.exists()
compile(src,str(out),'exec');out.write_text(src,'utf8')
print('Prepared CPU2/GPU0 whole4/context18 worker; it requires actual voice closure and fresh resource; model0.')
