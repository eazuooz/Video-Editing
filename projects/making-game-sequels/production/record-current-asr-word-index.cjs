// Keep one portable text/word evidence index; no media or recognizer rerun.
const fs=require('fs'),crypto=require('crypto');
const b='projects/making-game-sequels/production/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const voice=read(b+'narration-expanded13-index.json');if(!voice.fullCurrentHashAsrApproved)throw Error('Current technical review incomplete');
const scenes=voice.measurements.map(m=>{
 const p=m.scene==='13'?b+'asr-additive-whole-local/13-whole.json':['01','04','07','11'].includes(m.scene)?b+`asr-post-repair-local/${m.scene}-whole-v2.json`:`shared/output/narration/making-game-sequels/qwen3-1.7b-balanced-v1/asr/${m.scene}.json`;
 const a=read(p);if((a.audio_sha256||a.audioSha256)!==m.sha256||sha(m.path)!==m.sha256)throw Error('Readback hash changed '+m.scene);
 return {scene:m.scene,audioPath:m.path,audioSha256:m.sha256,seconds:m.seconds,readbackSource:p,readbackSha256:sha(p),text:a.text,words:a.words,technicalComparisonEvidence:m.readbackEvidence,humanPronunciation:'pending'};
});
const p=b+'current-asr-word-index.json';fs.writeFileSync(p,JSON.stringify({schemaVersion:1,recordedAt:new Date().toISOString(),scope:'All current13 unmixed narrated scenes; own voice ASR only, no reference lecture transcript.',sceneCount:13,paragraphs:52,scenes,finalMixAsrApproved:false,wordTimestampsAreProposal:true,humanWholeListening:'pending'},null,2)+'\n');console.log(JSON.stringify({scenes:scenes.length,words:scenes.reduce((n,s)=>n+s.words.length,0),media:0,images:0}));
