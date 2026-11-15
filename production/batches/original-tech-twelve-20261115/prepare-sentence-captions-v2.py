"""Meaning-matched clauses for the separate sentence narration, without timing."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
PAIRS={
 'shorts-oot-ninja-show-z-targeting':{
  'p001':[
   ['젤다에서 적을 주목해 보세요.','Try locking onto an enemy in Zelda.'],
   ['옆으로 움직여도 상대를 바라봅니다.','Link keeps facing it while moving sideways.'],
   ['특정 상대를 계속 겨누는 조작, 락온입니다.','Lock-on keeps a chosen opponent in focus.'],
   ['교토의 닌자 공연이 여기에 어떤 힌트를 줬을까요?','What did a Kyoto ninja show contribute?'],
   ['화면의 문제부터 살펴보겠습니다.','We will start with the camera problem.'],
   ['그다음은 공격 차례와 상대 중심 이동입니다.','Then: attack turns and target-relative movement.']],
  'p003':[
   ['한 개발자는 검술 액션의 힌트를 찾으러','A developer looking for swordplay ideas'],
   ['공연에 갔습니다.','went to a show.'],
   ['닌자는 팽팽한 사슬을 사이에 두고','A ninja kept a taut chain between opponents'],
   ['상대 주위를 돌았습니다.','while circling the other fighter.'],
   ['개발자는 이 움직임을 눈여겨봤습니다.','The developer took note of that movement.']],
  'p004':[
   ['상대를 겨누기 쉽게 하자는 고민은','Making opponents easier to target'],
   ['마리오 육십사 때부터 있었습니다.','had been discussed since Super Mario 64.'],
   ['다른 개발자가 공연에서 찾은 해법은','Another developer found a solution at the show:'],
   ['공격 차례였습니다.','taking turns to attack.'],
   ['한 명이 싸우는 동안 나머지는 기다렸습니다.','While one fought, the others waited.']],
  'p006':[
   ['사슬에서 얻은 힌트를','Think of the idea from the chain'],
   ['보이지 않는 연결로 생각해 보세요.','as an invisible connection.'],
   ['상대를 향한 방향이 기준입니다.','The direction toward the opponent is the reference.'],
   ['앞으로 움직이면 다가갑니다.','Moving forward brings you closer.'],
   ['옆으로 움직이면 상대 주위를 돕니다.','Moving sideways circles the opponent.'],
   ['빈틈을 찾으면 뛰어들어 공격합니다.','Find an opening, then jump in and attack.']]
 },
 'shorts-mario64-lakitu-camera':{
  'p001':[
   ['마리오 육십사에는','In Super Mario 64,'],
   ['카메라를 든 캐릭터가 나옵니다.','a character appears carrying a camera.'],
   ['이름은 쥬게무입니다.','His name is Lakitu.'],
   ['마리오 조작과 카메라 조작은 서로 다릅니다.','Mario and the camera have separate controls.'],
   ['가까이 살펴보고, 주위를 돌고,','We will look closely, circle around,'],
   ['멀리서 보는 순서로 살펴보겠습니다.','and pull back, in that order.']],
  'p002':[
   ['카메라는 마리오를 따라가며 촬영합니다.','The camera follows and films Mario.'],
   ['플레이어는 씨 버튼으로','The player uses the C buttons'],
   ['촬영 위치와 방향을 조절합니다.','to adjust its position and direction.'],
   ['화면을 보는 자리가 바로 시점입니다.','The viewpoint is where we see the scene from.'],
   ['이 시점도 직접 바꿀 수 있습니다.','That viewpoint is also under player control.']],
  'p003':[
   ['주변이나 위쪽을 둘러보세요.','Look around or upward.'],
   ['길과 파워스타를 찾는 데 도움이 됩니다.','It can help you find routes and Power Stars.'],
   ['마리오가 서 있는 자리와','Think about where Mario stands'],
   ['카메라가 향하는 방향을 나눠 생각하면 쉽습니다.','separately from what the camera points toward.']],
  'p005':[
   ['씨 버튼의 왼쪽과 오른쪽을 눌러 보세요.','Press C-left or C-right.'],
   ['카메라가 마리오 주위를 돕니다.','The camera circles Mario.'],
   ['같은 마리오를 다른 쪽에서 볼 수 있죠.','See the same Mario from another side.'],
   ['더 돌릴 수 없는 곳에서는','When the camera cannot go farther,'],
   ['경고음이 한계를 알려 줍니다.','a buzz signals its limit.']],
  'p006':[
   ['씨 버튼의 아래쪽을 누르면','Press C-down'],
   ['카메라가 뒤로 빠집니다.','to pull the camera back.'],
   ['마리오는 작게 보입니다.','Mario looks smaller.'],
   ['주변 공간은 더 넓게 들어옵니다.','More surroundings fit in view.'],
   ['가까이 보기, 주위를 돌기, 멀리 보기.','Look closely, circle around, and pull back.'],
   ['마리오 육십사에서는','In Super Mario 64,'],
   ['플레이어가 촬영자이기도 한 겁니다.','the player is also the cinematographer.']]
 }
}
def main():
    spec=importlib.util.spec_from_file_location('ot12_sentence_caption_layout',HERE/'lockon-layout-v1.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout);f=layout.font(48);results=[]
    for row in read(HERE/'batch.json')['projects']:
        p=ROOT/'projects'/row['slug'];source=p/'planning/narration-sentence-v2.json';d=read(source);old=read(p/'planning/caption-clauses-v1.json');old_by_id={x['id']:x['clauses']for x in old['paragraphs']};paragraphs=[]
        for paragraph in d['paragraphs']:
            pairs=PAIRS.get(p.name,{}).get(paragraph['id'],old_by_id[paragraph['id']])
            assert ''.join(' '.join(a for a,b in pairs).split())==''.join(paragraph['ko'].split()),(p.name,paragraph['id'])
            for ko,en in pairs:layout.wrap(ko,f);layout.wrap(en,f)
            paragraphs.append(dict(id=paragraph['id'],clauses=pairs))
        out=p/'planning/caption-clauses-sentence-v2.json';assert not out.exists();out.write_text(json.dumps(dict(schemaVersion=1,source=pin(source),previousUntimedClauses=pin(p/'planning/caption-clauses-v1.json'),paragraphs=paragraphs,englishRole='Original meaning-matched translation; align complete clauses to reviewed actual whole-word edges.',captionFontPixels=48,maximumLines=2,maximumWidth=800,timestampsAssigned=False,actualAsrWordAnchorsRequired=True,finalSubtitlesAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8');results.append(pin(out))
    print(json.dumps(dict(projects=len(results),clausesValidated=True,timestampsAssigned=False)))
if __name__=='__main__':main()
