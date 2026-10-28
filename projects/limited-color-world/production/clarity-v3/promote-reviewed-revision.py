"""Promote the verified correction plan without replacing earlier media/evidence."""
from pathlib import Path
import json
from datetime import datetime,timezone
import audio_pipeline as a
H=Path(__file__).resolve().parent
def main():
 plan=a.read(H/'edit-plan.contrast-v2.json');out=a.repo_path(plan['outputDir'])
 structure=a.read(out/'structural-verification.json');visual=a.read(H/'visual-review.json')
 assert structure['status']=='pass' and visual['status']=='pass'
 assert visual['masterSha256']==structure['outputs']['captioned']['sha256']
 active=H/'edit-plan.json';baseline=H/'edit-plan.before-contrast-v2.json'
 assert active.read_bytes()==baseline.read_bytes() or a.read(active)==plan
 active.write_bytes((H/'edit-plan.contrast-v2.json').read_bytes())
 receiptPath=a.ROOT/'production/batches/design-25-30-review-actions-20261029/D25-contrast-repair-native-receipt.json'
 receipt=a.read(receiptPath);now=datetime.now(timezone.utc).isoformat()
 preservation={'priorDeliveryMediaUntouched':True,'firstClarityPairUntouched':True,'nativeMoviesAndSceneFilesUntouched':True,'vendorInputsUntouched':True,'generatedAssetException':'17 prior c032 private material hashes changed at refresh/save; actual current bytes retained. No speculative recovery or claim that every generated asset stayed byte-identical.','proof':'production/batches/design-25-30-review-actions-20261029/contrast-repair/representative-pixel-proof.json'}
 p=a.read(H/'production-plan.json');p['status']='internal-qa-complete-local-collection';p['updatedAt']=now
 p['preservation']['contrastRepairPreservation']=preservation
 u=p['unity'];u.update(editor='6000.6.0f1 (f7f8ed4d1e24), installed ProjectVersion verified',pipeline='URP17.6, installed package verified',savedSceneStatus='18 independently editable saved scenes exist; 13 measured-v1 and 5 ContrastV2 scenes',nativeRuntimeVerifiedForNewRevision=True,measuredNativeCutCount=18,timingLocked=True)
 u['savedScenes']=[{'cutId':c['id'],'path':('unity/VideoEditing/'+a.read(a.repo_path(c['renderedSource']).parent/'render-success.json')['scene'])} for c in plan['cuts'] if c.get('renderedSource')]
 assert len(u['savedScenes'])==18
 u['capture']['timingLocked']=True
 u['actualImplementation']=['World-only URP StandardRequest; fixed camera, real object materials and articulated actor','ColorAdjustments.saturation -100 to 0 is a brightness check, not a color-vision simulation','Background-tree-only final-lit luminance compression; foreground and global lights unchanged','One FlushPoses after Apply per frame','Postcomposite measured brand UI and factual photos; fixed captions applied in final pair']
 u['sourceFingerprintEvidence']=a.artifact(receiptPath)
 for row in u['assetRecords']:
  if row['key']=='tree':row['privatePalettePurpose']='Verified green leaves/brown trunks from lossless actual PSD pixels; preserve mesh/UVs/vendor inputs. New private ContrastV2 shader compresses background final-lit luminance only in five specified cuts.'
 p['rendererRevision']['sourceStage']=a.artifact(H/'unity-src/D25ColorClarityStage.cs')
 p['rendererRevision']['actualRenderedPixels']='Complete native18 and final encoded35 cuts inspected at native1080/mobile375; source/cue/transition evidence in visual-review.json.'
 p['rendererRevision']['stableMaterialInstances']['nativeProof']='Full native rendering completed; private source preservation exception is explicitly recorded.'
 p['rendererRevision']['stableMaterialInstances']['preserved']=[x for x in p['rendererRevision']['stableMaterialInstances']['preserved'] if x!='all previously generated material assets']
 p['rendererRevision']['compositionColorEncoding']['verification']='Both actual final masters decoded as limited BT.709; corrected color/gray/restoration pixels directly reviewed.'
 p['rendererRevision']['contrastRepair']={'reason':'Earlier tree darkening increased internal contrast; narration requires reducing bright/dark differences. Compress only final-lit background-tree luminance while keeping hue and foreground unchanged.','cutIds':['c025','c026','c027','c030','c032'],'source':a.artifact(H/'unity-src/D25BackgroundContrast.shader'),'nativeReceipt':a.artifact(receiptPath),'pixelProof':preservation['proof'],'preservation':preservation}
 p['rendererRevision']['annotationRepair']={'cutId':'c028','evidence':'c028-correction-visual-review.json','scope':'Only two nested distant-scenery rectangles; same source, offsets, duration, marks style and caption/audio clock.'}
 p['audio']['finalReview']='audio-review.json';p['audio']['fullFinalAsrReview']='final-comparison-review.json';p['audio']['correctionReusesExactContinuousAac']=True
 p['delivery']['finalUserReview']='Pending actual user whole-video review of verified new four-output version'
 p['qaCompleted']={'structural':a.artifact(out/'structural-verification.json'),'visual':a.artifact(H/'visual-review.json'),'audio':a.artifact(H/'audio-review.json'),'speechMeaning':a.artifact(H/'final-comparison-review.json'),'finalPlan':a.artifact(active)}
 a.save(H/'production-plan.json',p)
 cp=a.read(H/'checkpoint.json');cp.pop('oldVersionsChanged',None);cp.update(status='internal-qa-complete-local-collection',updatedAt=now,sourceStageSha256=a.sha(H/'unity-src/D25ColorClarityStage.cs'),oldDeliveriesChanged=False,contrastRepairPreservation=preservation)
 cp['complete']+=['Complete35cut paired encoding','24,018-frame full PTS/audio/video verification of both masters','All113caption cues and35cut actual encoded visual evidence','One complete finalAAC ASR, direct full-script comparison and bounded229s decoder-artifact resolution','Same approved audio packet hash retained during six-cut visual repair']
 cp['pending']=['four-output collection','actual user whole-video review']
 cp['audio']['finalMix']['finalFullAsr']='pass with full-text direct comparison and bounded concrete-failure resolution; audio-review.json'
 cp['measuredTiming']['captionsAndPixels']='pass final visual-review.json';cp['captionQa']['finalEncodedPixels']='pass all113cues'
 cp['nativeQa']['repairPixelVerification']='pass final native plus actualencoded35cut evidence'
 cp['nativeQa']['fullCapture']['selectedFinalReceipt']=a.artifact(receiptPath)
 cp['nativeQa']['stableMaterialInstances']['nativeProof']='complete native18; precise generated-asset preservation exception recorded'
 cp['compositionPrepared'].update(newUiOverlayEncoderExecuted=True,newMixExecuted=True,finalPairExecuted=True)
 a.save(H/'checkpoint.json',cp)
 print('Verified correction plan promoted; prior media/evidence retained; collector still required.')
if __name__=='__main__':main()
