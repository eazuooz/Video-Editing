"""Record the selected M14 delta and the user's actual-game abstract rule."""
from pathlib import Path
import json, datetime
R=Path('D:/Github/VideoEditing')
B=R/'production/batches/private-math-gameplay-20261024/m14-gameplay-abstract-v5'
def read(p): return json.loads(p.read_text('utf-8-sig'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rule='''### 실제 게임으로 여는 Abstract

2026-10-25 사용자 지시 `actual-game-thesis-abstract-v1`: 영상 맨 앞의 기존 2초 브랜딩 직후, **전체 주제를 관통하는 핵심 질문·현상·결론의 방향을 실제 게임 예시와 설명으로 먼저 보여 준다.** 추상적인 목차 낭독이나 무관한 게임 몽타주로 대신하지 않는다. 시청자가 실제 대상의 전 상태→조작→결과를 알아볼 수 있는 독립 게임 녹화를 고르고, 그 결과가 본문의 어떤 질문과 원리로 이어지는지 짧고 자연스럽게 설명한다. 주제와 직접 연결되는 선·윤곽·기즈모를 발화에 맞춰 붙이고, 게임에서 보이지 않는 내부 계산은 관찰 사실과 구별한다. 길이는 이해에 필요한 동작과 자연스러운 발화에 맞추며 정지·반복·감속으로 채우지 않는다. 기존 2–4문장 개요와 역할을 통합해 같은 내용을 연속해서 두 번 소개하지 않는다. 초반의 구체적인 대상·문제를 첫 설명으로 이어 주고 마지막 결론에서도 같은 질문에 답한다.

기존 장면 계획에 핵심 주제, 독립 원본 URL/인아웃·권리·FHD 증거, 관찰한 동작, 대사 큐, 본문 연결을 기록하고 최종 출력에서 함께 확인한다. 현재 선택된 다각형 ② 수정과 앞으로 명시 선택하는 제작에 적용한다. 이번 편의 본문 설명·음성·학습 순서는 보존하며 추가 도입 음성만 생성한다. 이 규칙만으로 미선택 완성본을 재렌더하거나 업로드하지 않는다.

'''
p=R/'docs/VIDEO_WORKFLOW.md';s=p.read_text('utf-8-sig')
if '### 실제 게임으로 여는 Abstract' not in s:
    s=s.replace('## 3. 제작 전에 해결할 품질 기준', '## 3. 제작 전에 해결할 품질 기준\n\n'+rule,1);p.write_text(s,encoding='utf8')
p=R/'AGENTS.md';s=p.read_text('utf-8-sig')
agent='User-directed 2026-10-25 `actual-game-thesis-abstract-v1`: after branding, open with an actual independent gameplay example and a short narrated abstract that carries the whole video thesis (observable before/action/result → central question → first explanation). Integrate the overview, preserve native motion and source/rights/FHD evidence, and never use unrelated montage, static padding or a self-authored demo as actual gameplay. Apply to selected M14 and future explicitly selected work; preserve existing M14 body narration/explanations/order, generating only added opening speech. No automatic remake of other completed videos. See docs/VIDEO_WORKFLOW.md. '
if 'actual-game-thesis-abstract-v1' not in s:
    s=s.replace('- After the original 2-second branding,', '- '+agent+'After the original 2-second branding,',1);p.write_text(s,encoding='utf8')
p=R/'shared/publishing/video-production-control.json';d=read(p)
d['actualGameAbstractPolicy']={'id':'actual-game-thesis-abstract-v1','requestedOn':'2026-10-25','guide':'docs/VIDEO_WORKFLOW.md','scope':'Selected M14 delta and future explicitly selected videos','actualIndependentGameplayRequired':True,'automaticOtherRemake':False,'addsApprovalGate':False}
d.setdefault('scopedBatchAuthorizations',{})['m14-gameplay-abstract-v5']={'status':'active','selectedVideo':'game-math-polygon-partition-v2','episode':'M14','userEvidence':'남은 다각형 ②도 사각형 자르고 회전시키는 실제 게임영상 찾아서 마저 완성해줘. 설명은 그대로 유지하고. 영상 제일 처음에 전체 주제를 관철하는 Abstract 영상하고 설명을 실제 게임예시로 넣어줘. 규칙추가.','renderAuthorized':True,'newTtsAuthorized':'opening abstract only; preserve body PCM','bodyPreserved':True,'uploadAuthorized':False,'otherVideoAuthorized':False,'automationAuthorized':False,'boundary':'four local outputs, internal QA, review links, selective Git'}
save(p,d)
save(B/'checkpoint.json',{'episode':'M14','revision':'gameplay-abstract-v5','status':'finding-square-cut-rotation-native-source','base':'production/batches/private-math-gameplay-20261024/motion-v4/m14-plan.json','bodyPreservation':'existing explanation sources, PCM, order and body duration','intro':'new actual-game abstract after original 2s branding','recommendedChoice':'Finish selected M14 only; generalize abstract as future production rule without automatically remaking other 17 outputs.','humanReview':'pending','uploadAuthorized':False})
print('M14 scope and actual-game abstract rule recorded.')
