"""Use a reviewed extra1.5s of the same placed result after measured narration."""
from pathlib import Path
import copy,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
proof=read(ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/native-source-extension-179-184.json')
assert any(x['in']==179 and x['requestedOut']==184 and x['rate']==1 and x['normalSpeedReachedEnd'] for x in proof)
data=read(R/'additions.json');before=copy.deepcopy(data);changed={}
for s in data['scenes']:
 if s['id'] not in ['QF20','QC20']:continue
 assert s['intervals'][-1]==[178.9,181.9]
 s['intervals'][-1][1]=183.4;s['sourceSegments'][-1]['maxSeconds']=4.5;s['maximumSeconds']=9.6
 s['selection']['extensionAfterMeasuredVoice']='Reviewed extra1.5s of the placed result for side-face inspection; exact game speed, same operation, no frozen frame or loop.'
 s['annotation']['tracksPrepared']=False;s['annotation']['movingPixelApproval']=False
 changed[s['id']]=copy.deepcopy(s)
write(R/'before-gear-result-extension.json',before);write(R/'additions.json',data)
for e in read(R/'baseline.json')['episodes']:
 p=ROOT/'projects'/e['newSlug'];lesson=read(p/'production/lesson.json')
 lesson['scenes']=[copy.deepcopy(changed.get(s['id'],s)) for s in lesson['scenes']]
 old=read(R/'baseline'/e['slug']/'production/lesson.json')['scenes'];ids={s['id'] for s in old}
 assert [s for s in lesson['scenes'] if s['id'] in ids]==old;write(p/'production/lesson.json',lesson)
for lang,sha in read(R/'pretts-frozen-audit.json')['scriptSha256'].items():
 assert hashlib.sha256((ROOT/f'projects/game-math-quaternion-cross-game-additions-v3/script/narration.{lang}.json').read_bytes()).hexdigest()==sha
selection=read(R/'candidate-comparison.json')
for item in selection['selectedForLocalDraft']:
 if item['game']=='Space Engineers':
  item.pop('interval',None);item['intervals']=changed['QF20']['intervals'];item['sourceSegments']=changed['QF20']['sourceSegments'];item['extraNormalSpeedProof']='shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/native-source-extension-179-184.json'
write(R/'candidate-comparison.json',selection)
write(R/'gear-result-extension-review.json',dict(recordedAt=datetime.datetime.now().astimezone().isoformat(),normalSpeedAndCropInspected=True,additionalActualSeconds=1.5,why='Measured foundations explanation82.92s requires55.28s total added action; source capacity54s was1.28s short. Retain narration and approve1.5s of a clear result/side-face inspection.',masterSpeechScriptsStillFrozenExact=True,original80Exact=True,movingTrackAndFinalCaptionReview='pending'))
print('Extended only the reviewed placed result to183.4s; all original80 and frozen new spoken lines unchanged.')
