"""Record only the root agent's already viewed final picture evidence."""
from subject_revision import *
import qa,progress,review_delivery

NOTES={
 'M33': ['Viewed both fresh corrected encoded boards covering all28 first/15/50/85% pictures of003,018,020,024,026,042,029. Train-path photos accompany the original spline, tangent and boundary-condition diagrams; native train footage remains intact.',
         'Viewed corrected final029 landing and exact657.6167s apex at1080p and375px, plus12 encoded jump positions and mobile snapshot. The character head and feet are complete; symbolic conditions and staged derivation remain visible. Backings now render before the character.',
         'The fixed apex marker briefly touches the moving cap just after the peak; the face and equation remain recognizable. At exact003 first frame, an outgoing original ASS formula tail is still present for a single60fps frame. Original math ASS is deliberately byte-preserved; narrative reading frames are clear.',
         'Compared the replaced bad backing attempt against actual newly encoded Clean/Captioned apex and landing. This is sampled internal inspection, not full human viewing or a new voice review.'],
 'M32': ['Viewed both fresh encoded boards covering all20 first/15/50/85% pictures of001,003,010,015,029. Mario Maker route image accompanies the original control-point, interpolation, global-support and subdivision constructions without covering mathematics or captions.',
         'Viewed final003 at85% in1080p and375px: all construction points, p(t), algorithm heading and actual route picture remain visible. The image is labeled as a route example alongside our Bézier principle model.',
         'Viewed12 final010 positions plus mobile snapshot: only the selected control input changes while the curve and evaluated point update together; native gameplay elsewhere is preserved.'],
 'M31': ['Viewed both fresh encoded boards covering all20 first/15/50/85% pictures of001,005,013,033,034. Native Mario Maker preface remains animated; subsequent original point/curve formulas accompany the Satisfactory source path without occlusion.',
         'Viewed final013 at50% in1080p and375px: source train/rail, p(t), tangent and curvature formula remain separated from captions.',
         'Viewed12 final013 positions plus mobile snapshot: moving sample point and tangent follow the original varying circle, while the game-image correspondence stays clear. Existing parameterization and narration order preserved.'],
 'M30': ['Viewed the fresh encoded board containing first/15/50/85% of017,057,058,059. BeamNG source photo accompanies the original component-mass vehicle model; centroid and inertia formulas, component masses and caption area remain unobscured.',
         'Viewed final057 at85% in1080p and375px; vehicle-to-component correspondence and the full centroid expression remain readable.',
         'Viewed12 final017 positions plus its375px snapshot: source/model caption, reference marker and part masses stay stable through the original continuous narration. This revised context does not replace the retained native gameplay.'],
 'M28': ['Viewed the fresh encoded board with first/15/50/85% of002,010,024. Chomp source image now occupies blank upper-center; the original symbolic formula, units and final substitution all remain visible.',
         'Viewed corrected final002 at85% in1080p and375px. Photo, source/model label, spring object, calculation and captions do not overlap.',
         'Viewed12 final010 positions and mobile snapshot: BeamNG image follows the same spring displacement, rebuilt coil, restoring/damping arrows and synchronized graph. No robot or masking debris observed.'],
 'M29': ['Viewed the one fresh encoded QA board containing first/15/50/85% of006,019,021,022. Game collision photo accompanies unchanged contact-normal, impulse and relative-speed diagrams without hiding formulas.',
         'Viewed actual encoded022 at85% in1080p and375px; caption, separating contact, vn inequality and game/model correspondence remain clear.',
         'Viewed12 encoded019 positions: contact normal and object labels reverse together, relative directions and unchanged caption timing agree; no robot introduced.'],
}
def main(eid):
 e=EPISODES[eid];p=work(e);assert eid in NOTES
 for folder in ('full-picture-qa','motion-qa'):
  for receipt in (p/folder).glob('*/evidence.json'):
   v=read(receipt);v.update(actuallyInspected=True,reviewNotes=NOTES[eid],humanReviewed=False);save(receipt,v)
 qa.record(e,NOTES[eid]);progress.update()
 title=next(row['title'] for row in read(HERE/'progress.json')['rows'] if row['id']==eid)
 print(review_delivery.page(e,read(p/'encoded.json'),title));progress.update()
if __name__=='__main__':main(sys.argv[1])
