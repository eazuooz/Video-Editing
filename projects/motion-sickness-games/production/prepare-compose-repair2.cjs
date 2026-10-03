// Adapt the preservation compiler for six accepted repair1 candidates and one repair2.
const fs=require('node:fs'),path=require('node:path');
const p=path.join(__dirname,'compose-repaired-v2.py');
let s=fs.readFileSync(p,'utf8');
s=s.replace("WORK=BASE/'production/repair1'","WORK=BASE/'production/repair2'\nPRIOR=BASE/'production/repair1'");
const start=s.indexOf("review=read(WORK/'direct-review.json')");
const end=s.indexOf("v1=ROOT/",start);
if(start<0||end<0)throw Error('Compiler structure changed.');
s=s.slice(0,start)+`prior_request=read(PRIOR/'request.json')
# Original repair1 input versions are preserved beside the new request.
for entry in prior_request['inputs']:
 baseline=WORK/'baseline'/Path(entry['path']).relative_to(BASE.relative_to(ROOT))
 source=baseline if baseline.exists() else ROOT/entry['path']
 assert sha(source)==entry['sha256'],str(source)
prior_review=read(PRIOR/'direct-review.json')
new_review=read(WORK/'direct-review.json')
accepted={entry['scene']:entry for entry in prior_review['scenes'] if entry['decision']=='content-readback-pass'}
assert set(accepted)==set(request['acceptedRepair1Ids'])
for entry in new_review['scenes']:
 if entry['decision']=='content-readback-pass':
  assert entry['scene']=='05' and entry['scene'] not in accepted
  accepted[entry['scene']]=entry
expected={edit['id'] for edit in prior_request['edits']}
assert set(accepted)==expected,'Six retained candidates and new05 must pass direct current-hash review.'
def candidate_path(sid):
 entry=accepted[sid]
 cp=ROOT/entry['audio']
 assert sha(cp)==entry['audio_sha256']
 ap=ROOT/entry['asr']
 assert sha(ap)==entry['asr_sha256'] and read(ap)['audio_sha256']==sha(cp)
 return cp
for sid in accepted:candidate_path(sid)
`+s.slice(end);
s=s.replace("read(WORK/'splice-plan.json')","read(PRIOR/'splice-plan.json')");
s=s.replaceAll('candidate/\'chunks\'/f"{patch[\'candidateId\']}-scene.wav"',"candidate_path(patch['candidateId'])");
s=s.replace('candidate_asr=read(candidate/\'asr\'/f"{patch[\'candidateId\']}.json")',"candidate_asr=read(ROOT/accepted[patch['candidateId']]['asr'])");
s=s.replace("manifest=read(BASE/'project.json');manifest['tts'].update(outputDir=v2.relative_to(ROOT).as_posix(),filenameStem='motion-sickness-games-qwen3-1.7b-balanced-v2')",`manifest=read(BASE/'project.json');manifest['tts'].update(outputDir=v2.relative_to(ROOT).as_posix(),filenameStem='motion-sickness-games-qwen3-1.7b-balanced-v2')
manifest['paths'].update(narration=(v2/'motion-sickness-games-qwen3-1.7b-balanced-v2.wav').relative_to(ROOT).as_posix(),captionsKo=(v2/'motion-sickness-games-qwen3-1.7b-balanced-v2.srt').relative_to(ROOT).as_posix(),captionsEn=(v2/'motion-sickness-games-qwen3-1.7b-balanced-v2.en.srt').relative_to(ROOT).as_posix())`);
s=s.replace("'unchangedParagraphs':53,","'candidateReadbacks':[str(PRIOR.relative_to(ROOT)/'direct-review.json'),str(WORK.relative_to(ROOT)/'direct-review.json')],\n 'compositionInputs':request['inputs'],'unchangedParagraphs':53,");
if(s.includes("candidate/'"))throw Error('Unconverted candidate reference.');
fs.writeFileSync(path.join(__dirname,'compose-mixed-repaired-v2.py'),s);
console.log('Mixed-source preservation compiler prepared; not executed.');
