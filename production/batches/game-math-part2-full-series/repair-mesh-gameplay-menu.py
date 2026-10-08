"""Replace only the inspected gameplay menu boundary; preserve narration/timing."""
from pathlib import Path
import json, hashlib, shutil, sys, importlib.util, datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-mesh-uv';P=R/'projects'/slug;W=R/'shared/output'/slug
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
preserved=W/'before-menu-boundary-repair'
assert not preserved.exists(),'Repair is intentionally non-idempotent: inspect the saved receipt instead.'
preserved.mkdir()
Dfile=B/'lessons'/f'{slug}.json';Cfile=P/'sources/gameplay-cuts.json';Tfile=P/'production/timeline.json'
m=read(P/'project.json');oldD=read(Dfile);oldT=read(Tfile);oldC=read(Cfile)
for p in [Dfile,Cfile,Tfile,W/'render-receipts.json',P/'production/qa.json',P/'production/math-review.json']:
 shutil.copy2(p,preserved/p.name)
for k in ['videoClean','videoBurnedCaptions']:
 p=R/m['paths'][k];shutil.copy2(p,preserved/p.name)
shutil.copytree(W/'qa',preserved/'qa')
images=sorted((W/'qa').glob('caption-strips-*.jpg'))+sorted((W/'qa').glob('composition-sheet-*.jpg'))
oldbeats=read(W/'qa/final-beats/generated-samples.json');oldobs=read(W/'qa/observation-samples.json')
images += [R/x['path'] for x in oldbeats['records']]+[R/x['path'] for x in oldobs['sheets']]
assert len(images)==47,(len(images),'8 captions +6 composition +10 explanation +23 observation')
write(preserved/'prior-direct-pixel-review.json',dict(status='partial-review-menu-boundary-rejected',videoSha256=oldbeats['videoSha256'],images=[dict(path=rel(p),sha256=sha(p)) for p in images],directViewEvidence='All188 caption crops,22 composition frames,62 explanation beats and89 source/seam samples were directly inspected. Scene07 final source175.2667 displays an upgrade menu and is rejected. No whole-video pixel pass was claimed.'))
newSegments=[dict(**{'in':22,'maxSeconds':25}),dict(**{'in':90,'maxSeconds':19}),dict(**{'in':132,'maxSeconds':19}),dict(**{'in':156,'maxSeconds':17.5})]
D=read(Dfile);s=next(x for x in D['scenes'] if x['id']=='07');s['sourceSegments']=newSegments;s['maxSeconds']=80.5
C=read(Cfile);c=next(x for x in C['cuts'] if x['scene']=='07');c['sourceSegments']=newSegments;c['maxSeconds']=80.5
assert [x for x in oldD['scenes'] if x['id']!='07']==[x for x in D['scenes'] if x['id']!='07']
allowed={'sourceSegments','maxSeconds'}
assert {k:v for k,v in next(x for x in oldD['scenes'] if x['id']=='07').items() if k not in allowed}=={k:v for k,v in s.items() if k not in allowed}
assert {k:v for k,v in D.items() if k!='scenes'}=={k:v for k,v in oldD.items() if k!='scenes'}
write(Dfile,D);write(Cfile,C)
sys.path.insert(0,str(B));sys.argv=[str(B/'build.py'),slug,'plan']
spec=importlib.util.spec_from_file_location('mesh_menu_build',B/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
T=read(Tfile)
assert {k:v for k,v in oldT.items() if k!='scenes'}=={k:v for k,v in T.items() if k!='scenes'},'All KO/EN cues and frame totals must remain unchanged.'
for a,b in zip(oldT['scenes'],T['scenes']):
 assert {k:v for k,v in a.items() if k not in ('cut','cuts')}=={k:v for k,v in b.items() if k not in ('cut','cuts')},a['id']
 assert sha(R/b['voice'])==b['voiceSha256']
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
rr=read(W/'render-receipts.json');eq=[]
for e in (x for x in T['scenes'] if x['classification']=='explanation'):
 r=rr[e['id']];assert r['dataSha256']==sha(preserved/Dfile.name)
 assert r['lessonSha256']==sha(R/m['paths']['sharedManimLesson']) and r['voiceSha256']==e['voiceSha256']
 assert r['stubSha256']==sha(R/f'manim/projects/{slug}/scene.py')
 assert all(sha(R/path)==value for path,value in r['dependencySha256'].items())
 assert next(x for x in oldD['scenes'] if x['id']==e['id'])==next(x for x in D['scenes'] if x['id']==e['id'])
 target=W/f'manim/videos/scene/1080p60/Scene{e["id"]}.mp4'
 eq.append(dict(scene=e['id'],path=rel(target),sha256=sha(target),originalCompletedAt=r['completedAt']))
 r.update(previousDataSha256=r['dataSha256'],dataSha256=sha(Dfile),sourceOnlyEquivalenceProof=f'projects/{slug}/production/gameplay-menu-repair.json')
write(W/'render-receipts.json',rr)
boundary=R/'shared/output/game-math-part2-full-series/inspection/mesh-uv-menu-boundaries'
quarterSheets=sorted(boundary.glob('window-*.jpg'));assert len(quarterSheets)==4
newslot=next(x for x in T['scenes'] if x['id']=='07')
proof=dict(status='source-boundary-repaired-encoding-pending',atUtc=now,preserved=rel(preserved),lessonBeforeSha256=sha(preserved/Dfile.name),lessonAfterSha256=sha(Dfile),oldCuts=next(x for x in oldT['scenes'] if x['id']=='07')['cuts'],newCuts=newslot['cuts'],directQuarterSecondSourceReview=[dict(path=rel(p),sha256=sha(p)) for p in quarterSheets],rejectedSourceIntervals=[[109,110],[151.25,152],[174,175.5]],reason='The source ends now stop before upgrade side panels:109,151,173.4166667. Additional real-time safe play replaces the rejected final menu. No repeats or speed change.',timingAndAllKoEnCuesIdentical=True,allRawNarrationSha256Unchanged=True,explanationRenderEquivalence=dict(reason='mesh_uv.py selects only its own explanation scene and production/timeline.json slot; normal timing() loads that same unchanged slot. Only actual scene07 sourceSegments/maxSeconds changed; global top-level data, all ten explanation definitions, renderer, dependencies, all explanation slot fields and WAV hashes match exactly. No new explanation render is claimed.',videos=eq),finalEncodedPixelReview='pending')
write(P/'production/gameplay-menu-repair.json',proof)
print(json.dumps(dict(newCuts=newslot['cuts'],seconds=T['seconds'],allCueTimesPreserved=True,explanationVideosReused=len(eq))),flush=True)
# Encode the four revised real-time pieces only; retain every other existing clip.
c=newslot['cut'];credit=c['credit']+' | '+c['licenseLabel']+' | excerpt, muted'
vf="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='"+credit+"':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=808,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='youtu.be/"+c['sourceId']+"':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=834"
pieces=[]
for j,seg in enumerate(c['segments']):
 piece=W/f'clips/07-source-{j+1}.mp4'
 mod.b.ff(['-ss',str(seg['in']),'-i',R/c['sourceFile'],'-vf',vf,'-frames:v',str(seg['frames']),*mod.b.ENC,piece],f'clip-07-source-{j+1}.log');pieces.append(piece)
listing=W/'clips/07-concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in pieces)+'\n',encoding='utf8')
mod.b.ff(['-f','concat','-safe','0','-i',listing,'-c:v','copy','-an','-movflags','+faststart',W/'clips/07.mp4'],'clip-07-concat.log')
mod.assemble(True)
print('Only game scene07 was encoded; narration, all188 cues and total duration preserved.',flush=True)
