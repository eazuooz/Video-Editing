"""Register current revision only after its explicit direct-review record."""
import pathlib,json,hashlib,datetime
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';D=P/'production/local/threejs-revision-v1/pair-caption-decoder-v3'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 e=rd(D/'execution.json');q=rd(D/'combined-review.json');plan=rd(D/'plan.json');ledger=rd(P/'production/review-ledger.json')
 assert e['exitCode']==0 and e['identicalAac'] and q['allFinalPixelsApproved'] and q['sourceSha256']==e['outputs']['captioned']['sha256']
 assert ledger['rendererRevision']['assetMotionReview']['all58PlayedToEndObserved']
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 wr(P/'production/current-rebuild-timeline.json',dict(schemaVersion=1,canonicalPlan=rel(D/'plan.json'),canonicalPlanSha256=sha(D/'plan.json'),fps=60,scenes=plan['nodes']))
 p=rd(P/'project.json');p['baselineDeliveryBeforeThreeJS']={k:p[k] for k in ['publishing','finalRender']}
 p['status']='reviewed-threejs-pair-awaiting-private-upload';p['engines']=['three.js','manim','motion-canvas','ffmpeg']
 p['paths'].update(videoClean=e['outputs']['clean']['path'],videoBurnedCaptions=e['outputs']['captioned']['path'])
 p['editing']['explanationGeometry']='actual3D-geometry-light-depth-occlusion-plus-Manim-math-and-retained-2D-diagrams'
 p['editing']['footageClassification']['explanation']='Self-authored Three.js, Manim, Motion Canvas and explanatory diagrams; role rather than executability determines classification.'
 p['productionState'].update(updatedAt=now,currentFinalPlan=rel(D/'plan.json'),currentEncodedReview=rel(D/'combined-review.json'),currentPairEvidence=rel(D/'execution.json'),lookdev='50 Three.js and8 Manim assets; appropriate2D ranges retained. Current changed encoded pixels and motion reviewed; unchanged GOP evidence reused.')
 p['revisionInProgress'].update(status='reviewed-awaiting-private-upload',newOutputVerified=True)
 p['productionGates'].update(finalRendered=True,allEncodedPixelsReviewed=True,outputCollected=False,uploaded=False)
 p['finalRender'].update(outputs=e['outputs'],technicalEvidence=rel(D/'execution.json'),pixelEvidence=rel(D/'combined-review.json'))
 oldreceipt=P/'publishing/youtube-receipt.json';snapshot=P/'publishing/youtube-receipt-baseline-ZUrPmDV-bSQ.json'
 assert not snapshot.exists();snapshot.write_bytes(oldreceipt.read_bytes())
 p['publishing'].update(videoId=None,url=None,receipt=rel(P/'publishing/youtube-receipt-threejs-v1.json'),automaticChecks='not-started')
 wr(P/'project.json',p)
 ledger['rendererRevision'].update(newVideoVerified=True,technicalEvidence=rel(D/'execution.json'),encodedReview=rel(D/'combined-review.json'),unchangedAudioAsrReused=True)
 ledger.update(localProductionComplete=True,privateUploadComplete=False,deliveryComplete=False,gitDeliveryComplete=False)
 wr(P/'production/review-ledger.json',ledger)
 c=rd(P/'production/checkpoint.json');c.update(updatedAt=now,stage='threejs-reviewed-ready-to-collect',activeOwnedHeavyJob=None,nextAction='Collect four files and privately upload reviewed captioned revision once; save/reopen settings, selectively push and stop.')
 c['rendererRevision'].update(status='reviewed-pair',fullVideoRendered=True,newOutputVerified=True,newUploadComplete=False)
 c['gates'].update(finalRenderComplete=True,allFinalCaptionPixelsReviewed=True,collected=False,uploaded=False)
 wr(P/'production/checkpoint.json',c)
 u=rd(P/'publishing/upload-package-v1.json');u.update(status='reviewed-threejs-ready-to-collect',videoId=None,baselineVideoId='ZUrPmDV-bSQ',planSha256=sha(D/'plan.json'),captionedSha256=e['outputs']['captioned']['sha256'],receipt=p['publishing']['receipt'],descriptionKo=(P/'publishing/description.ko.txt').read_text(),descriptionEn=(P/'publishing/description.en.txt').read_text(),fullSettingsVerified=False)
 wr(P/'publishing/upload-package-threejs-v1.json',u)
 print('Registered reviewed revision; baseline retained, no upload yet.')
if __name__=='__main__':main()
