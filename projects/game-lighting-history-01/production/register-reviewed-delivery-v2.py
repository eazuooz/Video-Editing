"""Register the observed current pair only after the direct repair review."""
import pathlib,json,hashlib,datetime
R=pathlib.Path(__file__).resolve().parents[3]
P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1';D=O/'repair-v2'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 e=rd(D/'execution.json');q=rd(D/'combined-review.json');plan=rd(D/'plan.json')
 assert e['exitCode']==0 and q['allFinalPixelsApproved'] and q['sourceSha256']==e['outputs']['captioned']['sha256']
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 # Adapter for the repository's selected-timeline rebuild schema; canonical nodes stay in plan.json.
 adapter={'schemaVersion':1,'canonicalPlan':rel(D/'plan.json'),'canonicalPlanSha256':sh(D/'plan.json'),'fps':60,'scenes':plan['nodes']}
 wr(P/'production/current-rebuild-timeline.json',adapter)
 p=rd(P/'project.json');p['status']='reviewed-final-pair-awaiting-private-upload';p['engines']=['motion-canvas','ffmpeg']
 paths=p['paths'];paths.update(videoClean=e['outputs']['clean']['path'],videoBurnedCaptions=e['outputs']['captioned']['path'],timeline=rel(P/'production/current-rebuild-timeline.json'),publishingKo=rel(P/'publishing/description.ko.txt'),publishingEn=rel(P/'publishing/description.en.txt'),audioReport=rel(O/'mix-execution.json'),motionCanvasProject='motion-canvas/src/projects/game-lighting-history-01/explanation-assets-v1/explanation-01.ts')
 paths.pop('manimProject',None)
 p['membershipOutro']['appliedToFinal']=True
 p['editing']['plannedActualSeconds']=1302.9;p['editing']['plannedExplanationSeconds']=868.6;p['editing']['exampleInterleaving']['reviewStatus']='current encoded footage and joins reviewed; unchanged closed GOP evidence retained'
 p['productionGates'].update(footageIntervalsApproved=True,allAnimated25dPixelsReviewed=True,finalRendered=True,allEncodedPixelsReviewed=True)
 s=p['productionState'];s.update(updatedAt=now,currentParagraphPairs=144,currentFinalPlan=rel(D/'plan.json'),currentDuplicateReview=rel(P/'production/current-duplicate-review-v12.json'),currentEncodedReview=rel(D/'combined-review.json'),currentPairEvidence=rel(D/'execution.json'),currentVoiceApproved=True,guideParagraphsAdded=36,originalNarrationPreserved=True)
 s['explanationPaletteRevision']['blackPixelsApproved']=True
 s['lookdev']='Current black projected2.5D scenes and retained action ranges reviewed; final pixels approved with changed-range review plus verified unchanged closed GOP payloads.'
 s['currentVoiceReview']='Current original108 and36 guides plus final mix direct ASR comparisons accepted; human listening/pronunciation pending.'
 p['finalRender']={'status':'reviewed','frames':131010,'durationSeconds':2183.5,'outputs':e['outputs'],'technicalEvidence':rel(D/'execution.json'),'pixelEvidence':rel(D/'combined-review.json'),'knownIssues':['Human full listening/pronunciation pending','Public rights review pending','Original Nimbus Audio Library file pending','Existing truncated member handle preserved','External backup pending']}
 wr(P/'project.json',p)
 ledger=rd(P/'production/review-ledger.json');ledger['updatedAt']=now
 entries=[(P/'production/current-duplicate-review-v12.json','Current relevant changed inputs; unchanged comparison hashes reused','pass'),(O/'encoded-pixel-direct-review.json','Baseline990 images165boards; source failures preserved as historical','reused'),(O/'retained-motion-review.json','All30 retained explanation ranges at normal speed with sampled observations','pass'),(D/'source-review.json','Replacement native source intervals directly viewed and normal-speed sampled playback','pass'),(D/'execution.json','New clean/captioned full decode and every-frame PTS; identical AAC','pass'),(D/'combined-review.json','Current changed encoded pixels/joins plus byte-identical retained closed GOPs','pass')]
 for path,scope,result in entries:ledger['evidence']=[x for x in ledger['evidence'] if x['path']!=rel(path)];ledger['evidence'].append(dict(path=rel(path),sha256=sh(path),scope=scope,result=result))
 ledger['localProductionComplete']=True;ledger['wholeVideoCompleted']=False;ledger['implementationVerification']['finalRendering']='pass';ledger['implementationVerification']['finalPixels']='pass'
 wr(P/'production/review-ledger.json',ledger)
 c=rd(P/'production/checkpoint.json');c.update(updatedAt=now,stage='reviewed-pair-ready-to-collect',activeJob=None,nextAction='Collect four verified files, upload reviewed captioned master once as private, save/reopen settings and selectively commit/push.')
 c['gates'].update(allFinalCaptionPixelsReviewed=True,finalRenderComplete=True)
 c['unresolved']=['Four-file collection and one authorized private upload/settings/Git','Human listening/pronunciation, public rights, original Nimbus file and external backup pending']
 c['repairedPair']={'execution':rel(D/'execution.json'),'review':rel(D/'combined-review.json'),'exitCode':0}
 wr(P/'production/checkpoint.json',c)
 u=rd(P/'publishing/upload-package-v1.json');u.update(status='reviewed-ready-to-collect-and-upload',planSha256=sh(D/'plan.json'),captionedSha256=e['outputs']['captioned']['sha256']);wr(P/'publishing/upload-package-v1.json',u)
 print('Registered reviewed current pair; not yet collected or uploaded.')
if __name__=='__main__':main()
