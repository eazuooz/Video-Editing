const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const completion=JSON.parse(fs.readFileSync(path.join(__dirname,'all-tts-completion-v2.json'),'utf8'));
for(const episode of completion.episodes){
 const p=path.join(root,'projects',episode.slug,'README.md');
 const s=fs.readFileSync(p,'utf8');
 if(s.includes('현재 제작 상태 · 2026-10-09 검정 테마 수정'))continue;
 const newline=s.indexOf('\n');
 const update=`\n\n현재 제작 상태 · 2026-10-09 검정 테마 수정: 사용자 명시 요청에 따라 이 시리즈의 설명은 \`research-black-v1\`(검정 배경·흰 본문·노란 제목·의미별 벡터 색)로 제작한다. 투영된 앞/옆/윗면·가림과 내레이션에 맞는 움직임을 유지한다. 기존 흰 검수본과 음성은 보존한다. \`production/research/game-lighting-history/black-style-revision-v2.json\`을 따른다.\n\n현재 내레이션은 실제 생성·전체 WAV 디코드 완료(${episode.durationSeconds.toFixed(3)}초)이며 원래 연구 GPU의 재개도 기록했다. 음성 청취·발음, 정확한 자막 타이밍, 현재 검정 설명 픽셀, 실제 자료/권리, 최종 믹스·60:40·렌더·수집·비공개 업로드는 아직 검수/제작 중이다. 아래 이전 진행 기록은 역사로 보존하며 최신 체크포인트를 우선한다.\n`;
 fs.writeFileSync(p,s.slice(0,newline)+update+s.slice(newline));
}
console.log('Updated four current series README states; historical text preserved.');
