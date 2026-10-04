"""Record the directly reviewed new15 text; preserve every current14 script/PCM."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PROJECT=BASE.parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat()
ko=read(PROJECT/'script/narration.ko.json');en=read(PROJECT/'script/narration.en.json')
assert len(ko['scenes'])==len(en['scenes'])==15
for lang,d in [('ko',ko),('en',en)]:
 old=read(BASE/f'narration-script-{lang}-14-preserved.json')
 assert [s for s in d['scenes'] if s['id']!='15']==old['scenes']
current=read(BASE/'narration-expanded-index.json')
for x in current['measurements']:assert sha(ROOT/x['path'])==x['sha256']
proposal=read(BASE/'native-cue-proposal.json');new=next(x for x in ko['scenes'] if x['id']=='15')
groups=[g for g in proposal['groups'] if g['sceneId']=='15']
chapter=dict(id='15',title=new['title'],role='actual-existing-game',claim='보인 행동을 공간과 대상과 함께 구체적으로 전달하고 짧은 시연에 없는 조건은 정하지 않는다.',
 diagram='그림면/가상책상·이동/공격·목표를 구별하는 실제행동 적용; 마지막12결론 전에 삽입',
 sourceActionIds=[c['id'] for g in groups for c in g['sourceCuts']],measuredSeconds=None,
 newCommentaryOnly=True,finalCutAndCaptionApproval=False,nativeCueProposal=rel(BASE/'native-cue-proposal.json'))
p=PROJECT/'planning/chapter-plan.json';d=read(p)
assert not any(x['id']=='15' for x in d['chapters'])
i=next(i for i,x in enumerate(d['chapters']) if x['id']=='12');d['chapters'].insert(i,chapter)
d.update(updatedAt=now,sceneOrder=[x['id'] for x in ko['scenes']],nativeCueProposal=rel(BASE/'native-cue-proposal.json'),finalCutAndCaptionApproval=False)
save(p,d)
p=PROJECT/'sources/action-map.json';d=read(p);save(BASE/'action-map-v4-preserved.json',d)
i=next(i for i,x in enumerate(d['chapters']) if x['id']=='12');d['chapters'].insert(i,copy.deepcopy(chapter))
d.update(updatedAt=now,status='native-cue-reassignment-proposal-new15-voice-pending',nativeCueProposal=rel(BASE/'native-cue-proposal.json'),nativeCueUniqueSecondsProposed=proposal['sourceUniqueSeconds'],ratioApproved=False,finalCutAndCaptionApproval=False)
save(p,d)
p=BASE/'script-source-review.json';d=read(p);save(BASE/'script-source-review-v3-preserved.json',d)
newen=next(x for x in en['scenes'] if x['id']=='15')
scene=dict(id='15',role='actual-existing-game',paragraphs=[dict(paragraph=i+1,koSha256=hashlib.sha256(k.encode()).hexdigest(),enSha256=hashlib.sha256(e.encode()).hexdigest(),sourceActionIds=[c['id'] for c in groups[i]['sourceCuts']],meaningOrderAndClaimScopeDirectlyCompared=True) for i,(k,e) in enumerate(zip(new['lines'],newen['lines']))],directReview='All four paired paragraphs were read against the already inspected page combat/platforms, virtual-desk traversal/attack, Pepper water/lava/shooting and mine dodging/attacks. Targets and settings are stated; inputs, universal combat rules and developer pitch claims are not inferred.',planningSourceSeconds=sum(g['sourceSeconds'] for g in groups),measuredNarrationSeconds=None)
i=next(i for i,x in enumerate(d['scenes']) if x['id']=='12');d['scenes'].insert(i,scene)
for x in d['inputs']:x['sha256']=sha(ROOT/x['path'])
for p2 in [BASE/'native-cue-proposal.json',BASE/'native-cue-commentary-text-review.json']:
 d['inputs'].append(dict(path=rel(p2),sha256=sha(p2)))
d.update(updatedAt=now,reviewedAt=now,status='15-scenes60-paragraphs-independent-bilingual-text-reviewed-new15-CPU-TTS',method='Preserved all14 reviewed paired scripts and current PCM, then directly read the four new paired paragraphs, source-native action scope and unchanged overview/conclusion promises. Final source framing, all captions and body ratio remain pending.',sceneCount=15,paragraphs=60,wholeBilingualScriptReviewed=True,wholeBilingualTextChangedOnlyScene15=True,previousTextReview=rel(BASE/'script-source-review-v3-preserved.json'),new15VoiceAsrReview=False,nativeCueProposal=rel(BASE/'native-cue-proposal.json'))
save(p,d)
p=PROJECT/'project.json';d=read(p)
d.update(status='new15-only-CPU-voice-measurement-native-cue-proposal')
d['production'].update(pendingNarrationExpansion=True,currentVoiceApproved=False,current14VoiceTechnicallyReviewed=True,newScene15VoiceApproved=False,newScene15Request=rel(BASE/'native-cue-narration-request.json'),nativeCueProposal=rel(BASE/'native-cue-proposal.json'),finalTimingApproved=False)
save(p,d)
print(json.dumps(dict(scenes=15,pairedParagraphs=60,preserved14ScriptAndPcm=True,finalTimingApproved=False)))
