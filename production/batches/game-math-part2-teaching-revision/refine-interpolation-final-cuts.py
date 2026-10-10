"""Preserve the narration; finish the already reviewed board action at native speed."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
paths=[B/'interpolation-game-insertions.json',ROOT/'projects/game-math-interpolation-paths-v2/production/lesson.json']
for path in paths:
    data=json.loads(path.read_text(encoding='utf8'))
    scene=next(s for s in data['scenes'] if s['id']=='IG07')
    scene['intervals']=[[144,152.6],[197.8,207.8]]
    scene['maximumSeconds']=18.6
    scene.setdefault('selection',{}).update(
        finalRangeReason='Direct final pixels rejected the198.5–208.5 cut: a new jump starts at208.0 and the cut ends airborne. Fine0.5-second source review shows202.5–203.5 flip,204.0 first landing,205.0–206.5 second flip,207.0–207.8 upright roll before the next jump. Shift the same native10-second window to197.8–207.8 inside the already fully played193–208.5 candidate. Keep voice, duration, separate-cut warning and speed unchanged.',
        finalVisibleBeforeActionAfter='197.8 upright approach →202.5–203.5 board flip →204.0 landing →205.0–206.5 second flip →207.0–207.8 upright rolling result; stop before208.0 new jump',
        rejectedFinalCut={'interval':[198.5,208.5],'reason':'Final moving pixels end during a new backflip, not a completed action. Previous claimed upright208.5 was incorrect.','captionedSha256':'011e69dc599b4e6309cf9fb2ca2800e74c67b7b1beb62c257d0da259fd8193e4','fineSourceReview':'shared/output/game-math-part2-teaching-revision/interpolation/landing-review'},
        finalNativeMovingAnnotationApproval=False)
    scene=next(s for s in data['scenes'] if s['id']=='IG02')
    scene['intervals']=[[116,140]]
    scene['maximumSeconds']=24
    scene.setdefault('selection',{}).update(
        finalRangeReason='Move the measured23.6-second excerpt within the already fully played109.5–140 interval: the former end133.1 began another jump. Start116 and finish139.6 so viewers see the117–120 and127–131 actions and upright result139.',
        finalVisibleBeforeActionAfter='116 approach →117–120 body/board jump and landing →127–131 second turn and landing →upright139',
        finalNativeMovingAnnotationApproval=False)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('IG07 second excerpt now includes the reviewed flip and landing; final moving review remains pending.')
