// Actual still/clock observations; never promotes them to moving/final approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ex=b+'/local/part1-boundaries-v178/execution.json',boards=b+'/local/part1-boundaries-v178/boards-v179.json';
const e=read(ex),d=read(boards),out=b+'/part1-boundary-direct-review-v180.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve existing direct review');
if(e.exitCode!==0||e.results.length!==17)throw Error('Expected completed17 samples');
for(const r of e.results)if(sha(r.path)!==r.sha256)throw Error('Changed sample '+r.id);
const notes={
 'wheel-112':'Updates/Static vs. Dynamic Caching/WPO Disable Distance lecture card. Exclude from actual-action time.',
 'wheel-112-5':'Same lecture card; no actual Ferris-wheel view.',
 'wheel-113':'Same lecture card; no actual Ferris-wheel view.',
 'wheel-185-8':'Ferris-wheel structure and ground shadow; viewport menu is open. Do not infer selected VSM/cache diagnostic from menu alone.',
 'man-37':'Running mannequin and moving corridor; actual demonstration.',
 'man-37-5':'Mannequin/corridor actual pixels before terminal lecture card.',
 'man-38':'Dissolving Note on TSR lecture card overlaps demonstration. Reject terminal portion as actual footage.',
 'fan-32':'Actual rotating rust fan.',
 'fan-32-5':'Actual rotating rust fan.',
 'fan-33':'Actual fan;34.001 browser clock showed terminal lecture card. Conservative normal-speed end33.',
 'mobile-263':'Already inset phone test under lecture/presenter surround; crop only the actual phone test.',
 'mobile-264':'Same inset phone test; wall/graph visible.',
 'mobile-265':'Same inset phone test; wall/graph visible.',
 'mobile-266':'Same inset phone test; wall/graph visible.',
 'profile-crop':'Android/Mali/Adreno device-profile list and profile table readable; lecture heading excluded. Native crop500,312,1008,567.',
 'lod-crop':'Android profile texture LOD settings and category rows readable; main device-profile list retained. No lecture heading.',
 'console-crop':'Console-variable groups and World Min/Max LOD Size fields readable. No performance improvement inferred.'
};
const j={schemaVersion:1,recordedAt:new Date().toISOString(),physicalPart:'game-lighting-history-04-1',extraction:{path:ex,sha256:sha(ex)},boards:{path:boards,sha256:sha(boards),directlyReadAllThree:true},samples:e.results.map(r=>({id:r.id,path:r.path,sha256:r.sha256,seconds:r.seconds,crop:r.crop,directlyRead:true,observation:notes[r.id]})),browserObservations:[
 {source:'wheel',seconds:114,status:'PAUSED,ready4',observation:'Updates lecture card still present; exclude.'},
 {source:'wheel',seconds:114.5,status:'PAUSED',observation:'Actual Ferris-wheel structure and matching ground shadow. Conservative actual start114.5, not112.'},
 {source:'mobile',seconds:260,status:'PAUSED',observation:'Full phone/test view with Clear Coat rock, graph and UI.'},
 {source:'mobile',seconds:261,status:'PAUSED',observation:'Full phone/test view, now approaching GBuffer Normals wall.'},
 {source:'mobile',seconds:262,status:'PAUSED',observation:'Phone/test now inset with presenter outside. Crop change lies between261 and262; no guessed frame-accurate boundary adopted.'}
 ],sourceBindings:e.sources,proposedConservativeRanges:{wheel:[114.5,185.8],man:[0,37.5],fan:[0,33],fortniteRock:[240,260],fortniteWallInset:[276,289.8]},ttsInputMutation:false,original111OrFiveFramingChanged:false,allMovingPixelsReviewed:false,allFinalPixelsReviewed:false,currentFinalMixedAsrApproved:false,uploaded:false,limits:['These are source stills and actual browser clocks, not independent source-offset certification.','Final allocation must preserve whole approved narration and meet measured60:40 within one frame.','Do not extend actual clips using cards, loops, frozen frames or slow playback.','Fixed caption center960,970 remains unchanged; adjust source crop or cue wrapping for mobile buttons.']};
fs.writeFileSync(path.join(root,out),JSON.stringify(j,null,2)+'\n');
console.log(JSON.stringify({record:out,samples:17,boards:3,movingApproved:false,finalApproved:false}));
