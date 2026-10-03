// Record direct visual research; deliberately leave locked TTS and final gates unchanged.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,o)=>fs.writeFileSync(path.join(root,p),JSON.stringify(o,null,2)+'\n');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const at=new Date().toISOString(),request=read(base+'repair1/request.json');
for(const input of request.inputs)if(sha(input.path)!==input.sha256)throw Error('Frozen repair input changed: '+input.path);
const paths=['source-fit-followup/research-images.json','source-fit-followup/edges/images.json','source-fit-followup/talos-action-edges/images.json'];
const reviewed=paths.map(relative=>{
  const p=base+relative,o=read(p),images=o.images??o.frames,contacts=o.contacts??o.contactSheets;
  Object.assign(o,{directReview:'completed-source-fit-research-only',reviewedAt:at,reviewedImageEntries:images.length,finalTimingApproved:false,directReviewEvidence:base+'source-fit-followup/direct-review.json'});
  write(p,o);
  return {index:p,indexSha256:sha(p),imageEntries:images.length,contactSheets:contacts.map(file=>({file,sha256:sha(file)}))};
});
const audit=read(base+'source-fit-followup/initial-audit.json');
const report={recordedAt:at,scope:'Supplemental source-action/timing research against initial v1 speech. Not final cuts, every-cue approval, current repaired voice approval, or 60:40 approval.',
  reviewedImageEntries:reviewed.reduce((n,x)=>n+x.imageEntries,0),reviewedSources:reviewed,
  frozenInputsUnchanged:true,frozenInputHashes:request.inputs,initialAudit:base+'source-fit-followup/initial-audit.json',
  provisionalDeficits: audit.scenes.flatMap(s=>s.groups.filter(g=>g.provisionalDeficitSeconds>0).map(g=>({scene:s.scene,paragraphs:g.paragraphs,seconds:g.provisionalDeficitSeconds,overlappingGroups:s.overlappingParagraphGroupsRequireSpecificAllocation}))),
  findings:[
    'The total394.4-second bank cannot prove paragraph-level fit or the final ratio. Initial voice group05p4–6,09p3–6 and11p3–6 exceed their directly assigned banks.',
    'The07 bank assigns paragraph4 to two groups. Their deficits must not be added blindly; allocate each source interval to specific current speech windows without repeating source time.',
    'PWS69–89 contains tool/idle/minor-view changes and is rejected as quota padding. PWS90.5–98.9 does show nozzle/aim movement against a mostly stable playground and can teach independent aim, but does not prove spraying.',
    'PWS169–187 shows actual roundabout washing and view/tool changes. It can extend general washing observations without repeating the existing187–199 bank.',
    'PWS227–247 is not a single overhead washing action: a radial extension menu appears around233, and later views have little/no water. Do not count the menu/idle or describe the whole interval as spraying.',
    'PWS339.1–344.9 moves from upper boards toward the lower post;357.8/362/367 show post washing. Extending05 through367 requires removing/reallocating the overlap359–367 from07.',
    'PWS319.1/328.5/338.9 show upper blue boards/posts and spraying. Use only the unused tail after the final05p3 allocation for later generic target observations.',
    'PWS397–403.8 is dinosaur-slide washing, not boards/posts. It can accompany general tool/surface observations only; do not place it under a specific boards/posts sentence.',
    'PWS493.1–509.9 shows slide-side boards/posts washing. Only the unused tail after final11p1 may extend11p5–6 generic action review.',
    'Talos42.0 is still the purple-field first-person action;42.1/42.2 show the title. The frozen out42.2 is too late. Use an exclusive out no later than42.0 unless every native boundary frame is rechecked.',
    'Talos52.0 still shows the puzzle wall;52.2/52.2667/52.3333/52.4 show the snowy bridge with an unclear player-action/cinematic basis and do not show the claimed tilting walls/lasers. Exclude the snow from this paragraph and the actual60% count.',
    'Talos47/47.5 shows a carried cube and first-person puzzle movement;48–50 shows the wall/lasers tilting, then51–52 returns to the forward puzzle view. These are appropriate normal-speed action examples, ending before the snow cut.',
    'Talos15.5–16 shows the hand/device interaction.16.0–20.7333 and23.0333–30.1667 can extend the general direction/rule paragraph without repeating the platform/upper-device and tilting-wall paragraphs.',
    'All three contact sheets of the final25 Talos samples were read directly. The47 original edge entries were regenerated through the full linear decoder after two fast-seek mmco warnings; the preserved fast-seek images are not approval evidence.'
  ],
  provisionalRoutes:[
    {scene:'01',paragraphs:[2,3,4],sourceId:'PF5L_2g9UVQ',candidateIntervals:[[90.5,98.9],[99,118]],visibleAction:'Nozzle/aim positions move while playground landmarks remain mostly stable.',constraint:'Select to current v2 speech; no claim that the early nozzle segment sprays.'},
    {scene:'01',paragraphs:[5,6],sourceId:'PF5L_2g9UVQ',candidateIntervals:[[169,187]],visibleAction:'Actual roundabout spraying and tool/view changes.',constraint:'Independent WIP context/closing observation; do not repeat187–199.'},
    {scene:'05',paragraphs:[4,5,6],sourceId:'PF5L_2g9UVQ',candidateIntervals:[[339,367]],visibleAction:'Reposition from upper surface toward lower posts, then surface washing.',constraint:'Reallocate07 overlap359–367; exact repair length and each sentence/action must be verified.'},
    {scene:'07',paragraphs:[1],sourceId:'6slinvkF0Rs',candidateIntervals:[[31.033333,35.866667],[36,39.833333]],visibleAction:'Platform movement and view turning toward an upper device.',constraint:'Normal30fps clock converted to60fps only; verify native cut boundaries.'},
    {scene:'07',paragraphs:[2],sourceId:'6slinvkF0Rs',candidateIntervals:[[47.5,52],[40.2,42]],visibleAction:'Puzzle walls and laser lines tilt; another first-person view turns toward the purple field.',constraint:'Exclude title42.1+ and snow52.2+; exact sentence alignment pending.'},
    {scene:'07',paragraphs:[3],sourceId:'6slinvkF0Rs',candidateIntervals:[[16,20.733333],[23.033333,30.166667]],visibleAction:'Hand/device interaction and independent first-person puzzle views.',constraint:'Separate attempts/cuts; no invented continuous solve or repeated intervals.'},
    {scene:'07',paragraphs:[4,5,6],sourceId:'PF5L_2g9UVQ',candidateIntervals:[[247.5,267],[367,383]],visibleAction:'Look up at structure then another boards/post surface.',constraint:'Do not reuse05’s extended359–367. Fit repaired paragraph4 then current retained5/6.'},
    {scene:'09',paragraphs:[3,4,5,6],sourceId:'PF5L_2g9UVQ',candidateIntervals:[[465,483.8],[319.1,338.9],[397,403.8]],visibleAction:'Specific boards/posts first, then generic tool-to-surface observations.',constraint:'319.1+ only if unused by05; dinosaur only after specific boards/posts sentences.'},
    {scene:'11',paragraphs:[3,4,5,6],sourceId:'PF5L_2g9UVQ',candidateIntervals:[[528,552.4],[493.1,510]],visibleAction:'Upper bars first, then generic inspection of spraying and target surfaces.',constraint:'493.1+ only after final11p1 ends; exclude notification552.5+.'}
  ],
  sourceDecode:{linearEdgeSession:90652,exitCode:0,errorOutput:'',talosExtraProbeExitCode:0,errorOutput:'',supersededFastSeekWarnings:2},
  currentRepairedSpeechApproved:false,finalTimingApproved:false,finalBodyRatioApproved:false,everyCaptionCutReviewed:false,
  nextAction:'Leave locked TTS inputs unchanged while repair8552/PID47052 runs. Directly approve all seven candidate readbacks before composition; use the full current-hash v2 ASR to install exact non-repeated source intervals and review every caption/cut before rendering.'};
write(base+'source-fit-followup/direct-review.json',report);
console.log(JSON.stringify({reviewedImageEntries:report.reviewedImageEntries,report:base+'source-fit-followup/direct-review.json',frozenInputsUnchanged:true,finalTimingApproved:false}));
