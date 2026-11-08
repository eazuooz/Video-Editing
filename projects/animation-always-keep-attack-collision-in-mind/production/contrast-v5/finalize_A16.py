"""Single-episode A16 integration. No GPU, TTS, shared manifests or platform edits."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,re,shutil,sys
os.environ.update(OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
H=ROOT/'production/batches/animation-18-20261031/contrast-v5'
spec=importlib.util.spec_from_file_location('a16_assembler',H/'assemble_explanations.py')
ae=importlib.util.module_from_spec(spec);spec.loader.exec_module(ae)
LOCAL=H/'local/explanation-assembly/A16'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
 Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def rel(p):return Path(p).absolute().relative_to(ROOT).as_posix()
def norm(s):return ''.join(c.lower()for c in s if c.isalnum())
def cues(p):
 def sec(t):
  h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
 result=[]
 for block in re.split(r'\n\s*\n',Path(p).read_text('utf-8-sig').strip()):
  lines=block.splitlines();a,b=map(sec,lines[1].split(' --> '));result.append({'start':a,'end':b,'text':'\n'.join(lines[2:])})
 return result
def plan():
 ae.authorization('A16')
 gameManifest=H/'game-plates-caption-safe.json'
 if not gameManifest.exists():gameManifest=H/'game-plates-manifest.json'
 explanationManifest=ae.INTEGRATION
 gm=read(gameManifest);em=read(explanationManifest);baseline=read(ae.BASE)
 g=next(x for x in gm['episodes']if x['id']=='A16');e=next(x for x in em['episodes']if x['id']=='A16');b=next(x for x in baseline['records']if x['id']=='A16')
 assert g['ready']and gm['clock']=='relations-v4'and gm['baselineReviewSHA256']==sha(ae.BASE)
 assert len(em['episodes'])==17 and sum(len(x['rows'])for x in em['episodes'])==443 and em['precedenceResolved']
 revisions=read(H/'narration/source-verified-revisions.json');s=next(x for x in revisions['episodes']if x['id']=='A16')
 assert not s['changes']and not any(x['episode']=='A16'for x in revisions['existingApprovedChanges'])
 extension={'id':'A16','pictureEdits':g['pictureEdits'],'audioEdits':[]}
 d=ae.build_episode(e,b,extension)
 assert d['frames']==b['frames']and d['additionalFrames']==0 and len(d['audioEdl'])==1 and d['audioEdl'][0]['kind']=='preserve'
 assert all(r['newFrames']==r['endFrame']-r['startFrame']for r in extension['pictureEdits'])
 ae.save(LOCAL/'edl.json',d)
 save(HERE/'assembly-extension.json',{'schemaVersion':1,'clock':'relations-v4','baselineReviewSHA256':sha(ae.BASE),'episodes':[extension]})
 save(HERE/'assembly-plan.json',{'id':'A16','status':'single-episode-plan-validated','frames':d['frames'],'durationSeconds':d['frames']/60,
  'explanationIntervals':len(e['rows']),'gameAndAnalysisIntervals':len(g['pictureEdits']),'nonoverlapValidatedBy':'assemble_explanations.build_episode / exact picture EDL',
  'protectedMaps':e['preservedRelationRegions'],'preserveAllNarrationPcm':True,'sourceAudioAdded':False,
  'audioDecision':'Preserve exact baseline voice plus approved Nimbus bed. Newly acquired game sound remains separate because full sample listening and source-specific conditions are not completed.',
  'audioEvidence':rel(H/'footage/final-audio-adoption.json'),'newTts':False,'gpu':False,'edl':rel(LOCAL/'edl.json'),
  'inputs':[{'path':rel(p),'sha256':sha(p)}for p in [ae.BASE,explanationManifest,gameManifest,H/'narration/source-verified-revisions.json',H/'assemble_explanations.py']],
  'nativeGameplayFrames':sum(r.get('nativeFrames',0)for r in g['pictureEdits']),'analysisFramesFromGameMasks':sum(r.get('analysisFrames',0)for r in g['pictureEdits']),
  'humanReviewed':False,'platformChanged':False})
 print('A16 plan',d['frames'],'frames',len(d['pictureEdl']),'EDL regions; PCM entirely preserved',flush=True)
def captions():
 d=read(LOCAL/'edl.json');assert d['additionalFrames']==0 and len(d['audioEdl'])==1 and d['audioEdl'][0]['kind']=='preserve'
 b=next(x for x in read(H/'baseline-review-manifest.json')['records']if x['id']=='A16')
 folder=H/'local/final-audio/A16/captions';folder.mkdir(parents=True,exist_ok=True);proof=[]
 for lang in ['ko','en']:
  f=next(x for x in b['files']if x['kind']==lang+'.srt');src=ROOT/f['path'];assert sha(src)==f['sha256'];rows=cues(src)
  assert all(0<=x['start']<x['end']<=d['frames']/60 for x in rows)
  assert all(a['end']<=b['start']+.002 for a,b in zip(rows,rows[1:]))
  expected=read(HERE/('final.'+lang+'.json'))
  assert norm(''.join(x['text']for x in rows))==norm(''.join(' '.join(x['lines'])for x in expected['scenes']))
  dst=folder/('captions.provisional.'+lang+'.srt');shutil.copyfile(src,dst)
  proof.append({'language':lang,'source':rel(src),'sourceSha256':sha(src),'outputSha256':sha(dst),'cueCount':len(rows),'textAndTimestampsExact':True,'finalScriptTextMatches':True})
 src=HERE.parent/'local/relations-v4/captions.ass';dst=folder/'captions.provisional.ko.ass';shutil.copyfile(src,dst)
 save(folder/'review.json',{'status':'unchanged-approved-PCM-and-exact-baseline-cue-alignment','groups':[],'fallbackPassages':[],
  'assemblySha256':sha(LOCAL/'edl.json'),'method':'No new speech or time delta. Exact existing SRT and fixed-style KO ASS, verified against final KO/EN script.',
  'proof':proof,'ass':{'source':rel(src),'sourceSha256':sha(src),'outputSha256':sha(dst)},'humanListening':False})
 print('A16 captions exact',flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['plan','render','captions']);a=ap.parse_args()
 if a.command=='plan':plan()
 elif a.command=='captions':captions()
 else:print(ae.render_plan(read(LOCAL/'edl.json'))['stage'],flush=True)
if __name__=='__main__':main()
