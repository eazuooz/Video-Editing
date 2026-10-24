from pathlib import Path
import json
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
now=datetime.now(timezone.utc).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ideas=load(R/'shared/publishing/shorts-research/distinctive-ideas-2026-10-24.json')
slugs=['shorts-titanfall-time-shift','shorts-superliminal-perspective','shorts-ghost-leaf-updraft','shorts-gears-inertialization','shorts-portal-recursion']
auth={'id':'explicit-five-distinctive-shorts-20261024','requestedAt':now,'userEvidence':'이거 다만들어줘 한번에 — the five explicitly quoted Titanfall 2, Superliminal, Ghost of Tsushima, Gears of War 4 and Portal topics','slugs':slugs,'fullProductionAuthorized':True,'scope':'Five selected Shorts through finished local review outputs, internal QA and selective Git; latest explicit user request overrides the one-new-Short-per-day production limit for this finite batch only.','intermediateApprovalRequired':False,'youtubeAuthorized':False,'driveAuthorized':False,'humanFinalReviewRequired':True,'automaticNextOutsideBatch':False,'resourcePolicy':'Sequence resource-intensive jobs. Preserve live games/Unity and other jobs; use CPU/WARP while user editors remain open.','status':'active'}
save(B/'batch.json',{'schemaVersion':1,'authorization':auth,'stage':'sources-and-production-plans','updatedAt':now,'projects':[]})
controlpath=R/'shared/publishing/video-production-control.json';control=load(controlpath)
control['shortsBatchAuthorization']=auth
control['selectedShortVideo']=slugs[0]
control['shortsDirectSelection']={'slug':slugs[0],'selectedRevision':'distinctive-v1','fullProductionAuthorized':True,'batch':str((B/'batch.json').relative_to(R)).replace('\\','/'),'userEvidence':auth['userEvidence'],'scope':auth['scope'],'finalUserReviewRequired':True}
save(controlpath,control)
wp=R/'shared/publishing/shorts-worklist.json';work=load(wp)
batch=load(B/'batch.json')
for index,(slug,idea) in enumerate(zip(slugs,ideas['candidates']),1):
 p=R/'projects'/slug
 assert not (p/'project.json').exists(),f'Existing production must be resumed: {slug}'
 for d in ['script','planning','sources','production/local','publishing']: (p/d).mkdir(parents=True,exist_ok=True)
 (p/'.gitignore').write_text('production/local/\n__pycache__/\n',encoding='utf8')
 manifest={'schemaVersion':2,'slug':slug,'status':'preproduction','currentRevision':'distinctive-v1','title':idea['title'],'game':idea['game'],'authorization':auth,'format':{'type':'youtube-shorts','width':1080,'height':1920,'fps':60},'paths':{'productionPlan':f'projects/{slug}/planning/production-plan.json','checkpoint':f'projects/{slug}/production/checkpoint.json'},'publishReady':False,'createdAt':now}
 save(p/'project.json',manifest)
 plan={'slug':slug,'revision':'distinctive-v1','batchOrder':index,'research':idea,'scenePlan':[],'sourceFactsVerified':True,'independentFootageViewed':False,'scriptFinalized':False,'resourceChoice':{'device':'CPU/WARP','reason':'User Unity editors open. Preserve their resource usage; use approved Qwen voice with limited CPU threads and hidden isolated Unity captures.','policy':'recommended-production-choice-v1'},'humanReview':'pending','renderer':'Unity for actual technique implementation; Motion Canvas for animated guides, cat and composition','sourceCredits':'description-only','newCharacterGeneration':False}
 save(p/'planning/production-plan.json',plan)
 save(p/'production/checkpoint.json',{'slug':slug,'revision':'distinctive-v1','stage':'independent-footage-acquisition','authorization':auth,'updatedAt':now,'nextAction':'Acquire and directly view concept-matched FHD footage, then finalize narration and saved Unity scenes.','humanFinalReview':'pending'})
 save(p/'production/review-ledger.json',{'slug':slug,'revision':'distinctive-v1','checks':[],'platform':{'youtube':'not-uploaded','drive':'not-requested'},'humanFinalReview':'pending'})
 row={'slug':slug,'title':idea['title'],'status':'preproduction','authorization':auth,'batchOrder':index,'production':'Source acquisition and scene planning','review':'not-ready','youtube':'not-uploaded','drive':'not-requested'}
 assert not any(r.get('slug')==slug for r in work['rows'])
 work['rows'].append(row);batch['projects'].append({'slug':slug,'order':index,'status':'preproduction'})
work['updatedAt']=now;save(wp,work);save(B/'batch.json',batch)
print(json.dumps({'created':slugs,'resource':'CPU/WARP','youtubeAuthorized':False}))
