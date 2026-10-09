"""Reorder reviewed real-time source pieces to the spoken roof/container cues.

Preserve every voice, subtitle, explanation render and final frame count.
Run once; inspect its saved baseline and receipt before any later revision.
"""
from pathlib import Path
import json, hashlib, shutil, sys, importlib.util, datetime, math
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-normal-transform-uv';P=R/'projects'/slug;W=R/'shared/output'/slug
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
preserved=W/'before-subject-timing-repair'
resumePreparation=preserved.exists()
if not resumePreparation:preserved.mkdir()
Dfile=B/'lessons'/f'{slug}.json';Cfile=P/'sources/gameplay-cuts.json';Tfile=P/'production/timeline.json'
m=read(P/'project.json');oldD=read(Dfile);oldT=read(Tfile);oldC=read(Cfile)
stablePaths=[R/m['paths'][k] for k in ['narration','captionsKo','captionsEn','audioMix']]
stableHashes={rel(p):sha(p) for p in stablePaths}
if resumePreparation:
 assert not (P/'production/gameplay-subject-timing-repair.json').exists(),'Non-idempotent repair: inspect the existing receipt.'
 assert all(sha(p)==sha(preserved/p.name) for p in [Dfile,Cfile,Tfile,W/'render-receipts.json']), 'Resume only untouched preparation, never a partly mutated source.'
else:
 for p in [Dfile,Cfile,Tfile,W/'render-receipts.json',P/'production/qa.json',P/'production/math-review.json']:
  shutil.copy2(p,preserved/p.name)
 for k in ['videoClean','videoBurnedCaptions']:
  p=R/m['paths'][k];shutil.copy2(p,preserved/p.name)
 shutil.copytree(W/'qa',preserved/'qa')
images=sorted((W/'qa').glob('caption-strips-*.jpg'))+sorted((W/'qa').glob('composition-sheet-*.jpg'))
oldbeats=read(W/'qa/final-beats/generated-samples.json');oldobs=read(W/'qa/observation-samples.json')
images += [R/x['path'] for x in oldbeats['records']]+[R/x['path'] for x in oldobs['sheets']]
assert len(images)==40 and len(oldT['koCaptions'])==156
write(preserved/'prior-direct-pixel-review.json',dict(status='partial-review-scene08-subject-timing-rejected',videoSha256=oldbeats['videoSha256'],images=[dict(path=rel(p),sha256=sha(p)) for p in images],directViewEvidence='All156 caption crops, composition sheets,51 explanation beats and79 source/seam samples were directly inspected. Scene08 roof and container source switches occur after their spoken claims. The baseline is rejected at those subject connections; no whole-video pixel pass is claimed.'))
# Complete original intervals, each exactly once: wall720–750, roof588–603,
# container400–408. Align the first roof/container frames to subtitle88/89.
segments=[(720,1001),(588,245),(400,480),(588+245/60,655),(720+1001/60,799)]
assert sum(f for _,f in segments)==3180
newSegments=[{'in':at,'maxSeconds':math.nextafter(f/60,math.inf)} for at,f in segments]
assert all(math.floor(v['maxSeconds']*60)==f for v,(_,f) in zip(newSegments,segments))
D=read(Dfile);s=next(x for x in D['scenes'] if x['id']=='08');s['sourceSegments']=newSegments
C=read(Cfile);c=next(x for x in C['cuts'] if x['scene']=='08');c['sourceSegments']=newSegments
assert [x for x in oldD['scenes'] if x['id']!='08']==[x for x in D['scenes'] if x['id']!='08']
allowed={'sourceSegments'}
assert {k:v for k,v in next(x for x in oldD['scenes'] if x['id']=='08').items() if k not in allowed}=={k:v for k,v in s.items() if k not in allowed}
assert {k:v for k,v in D.items() if k!='scenes'}=={k:v for k,v in oldD.items() if k!='scenes'}
write(Dfile,D);write(Cfile,C)
sys.path.insert(0,str(B));sys.argv=[str(B/'build.py'),slug,'plan']
spec=importlib.util.spec_from_file_location('normal_subject_build',B/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
T=read(Tfile)
assert {k:v for k,v in oldT.items() if k!='scenes'}=={k:v for k,v in T.items() if k!='scenes'},'All156 KO/EN cue times and frame totals must be identical.'
for a,b in zip(oldT['scenes'],T['scenes']):
 assert {k:v for k,v in a.items() if k not in ('cut','cuts')}=={k:v for k,v in b.items() if k not in ('cut','cuts')},a['id']
 assert sha(R/b['voice'])==b['voiceSha256']
assert all(sha(R/p)==h for p,h in stableHashes.items())
rr=read(W/'render-receipts.json');eq=[]
for e in (x for x in T['scenes'] if x['classification']=='explanation'):
 r=rr[e['id']];assert r['dataSha256']==sha(preserved/Dfile.name)
 assert r['lessonSha256']==sha(R/m['paths']['sharedManimLesson']) and r['voiceSha256']==e['voiceSha256']
 assert r['stubSha256']==sha(R/f'manim/projects/{slug}/scene.py')
 assert all(sha(R/path)==value for path,value in r['dependencySha256'].items())
 assert next(x for x in oldD['scenes'] if x['id']==e['id'])==next(x for x in D['scenes'] if x['id']==e['id'])
 target=W/f'manim/videos/scene/1080p60/Scene{e["id"]}.mp4'
 eq.append(dict(scene=e['id'],path=rel(target),sha256=sha(target),originalCompletedAt=r['completedAt']))
 r.update(previousDataSha256=r['dataSha256'],dataSha256=sha(Dfile),sourceOnlyEquivalenceProof=f'projects/{slug}/production/gameplay-subject-timing-repair.json')
write(W/'render-receipts.json',rr)
newslot=next(x for x in T['scenes'] if x['id']=='08')
assert abs(newslot['cuts'][1]['outputStart']-398.3666666667)<1e-8
assert abs(newslot['cuts'][2]['outputStart']-402.45)<1e-8
proof=dict(status='source-timing-repaired-encoding-pending',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),preserved=rel(preserved),lessonBeforeSha256=sha(preserved/Dfile.name),lessonAfterSha256=sha(Dfile),oldCuts=next(x for x in oldT['scenes'] if x['id']=='08')['cuts'],newCuts=newslot['cuts'],reason='Roof begins at subtitle88; container begins at subtitle89. Then revisit the remaining original roof and wall footage during the general coordinate/address explanation. The complete original intervals are used once, at real-time speed.',timingAndAllKoEnCuesIdentical=True,allRawNarrationSha256Unchanged=True,stableFileHashes=stableHashes,explanationRenderEquivalence=dict(reason='All8 explanation scene definitions, complete timeline slots, renderer, stub, dependencies and WAV hashes are unchanged. Only scene08 actual sourceSegments changed. Cached explanation videos are reused; no rerender is claimed.',videos=eq),finalEncodedPixelReview='pending')
write(P/'production/gameplay-subject-timing-repair.json',proof)
print(json.dumps(dict(newCuts=newslot['cuts'],seconds=T['seconds'],allCueTimesPreserved=True,explanationVideosReused=len(eq))),flush=True)
c=newslot['cut'];credit=c['credit']+' | '+c['licenseLabel']+' | excerpt, muted'
vf="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='"+credit+"':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=808,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='youtu.be/"+c['sourceId']+"':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=834"
pieces=[]
for j,seg in enumerate(c['segments']):
 piece=W/f'clips/08-source-{j+1}.mp4'
 mod.b.ff(['-ss',str(seg['in']),'-i',R/c['sourceFile'],'-vf',vf,'-frames:v',str(seg['frames']),*mod.b.ENC,piece],f'clip-08-source-{j+1}.log');pieces.append(piece)
listing=W/'clips/08-concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in pieces)+'\n',encoding='utf8')
mod.b.ff(['-f','concat','-safe','0','-i',listing,'-c:v','copy','-an','-movflags','+faststart',W/'clips/08.mp4'],'clip-08-concat.log')
mod.assemble(True)
assert all(sha(R/p)==h for p,h in stableHashes.items()),'The same narration-only audio and all subtitle files must survive the edit.'
print('Only actual scene08 was encoded; all156 cues, narration and12:26 duration preserved.',flush=True)
