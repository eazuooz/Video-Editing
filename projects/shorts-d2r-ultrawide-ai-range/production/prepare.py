"""Create the three explicitly selected Diablo technical Shorts; no media jobs.

Narration stays provisional until inspected independent footage is linked.
Run once; reruns refuse to replace existing authored files.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
REVISION = 'distinctive-ten-v1'
DATA = [
    dict(slug='shorts-d2r-ultrawide-ai-range',topic='ultrawide',
         title='모니터를 넓혔더니 몬스터가 반격을 못 했다? | 디아블로2 개발 이야기',
         titleEn='A wider screen broke monster reactions? | Diablo II development',
         head=['화면을 넓혔더니','몬스터가 반격을 못 했다?'],
         term=['AI Reaction Range','AI 반응 범위'],
         source='https://www.bluetracker.gg/diablo3/topic/us-en/44360-diablo-ii-resurrected-console-lobbies-tcpip-uw-updates/',
         evidence='Blizzard community-team statement, 2021-09-07, Ultrawide Support Changes, all paragraphs read. Original forum is unavailable; preserved official statement is the evidence.',
         sourceScope='2021 Technical Alpha and release-era 19:9 decision, not a present-day exploit.',
         stages=['game','view','range','attack','limit','answer'],
         paragraphs=[
             [('화면이 넓어졌을 뿐인데,','Just widening the screen'),('몬스터가 맞고도 반격을 못 했습니다.','left monsters taking hits without reacting.'),('디아블로 투 레저렉션의 이천이십일 년 테스트에서 생긴 일이에요.','This happened in Diablo II: Resurrected’s 2021 test.')],
             [('원리를 단순하게 그려볼게요.','Here is a simplified reconstruction.'),('캐릭터와 몬스터는 그대로 두고,','Keep the player and monster in place.'),('화면만 옆으로 넓히면 더 먼 적이 보이죠.','Widening the view reveals a more distant enemy.')],
             [('하지만 화면에 보이는 범위와,','But what the player can see'),('몬스터가 플레이어에게 반응하는 범위는 다른 규칙입니다.','and when the monster reacts are separate rules.')],
             [('당시에는 넓어진 화면 끝의 적을 공격할 수 있었지만,','In that test, players could hit enemies in the extra screen area,'),('그 거리에서는 적의 반응이 시작되지 않았어요.','but the enemies did not react at that distance.'),('보이니까 쏠 수 있는데, 맞는 쪽은 가만히 있었던 거죠.','You could attack what you saw while the target stayed passive.')],
             [('그래서 개발진은 출시 때 보이는 폭을 십구 대 구로 제한했습니다.','For release, the team limited the view to nineteen by nine.'),('화면 양옆을 어둡게 처리해서,','Darkened edges kept the view'),('기존 전투 규칙이 감당하는 범위에 맞춘 거예요.','within the limits of the established combat rules.')],
             [('더 넓게 보여 주는 기능도,','Even a wider display option'),('게임 속 적이 반응하는 방식까지 함께 설계해야 했던 겁니다.','had to account for how enemies respond.')],
         ],
         requiredFootage='Independent or official-distributed actual D2R ranged combat for context. Historical defect must use labeled own diagram unless verified alpha footage is acquired.',
         limits=['No invented AI radius or distance number. Rectangle/circle boundaries are explanatory, not recovered game debug data.','Do not portray ordinary current gameplay as the 2021 alpha bug.','Use the whole source aspect ratio; a 21:9 illustration cannot be obtained by stretching a 16:9 source.']),
    dict(slug='shorts-d2r-loot-grass-clearance',topic='grass',
         title='아이템이 풀에 가려지자, 개발자는 풀을 비켜 줬다 | 디아블로2',
         titleEn='Grass hid the loot, so the developers moved the grass | Diablo II',
         head=['아이템이 안 보이자','풀이 비켜 줬다'],
         term=['Vegetation Displacement','식생 변위'],
         source='https://www.playstationlifestyle.net/2021/09/21/behind-diablo-ii-resurrected-authenticity-developer-interview/',
         evidence='Full direct developer interview read; The Guiding Light, Dustin King explains physical grass hiding drops and technology moving grass away.',
         sourceScope='Reported D2R development decision. Exact shader, radius and algorithm are not disclosed.',
         stages=['game','hidden','clear','distance','compare','answer'],
         paragraphs=[
             [('힘들게 잡은 몬스터가 아이템을 떨어뜨렸는데,','You defeat a monster and it drops an item.'),('풀에 가려서 보이지 않는다면요?','What if the grass hides it?')],
             [('디아블로 투 레저렉션에서는 그래픽을 바꾸며 풀이 입체적으로 늘어났습니다.','Diablo II: Resurrected added physical grass to its new visuals.'),('그런데 전리품까지 가려 버리는 문제가 생겼어요.','That grass could also obscure the loot.')],
             [('개발진의 해결책은 아이템이 떨어지면,','Their solution was to move the grass'),('주변 풀을 비켜 주는 기술이었습니다.','out of the way when an item dropped.')],
             [('우리 설명에서는 아이템의 위치를 기준으로,','In our illustration, the item’s position'),('가까운 풀만 바깥쪽으로 움직여 볼게요.','pushes only nearby blades outward.'),('주변은 그대로인데 아이템의 윤곽이 드러나죠.','The surroundings stay, while the item’s silhouette becomes visible.')],
             [('이렇게 식물의 위치나 모양을 바꾸는 걸,','Changing vegetation’s position or shape like this'),('식생 변위라고 설명할 수 있습니다.','is a form of vegetation displacement.'),('여기서 중요한 건 바람보다, 무엇을 보여 줄지였어요.','Here, the important question was what the player needed to see.')],
             [('사실적으로 풀을 늘리는 것만으로는 부족했습니다.','Adding realistic grass was only part of the job.'),('전리품을 찾는 재미까지 지켜야 그래픽 개선이 된 거죠.','The visual upgrade also had to preserve the joy of finding loot.')],
         ],
         requiredFootage='Inspect genuine FHD D2R ground loot in grass. Unless the movement itself is clearly visible, real footage establishes setting/loot only and the response is shown as our illustration.',
         limits=['Descriptive name, not an official proprietary algorithm.','No exact game shader/radius/force claim; own illustration uses an explicit analytic bend.','Do not imply all grass is deleted or all items cause an observable large clearing.']),
    dict(slug='shorts-d2-modular-sprite-equipment',topic='sprites',
         title='디아2는 갑옷을 갈아입을 때 그림 조각을 바꿨다? | 스프라이트의 비밀',
         titleEn='Diablo II changed armor by swapping picture parts | Modular sprites',
         head=['디아2의 장비 교체','그림 조각을 바꿨다?'],
         term=['Component-based Sprites','부품 조합형 스프라이트'],
         source='https://media.gdcvault.com/GD_Mag_Archives/GDM_October_2000.pdf',
         evidence='Original Erich Schaefer postmortem. Game Developer October 2000, printed p54 / PDF p37, modular armor caption; source modeling also confirmed by article body.',
         sourceScope='Original Diablo II renderer, not Resurrected’s modern 3D models.',
         stages=['game','parts','swap','sync','combine','answer'],
         paragraphs=[
             [('디아블로 투 원작에서는 장비를 바꾸면,','In the original Diablo II, changing equipment'),('캐릭터의 겉모습도 달라집니다.','also changes your character’s appearance.'),('이 많은 조합을 전부 따로 그렸을까요?','Did they draw every complete combination separately?')],
             [('개발진은 머리와 몸통, 다리와 양팔,','The team rendered the head, torso, legs and arms,'),('무기와 방패를 따로 렌더링했습니다.','as well as the weapon and shield, separately.'),('입체 모델을 부위별 그림으로 만든 거예요.','They turned the 3D model into component images.')],
             [('우리 캐릭터도 같은 방식으로 나눠 볼게요.','Let’s separate our character the same way.'),('다른 부위는 유지하고 갑옷 그림만 바꾸면,','Keep the other parts and replace the armor image.'),('새 장비를 입은 모습이 됩니다.','Now the character wears different equipment.')],
             [('움직일 때는 같은 자세에 해당하는 부품들을,','During movement, use the components for the same pose'),('같은 순서와 위치에 맞춰 겹쳐 그립니다.','and layer them at the matching positions.'),('그래야 팔과 무기가 따로 놀지 않겠죠.','That keeps the arm and weapon moving together.')],
             [('이런 부품 조합형 스프라이트는,','With component-based sprites,'),('부위마다 준비한 그림을 다시 조합해서,','the images prepared for individual parts can be recombined'),('여러 장비의 모습을 만들 수 있습니다.','to produce multiple equipment appearances.')],
             [('겉으로는 한 캐릭터지만,','It looks like one character,'),('속에서는 여러 그림이 같은 동작으로 맞물리고 있었던 겁니다.','but several images are coordinated in the same movement.')],
         ],
         requiredFootage='FHD recording of original Diablo II or verified legacy view. Must show equipment silhouette or actual equipment change, not a modern D2R model as sprite proof.',
         limits=['Do not imply every inventory item has a unique visible sprite.','Own medieval character is code-authored educational artwork; not a ripped Diablo asset.','Sync/order explanation is a general compositing prerequisite, not a claim of recovered exact D2 runtime data.']),
]

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists(): raise FileExistsError(path)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    for row in DATA:
        p=ROOT/'projects'/row['slug']; lines=[' '.join(x[0] for x in para) for para in row['paragraphs']]
        en=[' '.join(x[1] for x in para) for para in row['paragraphs']]
        clauses=[dict(id=f'p{i+1}-{j+1}',lineIndex=i,spoken=ko,ko=ko,en=eng) for i,para in enumerate(row['paragraphs']) for j,(ko,eng) in enumerate(para)]
        save(p/'project.json',dict(slug=row['slug'],title=row['title'],format=dict(type='youtube-shorts',width=1080,height=1920,fps=60),status='preproduction-footage-pending',currentRevision=REVISION,authorization=dict(userEvidence='10개 제작해줘~',scope='Explicit finite ten-Short batch through local final review only',fullProductionAuthorized=True,humanFinalReviewRequired=True,youtubeAuthorized=False,driveAuthorized=False),paths=dict(script=f'projects/{row["slug"]}/script/narration.spoken.ko.json',checkpoint=f'projects/{row["slug"]}/production/checkpoint.json',productionPlan=f'projects/{row["slug"]}/planning/production-plan.json'),publishReady=False))
        save(p/'script/narration.spoken.ko.json',dict(slug=row['slug'],revision=REVISION,scenes=[dict(id='main',lines=lines)]))
        save(p/'script/clauses.json',dict(clauses=clauses,pronunciationAliases={}))
        for lang,paras in [('ko',lines),('en',en)]:
            target=p/f'script/narration.{lang}.txt';target.write_text('\n\n'.join(paras)+'\n',encoding='utf8')
        save(p/'production/section-plan.json',[dict(id=s,paragraph=i,firstCue=f'p{i+1}-1',purpose=s,kind='game' if s=='game' else 'illustration') for i,s in enumerate(row['stages'])])
        sections=[];cursor=0
        for i,s in enumerate(row['stages']):
            length=max(5,round(len(lines[i])/11+1,2));end=round((cursor+length)*60)/60
            sections.append(dict(id=s,paragraph=i,kind='game' if s=='game' else 'illustration',start=cursor,end=end,startFrame=round(cursor*60),endFrame=round(end*60),hold=0))
            cursor=end
        save(p/'production/visual-timing.json',dict(revision=REVISION,status='provisional-not-audio-aligned',durationSeconds=cursor,frames=round(cursor*60),sections=sections,reactions=[dict(start=sections[2]['start'],end=sections[2]['start']+1.8,kind='realize'),dict(start=sections[-1]['start'],end=sections[-1]['start']+2,kind='relief')]))
        save(p/'production/scene-config.json',dict(topic=row['topic'],head=row['head'],term=row['term'],gameName='디아블로 II · 원작' if row['topic']=='sprites' else '디아블로 II: 레저렉션',footageReady=False,footageFrameDirectory='production/local/game-frames/game'))
        save(p/'sources/selected-footage.json',dict(status='pending-acquisition-and-inspection',requirement=row['requiredFootage'],sources=[],independentFootageViewed=False,rightsVerified=False,fhdVerified=False))
        save(p/'planning/production-plan.json',dict(revision=REVISION,scope='One of the explicitly requested ten Shorts',primarySource=dict(url=row['source'],readScope=row['evidence'],applicability=row['sourceScope'],kind='research-reference-only'),centralQuestion=row['title'],preservedClaims=row['sourceScope'],scriptFinalized=False,independentFootageViewed=False,scriptStatus='complete-provisional-narration-awaiting-actual-game-source-check',renderer=dict(name='Motion Canvas',reason='Editable two-dimensional mechanism diagram: preserve state while revealing view limits, vegetation clearance, or component composition. No simulated commercial-game measurements.',sourcePath=f'motion-canvas/src/projects/diablo-tricks-shorts-20261025/{row["topic"]}/scene.tsx',kind='illustration'),terminology=dict(english=row['term'][0],korean=row['term'][1],firstAppearance='Mechanism shown before naming'),scenePlan=[dict(paragraph=i+1,id=s,speech=lines[i],visualRole='actual-game-context-pending' if s=='game' else 'own-illustration',boundaryLink='Same objects continue from the prior state; no chapter reset',hold=0) for i,s in enumerate(row['stages'])],requiredFootage=row['requiredFootage'],essentialConditions=row['limits'],assets=[dict(path='shared/assets/branding/cat-reactions-v1/provenance.json',purpose='Yamyam cat reveal/conclusion reactions',reuse=True),dict(kind='code-authored-vector-diagrams',path=f'motion-canvas/src/projects/diablo-tricks-shorts-20261025/{row["topic"]}/scene.tsx',purpose='Own abstract mechanism, no reference-creator art')],visualReview=dict(native1080=False,mobile375=False,movingPlayback=False),audio=dict(status='not-generated',voice='approved-Qwen-reference-to-be-bound-by-parent',bgmRequired=True),finalHumanReview='pending'))
        save(p/'production/checkpoint.json',dict(revision=REVISION,state='provisional-script-and-scene-implementation',nextAction='Acquire and directly inspect source gameplay, confirm scene correspondence, then lock narration before TTS',blockers=['Independent gameplay and source-specific rights/FHD inspection pending','GPU occupied; no TTS or GPU render launched'],prohibitedInThisTask=['YouTube','Google Drive','automatic future batches'],actualCompleted=['Primary-source paragraphs read','KO/EN narration and clause records authored','Editable scene design authored'],mediaProduced=False))
        save(p/'production/review-ledger.json',dict(revision=REVISION,checks=[dict(name='primary-source-fact-check',status='pass-for-draft',evidence=row['evidence'],url=row['source']),dict(name='footage-rights-fhd-direct-view',status='pending'),dict(name='narration-audio-and-mobile',status='pending')],humanFinalReview='pending'))
        save(p/'publishing/metadata-draft.json',dict(titleKo=row['title'],titleEn=row['titleEn'],descriptionKo=lines[-1]+'\n\n#디아블로2 #게임개발 #게임그래픽\n\n자료\n'+row['source'],descriptionEn=en[-1]+'\n\n#Diablo2 #GameDevelopment\n\nSources\n'+row['source'],status='draft-footage-and-music-credits-pending'))
        (p/'planning/outline.md').write_text('# '+row['title']+'\n\n제작 중 · 실제 게임 소스 검수 전 대본 초안\n\n'+'\n\n'.join(f'{i+1}. {s}\n\n{lines[i]}' for i,s in enumerate(row['stages']))+'\n',encoding='utf8')
    print(json.dumps(dict(created=[x['slug'] for x in DATA],ttsStarted=False),ensure_ascii=False))

if __name__=='__main__':main()
