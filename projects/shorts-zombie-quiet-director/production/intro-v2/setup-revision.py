"""Select the human-requested prepend revision and pin the unchanged body."""
from pathlib import Path
import json,datetime,hashlib,copy
P=Path(__file__).resolve().parents[2];R=P.parents[1];L=P/'production/local/intro-v2'
KO='게임에서는 몬스터와의 전투 빈도를 의도적으로 조절하기도 합니다.'
EN='Some games deliberately control how often you fight monsters.'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,a):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 L.mkdir(parents=True,exist_ok=True);baseline=L/'baseline';baseline.mkdir(exist_ok=False)
 for rel in ['project.json','script/narration.ko.json','script/narration.en.json','script/captions.json','script/clauses.json','production/visual-timing.json','production/review-ledger.json','publishing/drive-receipt.json','production/delivery-output.json']:
  target=baseline/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((P/rel).read_bytes())
 pinned={}
 for rel in ['production/local/clean.mp4','production/local/captioned.mp4','production/local/final-mix.wav','production/local/narration-stem.wav','production/local/background-stem.wav']:
  source=P/rel;pinned[rel]={'sha256':sha(source),'bytes':source.stat().st_size}
 assert pinned['production/local/captioned.mp4']['sha256']=='537988bd6f023da3e06645c2eff2baa770b1a37cc06ac6b40fc6e28d2439d6a4'
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();evidence='영상 제일 앞에 부분에서 게임에서는 몬스터의 전두 빈도(강도)를 의도적으로 조절합니다. 앞부분에 애니메이션 우리도구중에 알아서 골라서 작업해서 추가해줘'
 record={'id':'zombie-quiet-intro-v2','at':now,'userEvidence':evidence,'scope':'Prepend new narrated monster encounter-frequency illustration; preserve complete44.2s body and approved PCM; complete Drive final review, no YouTube upload','renderer':'Motion Canvas, recognizable articulated2D zombies with unchanged scale/speed and changed encounter spacing','ko':KO,'en':EN,'canonicalMeaning':'Encounter/combat frequency, not enemy HP or attack strength; qualified statement does not give PZ an intensity Director','baselineCommit':'639f907e948af90474e31dabd152aa80e148fc22','baselineDurationSeconds':44.2,'baselineFrames':2652,'body':pinned,'priorDrive':read(P/'publishing/drive-receipt.json'),'retainedBodyRerender':False,'bodyVoiceRegenerated':False,'introBgm':'No separately restarted music; retain original body mix and its music onset. Intro uses clean narration before the opening fight/quiet contrast.'}
 save(P/'production/revisions/intro-v2.json',record)
 for language,text in [('ko',KO),('en',EN)]:
  doc={'title':'전투 빈도의 의도적 조절','status':'locked selected intro-only revision','scenes':[{'id':'00','title':'전투 간격의 조절','lines':[text]}]};save(P/f'script/intro-v2/narration.{language}.json',doc)
 manifest=read(P/'production/tts-manifest.json');manifest['revision']='zombie-quiet-intro-v2';manifest['paths']['script']=f'projects/{P.name}/script/intro-v2/narration.ko.json';manifest['tts'].update(outputDir=f'shared/output/narration/{P.name}/zombie-quiet-intro-v2',filenameStem='intro-v2',maxNewTokens=512);save(P/'production/intro-v2/tts-manifest.json',manifest)
 cp=read(P/'production/checkpoint.json');cp.update(stage='intro-v2-production',currentRevision='zombie-quiet-intro-v2',humanFinalReview='prior version revision requested; new complete version pending',next='Generate only new intro and preserve body',nextAction='New intro TTS, narration-timed animation and splice QA');save(P/'production/checkpoint.json',cp)
 plan=read(P/'planning/production-plan.json');plan.update(status='intro-v2-production',latestRevision=record);save(P/'planning/production-plan.json',plan)
 project=read(P/'project.json');project.update(status='intro-v2-production',publishReady=False);project['currentRevision']='zombie-quiet-intro-v2';save(P/'project.json',project)
 ctrlpath=R/'shared/publishing/video-production-control.json';ctrl=read(ctrlpath);owned=ctrl['shortsRecurringAuthorization'];assert owned['selectedShort']==P.name
 owned['previousSelection']=owned['latestSelection'];owned['latestSelection']={'at':now,'userEvidence':evidence,'selectedRevision':'zombie-quiet-intro-v2','scope':record['scope'],'humanFinalReviewRequired':True,'automaticNextVideo':False,'heartbeatRestrictionUnchanged':True};save(ctrlpath,ctrl)
 workpath=R/'shared/publishing/shorts-worklist.json';work=read(workpath);row=next(r for r in work['rows'] if r['slug']==P.name);row.update(productionStatus='intro animation revision in production',reviewStatus='revision requested; new complete version pending',currentRevision='zombie-quiet-intro-v2',userApproval='pending revised complete version');save(workpath,work)
 print('Pinned body and selected intro-v2; no media jobs started')
if __name__=='__main__':main()
