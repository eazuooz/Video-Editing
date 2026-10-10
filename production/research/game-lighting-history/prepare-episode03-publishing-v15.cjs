const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='game-lighting-history-03';
const read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,p))).digest('hex');
const defaults=read('shared/publishing/youtube-defaults.json');
const planPath=`projects/${slug}/production/measured-native-timeline-candidate-v15.json`;
const plan=read(planPath),ko=read(`projects/${slug}/script/narration.ko.json`),en=read(`projects/${slug}/script/narration.en.json`);
const english=['Updating a scene beyond the screen','Depth, distance fields and voxels','Traversing BVH boxes','Moving scenes and hybrid rendering','Samples, variance and noise','DLSS2 and reprojection','Updating DDGI probes','ReSTIR candidates and reservoirs','Visibility outside light transport','Mesh, pixel and texture budgets','Nanite clusters and hierarchy','Lumen tracing and surface cache','When changes reach the cache','Work saved and error retained'];
if(ko.scenes.length!==14 || en.scenes.length!==14)throw new Error('Current14chapters required');
const chapters=ko.scenes.map((s,i)=>{const frame=plan.slots.find(x=>x.scene===s.id).fromFrame;return {scene:s.id,actualStartFrame:frame,actualStartSeconds:frame/60,descriptionStartSeconds:i===0?0:Math.floor(frame/60),titleKo:s.title,titleEn:english[i]};});
const time=s=>`${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;
const footer=fs.readFileSync(path.resolve(root,'shared/publishing/youtube-channel-description.ko.txt'),'utf8').split('📚 수업 노트')[0].trim().replace(/━━━━━━━━━━━━━━━━━━\s*$/,'').trim();
const discord='https://discord.gg/wZuqe7fqkR';if(!footer.includes(defaults.coaching.url)||!footer.includes(defaults.membershipUrl)||!footer.includes(discord))throw new Error('Canonical footer links required');
const koBody='게임 렌더링 역사3편. 화면에 보이지 않는 물체까지 반사하려면 어떤 정보를 더 저장해야 할까요?\n\n같은 벽의 깊이·거리장·복셀 표현을 비교하고, 작은 수치로 BVH의 구간 검사를 따라갑니다. 이어서 표본의 노이즈, 재투영, DDGI 프로브와 ReSTIR의 후보 재사용을 구분합니다. 마지막에는 가시성·기하·픽셀·텍스처의 서로 다른 예산을 정리하고, 나나이트의 기하 선택과 루멘의 빛 갱신을 실제 게임·엔진 시연과 공간 도식으로 연결합니다.\n\n도식의 수치는 원리를 설명하기 위한 예시입니다. 실제 화면에 없는 내부 값이나 개발사의 성능을 추정하지 않습니다.\n\n';
const enBody='Game-rendering history, episode3. What extra information is needed to reflect an object beyond the screen?\n\nWe compare depth, distance fields and voxels for the same wall, then follow BVH interval tests with small numerical examples. We separate sample noise, reprojection, DDGI probe updates and ReSTIR candidate reuse. Finally, we distinguish visibility, geometry, pixel and texture budgets, connecting Nanite geometry selection and Lumen lighting updates to game/engine demonstrations and spatial diagrams.\n\nDiagram values are illustrative. Unseen engine internals and vendor performance are not inferred from a shot.\n\n';
const enFooter=`🎮 YamyamCoding: game programming with DirectX, Unity, Unreal Engine and computer graphics.\n\nProgramming coaching\n${defaults.coaching.url}\n\nDiscord community\n${discord}\n\nChannel membership\n${defaults.membershipUrl}`;
const descriptions={ko:koBody+chapters.map(c=>`${time(c.descriptionStartSeconds)} ${c.titleKo}`).join('\n')+'\n\n'+footer,
 en:enBody+chapters.map(c=>`${time(c.descriptionStartSeconds)} ${c.titleEn}`).join('\n')+'\n\n'+enFooter};
const comment=`레이 트레이싱과 루멘을 설명만 듣는 데서 끝내지 않고, 셰이더·렌더링 코드를 직접 설계하고 구현하는 연습을 함께 하고 싶으신가요?\n게임 프로그래밍1:1코칭·과외 안내: ${defaults.coaching.url}`;
const pub=`projects/${slug}/publishing`;const dest=path.resolve(root,pub,'prepared-upload-v15.json');
if(fs.existsSync(dest))throw new Error('Preserve prepared publishing record');
const record={preparedAt:new Date().toISOString(),status:'prepared-only-awaiting-final-QA-and-collection',slug,
 titleKo:'레이 트레이싱·루멘은 화면 밖의 빛을 어떻게 찾을까? | BVH·ReSTIR·나나이트',
 titleEn:'Ray Tracing to Lumen: BVH, ReSTIR and Nanite Beyond the Screen',
 descriptionKo:descriptions.ko,descriptionEn:descriptions.en,chapters,
 inputs:[planPath,`projects/${slug}/script/narration.ko.json`,`projects/${slug}/script/narration.en.json`,'shared/publishing/youtube-defaults.json'].map(file=>({path:file,sha256:hash(file)})),
 thumbnail:{path:`${pub}/local/thumbnail-v1.png`,sha256:hash(`${pub}/local/thumbnail-v1.png`),review:`${pub}/thumbnail-review-v1.json`,saved:false},
 uploadVariant:'captioned',uploadPath:`output/${slug}/${slug}.captioned.mp4`,cleanUploadAllowed:false,
 subtitles:['ko','en'].map(language=>({language,path:`output/${slug}/${slug}.${language}.srt`,method:'manual-file-upload-with-timing',published:false})),
 coaching:{url:defaults.coaching.url,cardStartSeconds:0,cardSaved:false,endingLinkSaved:false,pinnedCommentPrepared:true,commentStatus:'pending-video-publication',commentId:null},
 endScreen:{startSeconds:(plan.totals.finalFrames-600)/60,endSeconds:plan.finalSeconds,durationSeconds:10,playlistId:null,ownSubscribeSaved:false,externalCoachingLinkSaved:false,memberIdentitiesPreserved:true,verified:false},
 scheduling:{category:'game-lecture',time:'09:00',timezone:'Asia/Seoul',requireFreshStudioAndCalendar:true,targetDate:null,saved:false},
 actualVideoId:null,privateSaved:false,checksPassed:false,fullSettingsVerified:false,uploaded:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,
 humanWholeListening:'pending',humanPronunciation:'pending',rightsApproved:false};
fs.writeFileSync(dest,JSON.stringify(record,null,2)+'\n',{flag:'wx'});
for(const [lang,text] of Object.entries(descriptions))fs.writeFileSync(path.resolve(root,pub,`description.${lang}.v15.txt`),text+'\n',{flag:'wx'});
fs.writeFileSync(path.resolve(root,pub,'pinned-comment.ko.v15.txt'),comment+'\n',{flag:'wx'});
console.log(JSON.stringify({prepared:pub+'/prepared-upload-v15.json',chapters:chapters.length,duration:plan.finalSeconds,actualVideoId:null,uploaded:false,scheduled:false}));
