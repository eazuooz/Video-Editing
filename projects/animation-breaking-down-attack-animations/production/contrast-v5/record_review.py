"""Record the performed current-encoded image inspection; not a full human watch."""
from prepare import H,L,read,save,sha
def main():
 q=read(L/'qa.json')
 assert all(not p.read_bytes().strip() for p in (L/'qa').glob('*.decode.log'))
 review={
  'revision':'contrast-v5','status':'sampled-current-encoded-visuals-reviewed',
  'masterSha256':q['technicalChecks']['captioned.mp4']['sha256'],
  'reviewer':'Codex direct image inspection',
  'reviewedSamples':q['visualSamples'],
  'inspectedFull1080':['four-phase','preparation-guide','hit-stop-guide','follow-through-guide','control-difference'],
  'mobileSheet':str(L/'qa/mobile-sheet.jpg'),
  'mobileWidth':375,
  'observations':[
   'The four actual UE poses are visibly different: baseline stance, raised arms/weapon, target contact posture, and bent torso during follow-through. The current phase has a matching colored outline and label.',
   'The enlarged analysis uses one scene instead of duplicated left/right scenes. Its resting/impact skeleton, current arm joints and hand path are separately visible; the subject and phase labels remain recognizable at 375 px.',
   'The figure feet end above the phase strip; the foot-position marker is inside the scene. Fixed burned captions below the strip do not cover the pose, active-phase label or four-panel descriptions in the reviewed frames.',
   'The impact sample displays active evaluation and conditional hit-stop separately from the pose label. These are marked as the authored demonstration rules, not measured commercial-game data.',
   'The only retained paired view shows distinct behavior: the 48-frame version continues its attack pose while the 36-frame version has entered a real running animation. Its input thresholds are separately labeled.',
   'Three native-pass samples visibly carry 1/3, 2/3 and 3/3 markers. Successive native/slow samples show stance, raised arms, contact, follow-through and return; the post-analysis sample returns to the retained independent gameplay.'
  ],
  'motionReviewScope':'Selected encoded frames at successive timestamps plus source-frame mapping, exact skeletal-track projection proof and full technical decode. Not an uninterrupted human playback review.',
  'technicalQA':str(L/'qa.json'),
  'sourceJointProof':str(H/'joint-guide-proof.json'),
  'resolvedFindings':[
   {'issue':'Analysis viewport originally overlapped the phase strip at the feet','resolution':'Viewport height limited to 640, ending at y818 before the strip at y839; final encoded samples checked.'},
   {'issue':'A map insertion split cut-08 into two ranges sharing a file name, detected by exact frame-count gate','resolution':'Unique part names and original full-cut source offsets; 14+110 frames replace exactly 124, final duration 26858 frames.'}
  ],
  'newTTS':False,'newASR':False,'aacAndSrtBytesPreserved':True,
  'fullWatch':False,'fullHumanListening':False,'humanReview':False,
  'remainingReview':'User final review of the complete local A03 revision.',
 }
 save(H/'visual-review.json',review)
 save(H/'technical-qa.json',q)
 print('Recorded 19 encoded sample observations; human final review remains pending.')
if __name__=='__main__':main()
