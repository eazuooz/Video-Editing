"""Current measured chapters and the two explicitly accepted source links."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
Q=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
approval=read(Q/'besiege-description-exception-approval.json')
assert approval['sourceConditionExceptionAuthorized'] and not approval['externalUploadHold']
intro={
 'foundations':{
 'ko':'회전을 저장할 네 숫자는 왜 필요할까요? 허수의 뜻과 평면 회전부터 출발해 반각, 정규화와 역원으로 이어갑니다. 라이더스 리퍼블릭의 스키 자세, 트레일메이커스의 비행기 기울기, 스페이스 엔지니어스의 부품 배치 방향, 비시지의 선택 부품 회전을 비교합니다. 같은 원리를 다른 물체에 적용하면서 위치와 자세, 한 방향과 전체 자세, 회전을 되돌리는 일과 이동 경로를 되감는 일을 구분합니다. 기존 설명과 계산을 보존한 두 편 중 첫 편입니다. 게임 위의 선은 화면 관찰을 돕는 표시이며, 수치 예제는 우리가 정의한 모형의 계산입니다.',
 'en':'Why do we need four numbers to store a rotation? We begin with imaginary numbers and planar rotation, then connect half angles, normalization and inverses. We compare skier orientation in Riders Republic, aircraft banking in Trailmakers, part-placement directions in Space Engineers, and rotation of selected parts in Besiege. Applying the same principle to different objects, we distinguish position from orientation, one direction from a complete orientation, and undoing a rotation from rewinding a traveled path. This first of two lectures preserves the existing explanations and calculations. Gameplay lines describe visible screen relationships; numerical examples use our explicitly defined models.'},
 'calculations':{
 'ko':'네 숫자로 회전을 기록했다면 두 회전을 어떤 순서로 합쳐야 할까요? 라이더스 리퍼블릭의 몸체, 트레일메이커스의 비행기, 스페이스 엔지니어스의 부품 미리 보기, 비시지의 대포 방향을 연결해 합성·목표 자세·벡터 회전을 비교합니다. 고정된 축의 순서를 바꾸고, 현재 자세에서 목표까지 필요한 회전 차이를 구한 뒤, 같은 벡터를 돌려 방향과 길이를 확인합니다. 부품 하나의 방향과 전체 기체의 자세는 서로 다른 대상입니다. 게임 화면의 선은 엔진 내부의 실측값이 아니며, 계산은 정한 좌표·곱셈 약속의 설명용 모형입니다. 기존 내용과 계산을 보존한 쿼터니언 두 번째 강의입니다.',
 'en':'Once a rotation is stored in four numbers, in what order should two rotations be composed? We connect the body in Riders Republic, an aircraft in Trailmakers, a part preview in Space Engineers, and barrel directions in Besiege to compare composition, target orientation and vector rotation. We reverse the order of rotations about fixed axes, calculate the change from a current to a target orientation, and rotate the same vector to check direction and length. A single part and an entire aircraft are different targets. Screen annotations do not measure engine internals; calculations use an illustrative model with stated coordinate and multiplication conventions. This second quaternion lecture preserves the existing material and calculations.'}}
extra={'foundations':{'QF10':['비행기: 이동과 기울기를 따로 읽기','Aircraft: separate travel from banking'],'QF30':['선택한 부품에 같은 회전 적용하기','Apply one rotation to selected parts'],'QF20':['부품 방향과 전체 자세 구분하기','A part direction versus a complete orientation']},'calculations':{'QC10':['비행기로 연결하는 회전 순서 비교','Compare rotation order using an aircraft'],'QC20':['현재 부품 방향과 목표 방향 관찰하기','Observe current and target part directions'],'QC21':['30도에서 90도까지 필요한 회전 차이','A worked change from 30 to 90 degrees'],'QC30':['벡터 계산을 물체 방향으로 읽기','Read a calculated vector on its object']}}
def stamp(seconds):
    value=int(seconds+1e-7);return f'{value//60:02d}:{value%60:02d}'
for episode in ['foundations','calculations']:
    slug=f'game-math-quaternion-{episode}-v3'; P=ROOT/'projects'/slug; old=ROOT/f'projects/game-math-quaternion-{episode}-v2'
    timeline=read(P/'production/timeline.json'); baseline=read(old/'production/timeline.json')
    current={s['id']:s for s in timeline['scenes']}
    records={}
    for li,lang in enumerate(['ko','en']):
        text=(old/f'publishing/upload-description.{lang}.txt').read_text(encoding='utf8')
        footer_at=text.index('🎮'); footer=text[footer_at:]
        chapter_label='챕터' if lang=='ko' else 'Chapters'
        chapter_at=text.index(chapter_label)
        resources=text[text.index('📚'):chapter_at].rstrip()
        chapters=[]
        for match in re.finditer(r'^(\d+):(\d+) (.+)$',text[chapter_at:footer_at],re.M):
            seconds=int(match[1])*60+int(match[2]); label=match[3]
            if seconds==0: at=0
            elif seconds >= baseline['seconds']-11:
                at=timeline['seconds']-10
            else:
                # Existing chapter time can be rounded a fraction below its boundary.
                boundary=min(baseline['scenes'],key=lambda s:abs(s['start']-seconds))
                if abs(boundary['start']-seconds)<1.1:at=current[boundary['id']]['start']
                else:
                    scene=next(s for s in baseline['scenes'] if s['start']<=seconds<s['start']+s['seconds'])
                    at=current[scene['id']]['start']+(seconds-scene['start'])
            chapters.append((at,label))
        for ident,labels in extra[episode].items():chapters.append((current[ident]['start'],labels[li]))
        chapters.sort()
        assert len({stamp(t) for t,_ in chapters})==len(chapters)
        chapters_text='\n'.join(stamp(t)+' '+label for t,label in chapters)
        source_label='비시지 제작사 필수 링크' if lang=='ko' else 'Required Besiege developer links'
        result=intro[episode][lang]+'\n\n'+resources+'\n\n'+chapter_label+'\n'+chapters_text+'\n\n'+source_label+'\n'+'\n'.join(approval['requiredDescriptionLinks'])+'\n\n'+footer.rstrip()+'\n'
        assert len(result)<5000
        assert all(result.count(link)==1 for link in approval['requiredDescriptionLinks'])
        path=P/f'publishing/upload-description.{lang}.txt';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(result,encoding='utf8')
        records[lang]=dict(path=str(path.relative_to(ROOT)).replace('\\','/'),sha256=sha(path),characters=len(result),chapters=[dict(start=t,display=stamp(t),title=label) for t,label in chapters],channelFooterPreserved=result.endswith(footer.rstrip()+'\n'))
    comment=old/'publishing/pinned-comment.ko.txt'
    if comment.exists():(P/'publishing/pinned-comment.ko.txt').write_bytes(comment.read_bytes())
    thumbnail=old/'publishing/thumbnail-v2.png';assert thumbnail.exists()
    m=read(P/'project.json');m['publishing'].update(descriptionsPrepared=True,descriptionPreparation=records,thumbnailPath=str(thumbnail.relative_to(ROOT)).replace('\\','/'),thumbnailSha256=sha(thumbnail),thumbnailMethod='Reuse the directly inspected approved illustrated quaternion thumbnail',descriptionBesiegeLinksPlatformVerified=False)
    (P/'project.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (P/'publishing/prepared-metadata.json').write_text(json.dumps(dict(slug=slug,titles=m['titles'],descriptions=records,requiredBesiegeLinks=approval['requiredDescriptionLinks'],privateUploadRequiredFirst=True,thumbnailPath=m['publishing']['thumbnailPath'],thumbnailSha256=sha(thumbnail),actualVideoId=None,fullPublishingSettingsComplete=False,comments='Prepared only; posting/pinning pending until comments are available'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(slug,'prepared bilingual descriptions with current chapters and two mandatory links; platform verification pending')
