const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../..'),base=path.join(root,'projects/blank-project-coding');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const a=fs.readFileSync(path.join(base,'script/original-attachment.ko.txt'),'utf8').replace(/\r\n/g,'\n');
const b=fs.readFileSync(path.join(base,'script/original-continuation-17-24.ko.txt'),'utf8').replace(/\r\n/g,'\n');
function chapters(raw){return [...raw.matchAll(/^# ([^\n]+)\n([\s\S]*?)(?=^# |$(?![\s\S]))/gm)].map(m=>({number:Number(m[1].match(/^(\d+)\./)?.[1]||0),title:m[1].replace(/^\d+\. /,''),raw:m[2].trim()}));}
let all=[...chapters(a),...chapters(b)];
const broken=all.find(c=>c.number===16),repeat=all.find(c=>c.number===19);
broken.preservedFragment=broken.raw;
broken.raw=broken.raw+' 했다고 해보겠습니다.\n\n'+repeat.raw.split('했다고 해보겠습니다.')[1].trim();
broken.reconstructed=true;
function plain(raw){return raw.replace(/```[^\n]*\n[\s\S]*?```/g,'').replace(/\*\*/g,'').replace(/\[Inference\]\s*/g,'').trim();}
const scenes=[];
for(const c of all){
 const atoms=plain(c.raw).split(/\n\s*\n/).map(s=>s.replace(/\n/g,' ').trim()).filter(Boolean);
 const paras=[];let p='';
 for(let i=0;i<atoms.length;i++){p+=(p?' ':'')+atoms[i];if((p.length>=75&&/[.!?。”]$/.test(p))||p.length>=125||i===atoms.length-1){paras.push(p);p='';}}
 let group=[];let n=0;
 function flush(){if(!group.length)return;scenes.push({id:String(scenes.length+1).padStart(2,'0'),title:c.title,chapter:c.number,chapterPart:++n,source:'user-original',sourceReconstructed:c.reconstructed||false,lines:group});group=[];}
 for(const line of paras){if(group.length&&group.join(' ').length+line.length>280)flush();group.push(line);}flush();
 const expected=plain(c.raw).replace(/\s/g,''),actual=scenes.filter(s=>s.chapter===c.number).flatMap(s=>s.lines).join('').replace(/\s/g,'');
 if(expected!==actual)throw Error('Original loss in chapter '+c.number);
}
scenes.push({id:String(scenes.length+1).padStart(2,'0'),title:'얌얌코딩 프로그래밍 코칭·과외',chapter:25,source:'previous-user-authorized-coaching-ending',lines:['혼자 공부하다가 어디서부터 시작해야 할지 모르겠다면, 지금까지 만들어본 코드와 막힌 지점을 정리해보세요. 얌얌코딩 프로그래밍 코칭과 과외에서 여러분의 공부 방향을 함께 살펴볼 수 있습니다.','과외 안내 링크는 영상 설명란과 마지막 화면, 고정댓글에 남겨두겠습니다. 직접 생각하고 설계하고 구현하는 실력, 그 작은 시작부터 함께 만들어가겠습니다.']});
const payload={title:'AI 시대, 신입 개발자가 취업하기 어려운 진짜 이유',language:'ko',revision:'original-restored-v2',sourcePolicy:'Original chapter order and wording preserved; emphasis comes from visual contrast and delivery. Markdown and non-spoken code/Inference marker retained separately. Chapter16 truncated source explicitly reconstructed from supplied19 pending response.',scenes};
write(path.join(__dirname,'narration.ko.json'),payload);
write(path.join(__dirname,'original-chapters.json'),all);
const audit={checkedAt:new Date().toISOString(),sourceAttachmentSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(base,'script/original-attachment.ko.txt'))).digest('hex'),chapters:all.map(c=>({number:c.number,title:c.title,wordSequencePreserved:true,reconstructedTruncation:!!c.reconstructed,scenes:scenes.filter(s=>s.chapter===c.number).map(s=>s.id)})),omissions:[],order:all.map(c=>c.number),sceneCount:scenes.length,narrationCharacters:scenes.flatMap(s=>s.lines).join('').length,codeNotReadAloud:'chapter18 int main() {} shown as C++ syntax, source csharp fence preserved in raw file',inferenceMarker:'shown on screen as 추론; not read as an English word',status:'passed-original-order-and-content-with-explicit-chapter16-source-gap'};
write(path.join(__dirname,'original-preservation-audit.json'),audit);
const tts=structuredClone(payload),pronunciations={'Linked List':'링크드 리스트','Next Pointer':'넥스트 포인터','Pointer':'포인터','Node':'노드','Head':'헤드','C++':'씨 플러스 플러스','Feature Creator':'피처 크리에이터','Problem Solver':'프라블럼 솔버','System Maintainer':'시스템 메인테이너','Recognition':'레커그니션','Recall':'리콜','Problem Solving':'프라블럼 솔빙','Stack Overflow':'스택 오버플로','GitHub':'깃허브','Breakpoint':'브레이크포인트','Line Clear':'라인 클리어','Collision':'컬리전','Rotation':'로테이션','Board':'보드','Block':'블록'};
for(const s of tts.scenes)for(let i=0;i<s.lines.length;i++)for(const [k,v]of Object.entries(pronunciations))s.lines[i]=s.lines[i].replaceAll(k,v);
write(path.join(__dirname,'narration.tts.ko.json'),tts);write(path.join(__dirname,'pronunciation-map.json'),pronunciations);
const manifest=read(path.join(base,'project.json'));manifest.paths.script='projects/blank-project-coding/revisions/original-restored-v2/narration.tts.ko.json';manifest.tts.outputDir='shared/output/narration/blank-project-coding/original-restored-v2';manifest.tts.filenameStem='blank-project-coding-original-restored-v2';manifest.tts.sceneGapSeconds=.65;manifest.editing.exampleSeconds=0;manifest.tts.maxNewTokens=1536;
write(path.join(__dirname,'voice.manifest.json'),manifest);
fs.writeFileSync(path.join(__dirname,'narration.review.txt'),payload.title+'\n\n'+all.map(c=>'# '+c.number+'. '+c.title+'\n\n'+c.raw).join('\n\n')+'\n\n# 얌얌코딩 코칭·과외\n\n'+scenes.at(-1).lines.join('\n\n')+'\n');
console.log(JSON.stringify({sceneCount:scenes.length,characters:audit.narrationCharacters,chapters:audit.order}));
