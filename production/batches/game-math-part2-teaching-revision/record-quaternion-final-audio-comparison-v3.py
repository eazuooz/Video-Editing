"""Bind all94 directly compared unprompted AAC transcripts to final audio."""
from pathlib import Path
import json,hashlib,subprocess,datetime
ROOT=Path(__file__).resolve().parents[3];Q=Path(__file__).parent/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def audio_digest(p,decoded=False):
 args=['ffmpeg','-v','error','-threads','2','-i',str(p),'-map','0:a:0']
 args+=['-ar','48000','-ac','2','-c:a','pcm_s16le','-f','s16le','pipe:1'] if decoded else ['-c','copy','-f','md5','pipe:1']
 proc=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 h=hashlib.sha256();small=b''
 while data:=proc.stdout.read(1024*1024):
  if decoded:h.update(data)
  else:small+=data
 assert proc.wait()==0,proc.stderr.read().decode(errors='replace')
 return h.hexdigest() if decoded else small.decode().strip()
audit={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'Codex direct expected/raw transcript meaning comparison; CPU recognition without expected-text prompt','method':'Read complete AAC readback scene by scene in timeline order; compare numbers, formulas, operation order and teaching meaning. Resolve long-chunk overlap and repeated-number omissions with9 bounded unprompted windows. Exact final encoded AAC and decoded PCM equality transfers evidence across visual-only corrections.','humanListeningComplete':False,'recognitionIsHumanListening':False,'rightsReviewComplete':False,'backgroundMusic':False,'sourceAudio':False,'episodes':{},'diagnosticWindows':read(Q/'baseline-diagnostic-readback.json'),'diagnosticSha256':sha(Q/'baseline-diagnostic-readback.json'),'recognitionLimitations':['06 duplicated earlier20s text and hallucinated a zero-duration thank-you; bounded20–37s readback is complete and has neither.','09 repeated four0 components collapsed in long readback; bounded19.8–28.7s contains allfour.','20 next-video greeting appears only in long-scene recognition; bounded92–108.2s contains the expected transition.','N08 repeated2 denominator rendered as Korean 이 in bounded output; exact expected sqrt2/2 preserved.','Conjugate/inverse/half-angle, ski and quaternion have recognition homophones; mathematical formulas and intended meaning compared; human pronunciation/listening remains pending.'],'mathMeaningChecks':['i²=-1; (2,1)i=(-1,2), length√5.','wxyz Hamilton/right-handed column-vector local-to-world; q[0,v]q⁻¹.','qx90/z90 half-angle√2/2; repeatedz90 yields180 and q⁴=-1, same endpoint not same traveled path.','q/-q equal orientation, conjugate/inverse distinct; zero4-vector invalid; [3,0,0,4] normalized[.6,0,0,.8]; general inverse conjugate/norm²; scalar2 inverse.5.','x×y=+z and y×x=-z; fixedx90→y90 applied toez=-ey, reversedex.','world delta B*A⁻¹ left, body A⁻¹*B right; samez30→90 difference60; different-axis angles not subtraction.','2acos(clamp(abs(dot))) minimum endpoint difference0–180, not accumulatedtricks or positiondistance.','log/exp selected branch/half-angle/radians; rotationfraction not halving fourcomponents.','z90(1,0,1)=(0,1,1), unchangedz1 and norm√2; one-sided multiply produces scalar-c.','four32-bitcomponents16bytes excludes alignment; storage size not universalperformanceclaim.']}
for episode,expected_count in [('foundations',50),('calculations',44)]:
 slug='game-math-quaternion-'+episode+'-v3';P=ROOT/'projects'/slug;m=read(P/'project.json');t=read(P/'production/timeline.json');statepath=Q/(slug+'-mixed-asr-v3-execution.json');state=read(statepath)
 assert state['exitCode']==0 and state['completed']==expected_count and sha(ROOT/state['source'])==state['sha256'] and sha(P/'production/timeline.json')==state['timelineSha256']
 source=ROOT/state['source'];current=ROOT/m['paths']['videoClean'];packet=audio_digest(source);pcm=audio_digest(source,True)
 assert audio_digest(current)==packet and audio_digest(current,True)==pcm,'Visual correction must preserve all original/final narration audio.'
 rows=[]
 for slot in t['scenes']:
  p=ROOT/f'shared/output/{slug}/mixed-asr-v3/{slot["id"]}.json';raw=read(p)
  rows.append({'scene':slot['id'],'preservedOriginal':slot['preservedOriginal'],'expectedKo':' '.join(c['text'] for c in slot['cues']),'actualUnpromptedReadback':raw['text'],'rawSha256':sha(p),'readbackSource':p.relative_to(ROOT).as_posix(),'directMeaningCompared':True,'humanListeningComplete':False})
 assert len(rows)==expected_count
 audit['episodes'][slug]={'asrActualInput':state['source'],'asrInputSha256':state['sha256'],'currentClean':m['paths']['videoClean'],'currentCleanSha256':sha(current),'identicalEncodedAudioMd5':packet,'identical48kStereoDecodedPcmSha256':pcm,'sceneCount':len(rows),'completeDirectTranscriptComparison':True,'numericAndConventionMeaningPassed':True,'scenes':rows}
 state['fullDirectComparisonComplete']=True;state['directComparisonEvidence']=(Q/'final-aac-meaning-comparison.json').relative_to(ROOT).as_posix();state['humanListening']='pending';write(statepath,state)
write(Q/'final-aac-meaning-comparison.json',audit)
print('Compared50+44 actual AAC scene transcripts; final visual revisions preserve encoded audio and decoded PCM exactly; human listening remains pending.')
