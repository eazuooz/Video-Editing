"""Keep reproducible requests, boards and the independent article consistent."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;P=H.parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
j=read(P/'planning/reproduction-recipes.json');j['recipes']=[r for r in j['recipes'] if r['id'] not in ('sofa-image','table-image')]
insert=next(i for i,r in enumerate(j['recipes']) if r['id']=='tripo')
j['recipes'][insert:insert]=[
 {'id':'sofa-image','tool':'이미지 생성 → Tripo','input':'따뜻한 목재와 라탄/코드 짜임 디자인 참고','request':'밝은 꿀빛 목재 프레임과 크림색 촘촘한 라탄/코드 짜임의 2인 소파를 단독으로 만들어줘. 폭 1.85m, 등받이 높이 약 0.92m, 깊이 0.76m를 기준으로 해. 완만히 기댄 등받이, 가는 팔걸이와 분리된 네 다리가 모두 보이는 3/4 정면 시점으로 해줘. 로고·사람·꽃·식기·방·테이블은 빼고 투명 배경과 균일한 조명을 사용해줘. 이 이미지를 Tripo H3.1 입력으로 사용하고 Triangle 목표 20K로 정리한 뒤 FBX와 현재 4K 텍스처를 내보내줘.','output':'라탄 소파 입력 PNG와 실제 게임용 Tripo 모델','check':'등·좌판 짜임, 분리된 다리, 최종 22,066 triangles와 4K Base Color/Normal 확인'},
 {'id':'table-image','tool':'이미지 생성 → Tripo','input':'소파와 같은 목재/짜임 팔레트','request':'소파와 같은 밝은 목재의 낮은 타원형 커피 테이블 하나를 만들어줘. 폭 1.25m, 깊이 0.68m, 상판 높이 0.44m를 엔진 배치 기준으로 해. 둥근 목재 상판과 모서리, 경사진 네 다리, 크림색 짜임의 아래 선반을 표현해줘. 상판은 발을 올릴 수 있게 비워 두고 소품·식기·꽃·사람·소파·글자는 넣지 마. 투명 배경의 단독 이미지를 Tripo H3.1 입력으로 사용해. Triangle 목표 10K로 정리하고 FBX와 현재 4K 텍스처를 내려받아줘.','output':'비어 있는 우드·라탄 테이블 모델','check':'실제 9,375 triangles, 평평한 상판, 네 다리, 소파와의 색/치수 일치'}]
for r in j['recipes']:
 if r['id']=='layout':r.update(input='Tripo 소파/테이블 FBX와 캐릭터',request='고정된 대각선 직교 카메라와 미터 단위를 사용해줘. Tripo 소파를 폭 1.85m·높이 0.92m·깊이 0.76m, 테이블을 폭 1.25m·높이 0.44m·깊이 0.68m에 맞춰 중앙 카펫에 배치해줘. 소파 등받이에 기대고 앞 테이블에 발을 올려 책 읽게 해줘. 테이블을 관통하지 않도록 옆 통로로 접근하고 기존 착석/기립 클립을 이어줘. 아이맥 책상·양옆 책장·벽난로·창가 레코드·고양이는 보존해줘.')
 if r['id']=='book-contact':r['request']=r['request'].replace('소파 좌판·등 쿠션·발받침','소파 좌판·기댄 등받이·낮은 테이블').replace('자리 잡은 뒤 책을 펼쳐줘.','자리 잡은 뒤 책을 펼쳐줘. 원래 기대는 다리 동작은 유지하고 발목 IK 목표를 상판 높이에 맞춰 발이 떠 있거나 관통하지 않게 해줘.')
 if r['id']=='cat':r['request']=r['request'].replace('작은 호흡을 더해줘.','원래 메시의 몸통과 꼬리 영역을 따로 나눠 작은 수면 동작을 더해줘. 얼굴과 앞발은 고정하고 몸통은 약 4.8초 주기로 몇 mm 오르내리게, 꼬리 끝은 약 7.5초 주기로 조금씩 움직여줘. 꼬리가 턱과 얼굴을 통과하지 않게 바깥쪽으로 움직이고 UV와 털 무늬를 보존해줘.');r['check']+='; 얼굴 고정과 몸통/꼬리 변형을 여러 시각에서 실제 재생 확인'
save(P/'planning/reproduction-recipes.json',j)
f=H/'build-request-reference.py';s=f.read_text('utf-8').replace('17','19').replace('누워 읽기와 책 접촉','소파 독서와 테이블·책 접촉')
ids=['room-image','hero-image','headphone-image','tripo','unity-scope','layout','materials','actions','book-contact','hair','plants-window','rain','fire','cat','radio','notes-timer','web-build']
s=s.replace('cards=[]',"labels=dict(zip("+repr(ids)+",labels));labels.update({'sofa-image':'목재·라탄 소파 입력','table-image':'낮은 우드 테이블 입력'})\ncards=[]")
s=s.replace("for i,(r,label) in enumerate(zip(j['recipes'],labels),1):","for i,r in enumerate(j['recipes'],1):\n    label=labels[r['id']]")
f.write_text(s,'utf-8')
f=H/'verify-film.py';f.write_text(f.read_text('utf-8').replace('요청문 17개','요청문 19개'),'utf-8')
f=H/'compose-howto-article.py';s=f.read_text('utf-8').replace("request('unity-scope')+request('layout')","request('unity-scope')+request('sofa-image')+request('table-image')+request('layout')").replace("==17","==19").replace('17 requests','19 requests')
marker="assert set(re.findall"
update="""out=re.sub(r'독서 자리는 기존 라이브러리의 RG Poly.*?조합합니다\\.', '독서용 소파와 테이블은 각각의 단독 입력 이미지를 만들어 Tripo H3.1로 생성했습니다. 밝은 목재 프레임과 크림색 라탄/코드 짜임을 맞추고, 소파는 Triangle 목표 20K에서 실제 22,066삼각형, 테이블은 목표 10K에서 9,375삼각형으로 정리했습니다. 두 가구의 생성·정리는 각각 90크레딧, 합계 180크레딧이며 캐릭터·헤드폰 175와 고양이 90은 별도입니다. 기존 붉은 가죽 소파는 이전 검수본에 남기고 현재 장면은 새 가구를 사용합니다.', out, flags=re.S)
out=out.replace('발받침을 배치합니다.','낮은 우드 테이블을 배치합니다.').replace('발받침을 통과하지 않도록','테이블을 통과하지 않도록').replace('골반·쿠션·발바닥을 같은 가구 좌표에서 확인한 후','골반·등받이·테이블 상판·발바닥을 같은 가구 좌표에서 확인한 후')
out=out.replace('현재 고양이 재질에는 Base Color와 Normal을 연결하고 금속성을 0, Smoothness를 0.08로 두었습니다.', '현재 고양이 재질에는 Base Color와 Normal을 연결하고 금속성을 0, Smoothness를 0.08로 두었습니다.')
out=out.replace('작은 수면 호흡은 바닥 접촉을 유지한 미세한 스케일 변화입니다. 별도의 고양이 리깅이나 걷기 모션을 생성한 것은 아닙니다.', '수면 동작은 원래 메시의 몸통과 꼬리에 다른 가중치를 둔 국소 변형입니다. 몸통은 약 4.8초 주기로 최대 약 5mm, 꼬리는 약 7.5초 주기로 작은 움직임을 더합니다. 얼굴과 앞발은 안정적으로 남기고 꼬리 끝은 턱 바깥으로 움직입니다. 실제 표본에서 얼굴의 변위는 부동소수점 오차 범위였고, 몸통·꼬리의 최대 변위는 약 1.4cm였습니다. UV와 텍스처를 유지한 모델별 영역 마스크이며 일반적인 고양이 리깅이나 걷기 모션을 생성한 것은 아닙니다.')
out=re.sub(r'\\n- 소파: \\[Vintage Retro Stylized Pack.*?가져왔습니다\\.\\n', '\\n- 현재 소파·테이블: 자체 이미지 입력과 Tripo H3.1 생성·정리 결과. 원본 FBX와 출력별 재질을 함께 보관하며, 과거 라이브러리 가죽 소파와 구분합니다.\\n', out)
"""
s=s.replace(marker,update+'\n'+marker);f.write_text(s,'utf-8')
f=H/'render-howto-storyboards.cjs';s=f.read_text('utf-8').replace("11:['미터 단위 · 고정 카메라','책상 · 의자 · 독서 소파','캐릭터 키 · 좌판 · 무릎 공간']","11:['소파·테이블 입력을 분리','Tripo 생성 → 게임용 메시','미터 단위 · 몸과 가구 접촉']").replace("18:['휴식 몸 + 독서 팔 Avatar Mask','책은 얼굴 방향 · 양손은 바깥','손목 방향 · 팔꿈치 · 간격 확인']","18:['휴식 몸 + 독서 팔 Avatar Mask','등은 소파 · 발은 테이블','책·손목·팔꿈치 간격 확인']").replace("'4K 텍스처 · 실제 모델 · 작은 호흡'","'4K 텍스처 · 몸통 호흡 · 작은 꼬리'")
s=s.replace(" if(id===4)"," if(id===11){pic('sofa-input',76,240,1120,335);pic('table-input',76,585,1120,245);steps(id);return;}\n if(id===4)")
f.write_text(s,'utf-8')
f=H/'render-film.py';s=f.read_text('utf-8').replace('n in (2,6,13,30)','n in (2,6,11,13,30)');f.write_text(s,'utf-8')
f=H/'prepare-film-assets.py';s=f.read_text('utf-8').replace('living-room-v11/tripo-cat-ready.jpg','living-room-v10/tripo-cat-ready.jpg');s+='\nfor key,name in [("sofa-input","rattan-sofa-v11-input.png"),("table-input","rattan-table-v11-input.png")]:shutil.copy2(P/"assets/references"/name,A/(key+".png"))\n';f.write_text(s,'utf-8')
f=H/'prepare-wiki-frames.py';s=f.read_text('utf-8').replace('작은 호흡으로 바닥 접촉을 유지한다.','원본 메시의 몸통 호흡과 작은 꼬리 움직임을 더하고 얼굴은 고정한다.');f.write_text(s,'utf-8')
print('Prepared 19 requests and wood/rattan + cat-motion tutorial material')
