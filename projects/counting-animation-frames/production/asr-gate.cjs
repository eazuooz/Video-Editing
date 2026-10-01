// A reviewed numerical-orthography exception is bound to this exact WAV hash.
// Never reduce the default gate or accept a different take from an old review.
const fs=require('node:fs'),path=require('node:path');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const allowedNumericPairs=new Set(['일:1','예순:60','열두:12','영점이:02','서른:30','영점사:04','두:2']);
function reviewedNumeralOnly(scene){
 const review=read(path.join(__dirname,'narration-scene-review.json')).scenes.find(s=>s.scene===scene.scene&&s.audioSha256===scene.audio_sha256&&s.result==='passed-content-and-ending');
 return Boolean(review&&scene.scene==='02'&&scene.audio_sha256==='1952e3381f9b5a17fd27831ed03bf53df069690b19f3c76987571a75dded5a7f'&&scene.differences.length===10&&scene.differences.every(d=>d.kind==='replace'&&allowedNumericPairs.has(d.expected+':'+d.recognized)));
}
function failures(report){return report.scenes.filter(s=>!s.acousticChecks.endingHeuristicPassed||(s.similarity<.94&&!reviewedNumeralOnly(s)));}
module.exports={failures,reviewedNumeralOnly};
