const fs=require('node:fs'),path=require('node:path');
const project=path.resolve(__dirname,'..');
const script=JSON.parse(fs.readFileSync(path.join(project,'script/narration.ko.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(project,'project.json'),'utf8'));
const cue=['물리적인 화면과 게임 카메라 구분','같은 세로 FOV에서 16:9와 21:9 비교','같은 위치에서 수평 FOV 60°/100° 비교','표적 크기와 게임 목적','운전석·무기·UI의 가림과 판단 공간','비율·FOV·화면 점유율 구분과 최종 체크리스트'];
const text=`# ${script.title}\n\n대본 ${script.version} · 상태: ${manifest.approvals.script} · 본편 실측 ${manifest.video.durationSeconds}초\n\n게임 디자인 설명이 목적이며 게임명은 사례다. 아래 내레이션은 원문 번역이 아닌 자체 구성이다.\n게임 전체화면 약 68% / 2.5D 설명 약 32%로 편집한다.\n\n`+script.scenes.map((s,i)=>`## ${s.id}. ${s.title}\n\n화면: ${cue[i]}. 실제 예시 페어는 planning/footage-plan.md 참조.\n\n${s.lines.join('\n\n')}\n`).join('\n')+'\n## 제작 메모\n\n발음용 비율과 필드 오브 뷰/에프오브이는 표시 자막에서 16:9·21:9·Field of View/FOV로 쓴다.\n기존 균형형 1.7B 전체 장면 연속 발화.\nDiscovery 선택 승인. 예시에서도 한국어 내레이션을 계속하고, 원음은 정규화/덕킹 뒤 0.5배로 낮춘다.\n원본 회원 이미지가 없으면 이름만 있는 구형 엔딩을 재사용하지 않는다.\n';
fs.writeFileSync(path.join(project,'script/review.ko.md'),text);
console.log(JSON.stringify({scenes:script.scenes.length,lines:script.scenes.reduce((n,s)=>n+s.lines.length,0),characters:script.scenes.flatMap(s=>s.lines).join('').length,scriptApproval:manifest.approvals.script}));
