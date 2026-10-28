"""Record completed direct reviews and exact unchanged-frame evidence, honestly scoped."""
from pathlib import Path
from datetime import datetime,timezone
import audio_pipeline as a
H=Path(__file__).resolve().parent
def main():
 plan=a.read(H/'edit-plan.contrast-v2.json');out=a.repo_path(plan['outputDir']);evidence=a.read(out/'qa/v1/evidence.json');structure=a.read(out/'structural-verification.json');identity=a.read(H/'final-frame-preservation.json')
 assert structure['status']=='pass' and evidence['allCaptionCuesCovered']
 assert evidence['captionedMp4']['sha256']==structure['outputs']['captioned']['sha256']==identity['newMaster']['sha256']
 # Completed by this agent: every sheet for these five correction cuts and
 # the two otherwise unchanged photo cuts with expected encoding differences.
 direct=['c025','c026','c027','c030','c032','c029','c031']
 native=['00667.jpg','00677.jpg','00699.jpg','00768.jpg','00797.jpg','00758.jpg','00779.jpg']
 records={cid:{'mobileSheets':evidence['cuts'][cid]['mobileSheets'],'sampledStates':evidence['cuts'][cid]['nativeFrames'],'captionCues':evidence['cuts'][cid]['overlappingCaptionCues'],'result':'Directly viewed: target/action/result, motion-state progression, fixed captions and boundary continuity pass.'} for cid in direct}
 gameplay=a.read(H/'gameplay-final-binding.json')
 assert gameplay['status']=='passed-final-gameplay-sampled-visual-review'
 assert gameplay['captionedMp4']['sha256']==evidence['captionedMp4']['sha256']
 records['c029']={'sampledStates':[r for r in evidence['cuts']['c029']['nativeFrames'] if r['frame']==20527],'mobileSheets':[a.relative(out/'qa/v1/c030-375-01.jpg')],'result':'The sole nonidentical c029 frame20527 was directly viewed in1080 and as the adjacent first375 state of c030. Other c029 states transfer by exact pixel identity.'}
 review={'schemaVersion':1,'status':'pass','masterSha256':evidence['captionedMp4']['sha256'],'master':evidence['captionedMp4'],'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewedCutIds':[c['id'] for c in plan['cuts']],'allCaptionCuesReviewed':True,'captionCueCount':113,'native1080AndMobile375Reviewed':True,'evidence':a.artifact(out/'qa/v1/evidence.json'),'uniqueExtractedFrames':870,'reviewScope':'Direct sampled frame/cue/motion-state review and exact unchanged-pixel transfer; not continuous human viewing or listening.','directDeltaAndCompressionDifferenceReview':records,'native1080DirectlyViewed':[a.artifact(out/'qa/v1/frames'/f) for f in native],'unchanged18ExplanationReview':a.artifact(H/'unchanged-explanation-visual-review.json'),'independentGameplayReview':a.artifact(H/'gameplay-final-binding.json'),'unchangedFrameComparison':a.artifact(H/'final-frame-preservation.json'),'unchangedFrameTransfer':{'sampledFrames':748,'identicalFrames':733,'differentFrames':15,'differentCuts':['c029','c031'],'maxMean8bitDifference':identity['maximumMeanDifference'],'disposition':'All 15 nonidentical states were directly rechecked in complete c029/c031 final sheets and representative1080. Same decoded source/caption clock and source image details; minor compression differences, no shifted content.'},'nativeContrastRepairProof':'production/batches/design-25-30-review-actions-20261029/contrast-repair/representative-pixel-proof.json','parentSpotChecks':['Original color/gray/restoration layout and exact modified background-tree comparison','Actual encoded c011/c012 proof','Corrected c028 narrow distant-scenery rectangle'], 'conclusions':['Same objects/camera survive grayscale, shape/brightness/pattern changes and color restoration. Grayscale explicitly remains a brightness check.','Background tree brightness range actually compresses; path/chest edges remain legible and restored leaves/trunks remain green/brown.','Tracked actual-game annotations follow verified targets and clear at source cuts. Narrow c028 distant-cliff box excludes foreground coins/water/player.','All relevant clause captions, measured cue boundaries and cut joins are sampled in the evidence; no caption/layout overlap found.'],'humanWholeReview':'pending','humanWholeListening':'pending'}
 a.save(H/'visual-review.json',review)
 for file in ['audio-review.json','final-comparison-review.json']:
  row=a.read(H/file);assert row['encodedAudioPacketsSha256']==structure['outputs']['captioned']['audioPacketsSha256']
  row['finalCorrectedMasterBinding']={'masterSha256':review['masterSha256'],'identicalAudioPackets':True,'proof':a.artifact(out/'structural-verification.json'),'recognitionRerun':False,'sameOriginalAsrEvidence':True}
  a.save(H/file,row)
 print('Final direct visual review and unchanged AAC evidence bound to corrected master.')
if __name__=='__main__':main()
