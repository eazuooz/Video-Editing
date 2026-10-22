"""Persist current observed camera-cue limits; not an adoption or completion."""
import datetime
from polish_common import *
e=Episode('M17');e.authorized();p=e.H/'camera-cue-candidate-647.json';d=read(p)
save(e.H/'camera-cue-candidate-review.json',{'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'partial-cue-match-needs-zoom-retiming','candidate':rel(p),'candidateSha256':sha(p),
 'directInspection':'All37 candidate stills on8 sheets viewed: orbit3/higher2/end3. Half-second sampling in the orbit/higher windows; one-second or selected samples in the ending. Not continuous playback.',
 'observed':[
  {'speechWindow':[13.46,20.12],'sourceWindow':[660.46,667.12],'finding':'Camera visibly turns around the same tower at660–661.5; the front long roof overlaps its lower facade. The roof/top remains visible. Use the precise observed overlap, not a claimed internal clipping test.'},
  {'speechWindow':[26.36,33.96],'sourceWindow':[673.36,680.96],'finding':'673.5–675 source shows a higher view and inside terraces; later construction changes are also visible. Same building must remain the reference.'},
  {'speechWindow':[81.52,88.58],'sourceWindow':[728.52,735.58],'finding':'Orbit/construction remains during this sentence. The wide zoom is seen at736.5, later than the current speech; closer zoom at743. Whole647-start candidate is not ready to adopt.'}],
 'nextAction':'Adjust only internal source excerpts in scene14 to place the observed736.5 wide zoom /743 close view under the81.52–88.58 sentence; inspect new boundaries and retain6156 frames. Keep original626-start source untouched until review.',
 'fullMasterReady':False,'sourceAdopted':False,'narrationChanged':False,'humanReview':'pending'})
print('M17 orbit and higher-view match observed; zoom mismatch explicitly remains.')
