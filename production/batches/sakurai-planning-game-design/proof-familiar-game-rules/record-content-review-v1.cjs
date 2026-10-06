const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../../..');
const proof = 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules';
const read = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write = (p,d) => fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const stamp = new Date().toISOString();
const preflight = read('production/batches/sakurai-planning-game-design/preflight/familiar-game-rules.json');
if(preflight.existingProjects.length!==36 || preflight.exactMatches.length) throw Error('Review inventory changed. Read current inputs before recording.');
const specs = [
  ['one-button-game-design','script/narration','Button count and four temporal input types; familiar conventions and preserving functional input dimensions are not its central question.'],
  ['responsive-game-feedback','production/final-v2/script','Acknowledgment, rejection, selection before confirmation, pending/completed and context-specific responses. Its Enter/Space example is narrow overlap; do not repeat that comparison as a familiar-rules chapter.'],
  ['let-them-play','script/narration','First-play access, playable discovery and tutorial pacing; does not decide which existing input conventions transfer or what rebinding cannot preserve.'],
  ['play-first','script/narration','Mario first minutes, narrative and tutorial after play; no full chapter on remapping or continuous/discrete input equivalence.'],
  ['motion-sickness-games','script/narration','Camera motion, comfort settings and readable movement; preserve overlap as a boundary only, do not reproduce its comfort advice.'],
  ['small-window-game-design','script/narration','Aspect ratio, field of view, target size and screen framing; no control grammar transfer decision.'],
  ['deconstruct-analyze-rebuild','production/final-v2/script','Observe, hypothesize, implement and verify a mechanic; not a lesson on familiar control conventions or analog/digital functional limits.'],
  ['avoid-game-comparisons','script/narration','Observed action, scope of comparisons and independent explanation; not a mapping-design lesson.'],
  ['making-game-sequels','script/narration','Preserve a sequel core action and add a new decision/distance. Do not reuse its OMD actions or sequel-development claims; familiar-rules focuses on transfer between control schemes and devices.']
];
const scripts = specs.map(([slug,base,boundary])=>({slug,boundary,languages:['ko','en'].map(lang=>{
  const p=`projects/${slug}/${base}.${lang}.json`,d=read(p);
  const counts=d.scenes.map(s=>({id:s.id,paragraphs:s.lines.length}));
  if(counts.some(x=>x.paragraphs===0)) throw Error('Empty script '+p);
  return {path:p,sha256:sha(p),scenes:counts.length,paragraphs:counts.reduce((a,b)=>a+b.paragraphs,0),fullTextDirectlyRead:true};
})}));
const changedMath=['game-math-quaternion-operations','game-math-rotation-interpolation'].map(slug=>({slug,languages:['ko','en'].map(lang=>{const p=`projects/${slug}/script/narration.${lang}.json`,d=read(p);return {path:p,sha256:sha(p),scenes:d.scenes.length,paragraphs:d.scenes.reduce((a,s)=>a+s.lines.length,0),fullCurrentTextDirectlyRead:true};}),boundary:'Current complete text is rotation mathematics, reference frames, endpoints/path history, interpolation and conversions. Familiar input conventions/remapping are separate. No foreign file was edited.'}));
const studioFiles=['studio-button-title-filter.ax.txt','studio-one-button-ko-fields.json','studio-one-button-en-fields.json','studio-feedback-ko-fields.json','studio-feedback-en-fields.json','studio-feedback-en.ax.txt'];
for(const n of studioFiles){if(fs.statSync(path.join(root,proof,n)).size<100)throw Error('Missing actual Studio text '+n);}
const original='shared/output/familiar-game-rules/research/original-ANerCiyfJjo.ja.txt';
fs.mkdirSync(path.dirname(path.join(root,original)),{recursive:true});
fs.copyFileSync('C:/Users/eazuo/AppData/Local/Temp/browser-use/exports/youtube-ANerCiyfJjo-23934969-8e89-48f4-a48a-4c0d33fdc225.txt',path.join(root,original));
const reason='전체36프로젝트의 개념·KOEN제목·질문·장별주장을 검토하고, 관련9프로젝트의 현재 전체KOEN대본과 실제Studio 원버튼/입력피드백 KOEN설명을 직접 읽었다. ANerCiyfJjo 전체JA는 연구용으로만 읽었다. 신규 질문은 어떤 익숙한 조작 약속을 유지하고 재배치할지, 입력 장치의 연속/이산 기능 차이가 어디서 남는지이다. 원버튼의 네 입력 유형, 입력피드백의 확인/거절/처리상태, 튜토리얼의 첫플레이 흐름, 속편의 핵심행동 유지/새거리 질문을 재제작하지 않는다. 단순 버튼 수나 Enter/Space 확인 예시를 중심 장으로 반복하지 않고 신규 공식 실제 행동을 확인한 뒤 독립 해설을 쓴다. 원본FPS학습전이·재배치·아날로그/디지털 제약 개념은 사용하되 원문의 Chelnov 배선 일화를 확인된 하드웨어 역사로 옮기지 않는다. 최신 쿼터니언/보간26장씩 KOEN 전체 변경본문도 직접 읽었으며 회전수학으로 구별된다.';
const audit={schemaVersion:1,reviewedAt:stamp,slug:'familiar-game-rules',verdict:'distinct',scope:{inventory:36,inventoryConceptTitlesQuestionsAndChapterClaimsDirectlyRead:true,relatedFullScriptPairs:scripts.length,all36FullScriptPairsNewlyRead:false},question:'익숙한 조작 약속을 어디까지 유지하고, 재배치와 장치 변경에서 어떤 기능을 따로 설계해야 할까?',independentNewScriptCreated:false,newTtsStarted:false,newMotionCanvasSceneCreated:false,original:{videoId:'ANerCiyfJjo',fullJapaneseTranscriptDirectlyRead:true,range:'00:03–03:10',localOnlyPath:original,sha256:sha(original),researchOnly:true,copyOrTranslationForProduction:false,autoTranscriptErrorsPreserved:true,unconfirmedPersonalWiringAnecdoteNotAdopted:true},scripts,changedMath,studio:{readOnly:true,searchScope:'Focused channel title filter 버튼 returned2 actual rows; not a claim that every channel upload was text-searched.',matches:[{videoId:'DeSXTV41GXs',fullKoEnTitleDescriptionDirectlyRead:true,actualVisibility:'public',preserved:true},{videoId:'BYk6cLsO9Mc',fullKoEnTitleDescriptionDirectlyRead:true,actualVisibility:'user-scheduled-2026-10-07',preserved:true}],evidence:studioFiles.map(n=>({path:proof+'/'+n,sha256:sha(proof+'/'+n)})),priorCompletedSequelReadback:'projects/making-game-sequels/publishing/youtube-upload.json'},reason,rightsOrFootageApproval:false,nextAction:'Inspect fresh existing-game official sources, permissions, unique action intervals and control claims before narration. Input settings/menu graphics alone are explanation, not actual-game quota.'};
const auditPath=proof+'/full-content-and-studio-review-v1.json';write(auditPath,audit);
execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','familiar-game-rules','--decision','distinct','--reason',reason,'--studio-evidence',auditPath],{cwd:root,stdio:'inherit'});
execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','familiar-game-rules','--check'],{cwd:root,stdio:'inherit'});
const qPath='production/batches/sakurai-planning-game-design/queue.json',q=read(qPath),i=q.items.find(x=>x.slug==='familiar-game-rules');
Object.assign(i,{stage:'distinct-reviewed-source-candidate-research',updatedAt:stamp,duplicateReview:{verdict:'distinct',evidence:auditPath,currentInputsDigest:read('production/batches/sakurai-planning-game-design/preflight/familiar-game-rules.json').inputsDigest,currentCheckPassed:true},nextAction:audit.nextAction});
i.sourceReview.currentDuplicateDecision='distinct';q.updatedAt=stamp;q.lastProgressAt=stamp;write(qPath,q);
console.log(JSON.stringify({audit:auditPath,relatedFullKoEnPairs:scripts.length,changedMathFullPairs:changedMath.length,sourceTranscript:'local-only',newScript:false,newTts:false}));
