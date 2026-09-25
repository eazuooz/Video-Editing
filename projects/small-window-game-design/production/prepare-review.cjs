const fs=require('node:fs'),path=require('node:path');
const project=path.resolve(__dirname,'..');
const script=JSON.parse(fs.readFileSync(path.join(project,'script/narration.ko.json'),'utf8'));
const cue=['물리적인 화면과 게임 카메라 구분','도로와 운전석 가림 비교','같은 위치에서 수평 FOV 60°/100° 비교','표적 크기와 게임 목적','이동과 관찰 방향 분리','가림 제거와 최종 체크리스트'];
const text=`# ${script.title}\n\n대본 v1 · 사용자 검토 대기 · 본편 약 4~5분 목표(실측 전)\n\n게임 디자인 설명이 목적이며 게임명은 사례다. 아래 내레이션은 원문 번역이 아닌 자체 구성이다.\n\n`+script.scenes.map((s,i)=>`## ${s.id}. ${s.title}\n\n화면: ${cue[i]}. 실제 예시 후보와의 페어는 planning/footage-plan.md 참조.\n\n${s.lines.join('\n\n')}\n`).join('\n')+'\n## 제작 메모\n\n발음용 대본의 필드 오브 뷰/에프오브이는 표시 자막에서 Field of View/FOV로 쓴다. VR 역시 영문 표기.\n기존 균형형 1.7B 목소리를 제안하며 이번 첫 장면 샘플 승인 후 전체 합성한다.\nBGM 선택 전 믹스하지 않는다. 예시에서도 한국어 내레이션을 계속하고 원음은 작게 둔다.\n원본 회원 이미지가 없으면 이름만 있는 구형 엔딩을 재사용하지 않는다.\n';
fs.writeFileSync(path.join(project,'script/review.ko.md'),text);
console.log(JSON.stringify({scenes:script.scenes.length,lines:script.scenes.reduce((n,s)=>n+s.lines.length,0),characters:script.scenes.flatMap(s=>s.lines).join('').length,scriptApproval:'pending'}));
