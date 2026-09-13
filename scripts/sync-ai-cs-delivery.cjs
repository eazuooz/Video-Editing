// Generate edit cues / chapter timecodes from the same measured timeline as audio.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),project='projects/ai-era-cs-fundamentals';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const m=read(`${project}/project.json`),t=read(`${m.tts.outputDir}/${m.tts.filenameStem}.timing.json`),script=read(m.paths.script),media=read(`${project}/sources/selected-footage.json`);
if(m.scriptRevision<6||t.narration_placement!=='continuous-across-example-and-explanation')throw Error('Expected continuous v6+ timing');
const first=new Map();for(const e of t.entries)if(!first.has(e.scene_id))first.set(e.scene_id,e.start);
const starts=script.scenes.map(s=>Math.round(first.get(s.id)*30)/30),duration=Math.round(t.duration_seconds*30)/30;
if(Math.abs(duration-m.video.durationSeconds)>.002)throw Error('Timing not synchronized');
const stamp=s=>{const n=Math.round(s*1000);return `${String(Math.floor(n/60000)).padStart(2,'0')}:${String(Math.floor(n/1000)%60).padStart(2,'0')}.${String(n%1000).padStart(3,'0')}`;};
const chapter=s=>`${String(Math.floor(s/60)).padStart(2,'0')}:${String(Math.floor(s)%60).padStart(2,'0')}`;
const bgm=['full-mix-awaiting-listening-review','full-mix-license-pending','final'].includes(m.audio.mixStatus);
const rightsPending=m.audio.mixStatus==='full-mix-license-pending'||m.audio.backgroundMusic?.previewUseOnly===true;
const music=bgm?'Blue Dream - Cheel / continuous':'MISSING - selected Blue Dream, not acquired';
const rows=[['scene','start','end','segment_type','visual','source','narration','source_audio','bgm','status']];
for(const [i,s]of script.scenes.entries()){
 const clip=media.clips.find(c=>c.scene===s.id);let cursor=starts[i];
 for(const part of clip.segments){
  const source=media.clips.find(c=>c.scene===part.sourceScene);if(!source)throw Error('Unknown source segment');
  rows.push([s.id,stamp(cursor),stamp(cursor+part.duration),'real-example',source.title,`${source.url} @ ${part.start}s`,`balanced-v${m.scriptRevision} continuous`,'-31 LUFS before narration ducking',music,'measured TTS']);cursor+=part.duration;
 }
 if(Math.abs(cursor-starts[i]-m.editing.exampleSeconds)>.01)throw Error('Footage does not fill slot');
 rows.push([s.id,stamp(cursor),stamp(starts[i+1]??duration),'channel-explanation',s.title,'original Motion Canvas',`balanced-v${m.scriptRevision} continuous`,'none',music,'measured TTS']);
 rows.push([s.id,stamp(cursor),stamp(cursor+m.editing.memeSeconds),'meme-overlay','original reinterpretation','sources/MEMES.md','continues under overlay','no borrowed meme audio',music,'overlay; no additional duration']);
}
const csvPath=path.join(root,project,'planning/edit-cues.csv');
const archive=path.join(root,project,'revisions/v5/edit-cues.csv');
if(fs.existsSync(csvPath)&&!fs.existsSync(archive))fs.copyFileSync(csvPath,archive,fs.constants.COPYFILE_EXCL);
fs.writeFileSync(csvPath,rows.map(row=>row.map(v=>`"${String(v).replaceAll('"','""')}"`).join(',')).join('\n')+'\n');
for(const lang of ['ko','en']){
 const file=path.join(root,project,`publishing/youtube.${lang}.md`),old=fs.readFileSync(file,'utf8');
 let index=0;let next=old.replace(/^\d{2}:\d{2}(?= )/gm,()=>{if(index>=starts.length)throw Error('Extra publishing chapter');return chapter(starts[index++]);});
 if(index!==starts.length)throw Error('Publishing chapter count mismatch');
 const prefix=(lang==='ko'?`상태: v${m.scriptRevision} 연속 내레이션·한영 SRT·실측 타이밍 ${duration.toFixed(3)}초. ${bgm?'BGM 믹스 생성, 전체 청취 승인 대기.':'Blue Dream 음원/라이선스 미확보로 BGM 미포함. 게시 완료 아님.'}`:`Status: v${m.scriptRevision} continuous narration and aligned KO/EN subtitles, ${duration.toFixed(3)} seconds. ${bgm?'BGM mixed; full listening approval pending.':'Blue Dream file/license missing; BGM NOT included, not publish-ready.'}`)+(rightsPending?(lang==='ko'?' 공식 채널 음원 사용 청취 검토본. 오디오 보관함 사용 조건 미확인: 게시 보류.':' Private listening review using the creator upload. Audio Library terms unverified: do not publish.'):'');
 next=next.replace(/^(?:상태:|Status:).*$/m,prefix);
 const backup=path.join(root,project,`revisions/v5/youtube.${lang}.md`);if(!fs.existsSync(backup))fs.copyFileSync(file,backup,fs.constants.COPYFILE_EXCL);
 fs.writeFileSync(file,next);
}
const report=read(m.paths.audioMixReport);
const md=[`# v${m.scriptRevision} 오디오 검토`, '', `상태: ${bgm?'내레이션 + 작은 원음 + 연속 Blue Dream, 청취 승인 대기':'내레이션 + 작은 원음 검토본. Blue Dream 미포함 — 음원/라이선스 필요'}`, '', `전체 길이: ${duration.toFixed(3)}초. 12개 독립 씬, 86개 대본 문단. 자료화면에서도 첫 순간부터 대사가 이어집니다.`, '', `- 편집기 WAV: \`${m.paths.editorAudioMix}\``, `- MP4용 AAC: \`${m.paths.audioMix}\``, `- 한국어 SRT: \`${m.paths.captionsKo}\``, `- 영어 SRT: \`${m.paths.captionsEn}\``, `- 측정: ${report.measurement.input_i} LUFS / ${report.measurement.input_tp} dBTP`, `- 내레이션 -16 LUFS 후 +1.8dB, 원음 -31 LUFS, BGM -28 LUFS 목표. 수치는 합산 전 레이어 목표입니다.`, '', '| 씬 | 시작 | 자료화면 우리 음성 LUFS | 원음 LUFS (덕킹 전) |', '|---|---|---|---|', ...report.scenes.map(s=>`| ${s.scene} | ${stamp(s.start)} | ${s.exampleVoiceLufs} | ${s.sourceLufs} |`), '', '자동 측정/받아쓰기 확인과 사람의 전체 청취 승인은 별도입니다. 미확보된 음악을 완료 상태로 표시하지 않습니다.', ''];
if(rightsPending)md.splice(3,0,'Blue Dream 공식 채널 음원을 사용한 비공개 청취 검토본입니다. 오디오 보관함 사용 조건은 미확인 상태이며 게시 보류입니다. `audio/blue-dream-creator-evidence.md`를 확인하세요.','');
fs.writeFileSync(path.join(root,project,'audio/mix-report.md'),md.join('\n'));
console.log(`Synchronized edit cues, KO/EN publishing chapters and audio report: ${duration.toFixed(3)}s`);
