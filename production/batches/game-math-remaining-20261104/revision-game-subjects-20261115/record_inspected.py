"""Record only the root agent's already viewed final picture evidence."""
from subject_revision import *
import qa,progress,review_delivery

NOTES={
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
