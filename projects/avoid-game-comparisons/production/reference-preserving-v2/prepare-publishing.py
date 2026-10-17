from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';V=P/'production/reference-preserving-v2';O=P/'publishing/reference-preserving-v2';O.mkdir(exist_ok=True)
plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));design=json.loads((P/'planning/chapter-plan.json').read_text(encoding='utf8'))['currentRevision'];ko=json.loads((P/'script/reference-preserving-v2/narration.ko.json').read_text(encoding='utf8'));en=json.loads((P/'script/reference-preserving-v2/narration.en.json').read_text(encoding='utf8'))
def stamp(v):n=int(v);return f'{n//60:02}:{n%60:02}'
starts={s['id']:s['startFrame']/60 for s in plan['scenes']}
credits='\n'.join(design['publishingDraft']['credits'])
for lang,script,intro in [('ko',ko,'마리오 같다는 말로 게임을 설명하면, 상대도 같은 플레이를 떠올릴까요? 횡스크롤 점프와 캡처를 사용하는 실제 장면을 살펴보고, 기획을 목표·행동·조건과 결과로 구체화합니다. 상대가 자기 말로 설명한 플레이를 확인하는 방법까지 연결합니다.'),('en',en,'Does “like Mario” make another person imagine the same game? We compare side-scrolling jumps with capture-based abilities, then describe a concept through goals, actions, conditions and outcomes. A listener’s retelling helps reveal which actions the explanation left out.')]:
 chapters=['00:00 '+('얌얌코딩 · 같은 이름, 다른 플레이' if lang=='ko' else 'Yamyam Coding · one name, different play')]+[stamp(starts[s['id']])+' '+s['title'] for s in script['scenes'][1:]]+[stamp(plan['totalFrames']/60-10)+' '+('멤버쉽가입 감사드립니다.' if lang=='ko' else 'Membership thanks')]
 old=(P/f'publishing/description.{lang}.txt').read_text(encoding='utf8');footer=old[old.index('🎮'):]
 (O/f'description.{lang}.txt').write_text(intro+'\n\n'+'\n'.join(chapters)+'\n\n'+footer+'\n\n'+('영상·음원 크레딧\n' if lang=='ko' else 'Footage and music credits\n')+credits+'\n',encoding='utf8')
(O/'metadata.json').write_text(json.dumps({'revision':design['id'],'title':design['selectedTitle'],'titleCandidates':design['titleCandidates'],'thumbnail':design['publishingDraft']['thumbnailReuse'],'captionedMasterRequired':[1920,1080,60],'manualKoEnCaptions':True,'coachingCardAt':'00:00','membershipEndScreenSeconds':10,'privacyAfterReview':'private','userReview':'pending current completed local master','youtubeUploadAuthorized':False,'existingVideoPreserved':'cQE7_ygx_XM','credits':design['publishingDraft']['credits']},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Bilingual publishing drafts prepared; no platform settings changed')
