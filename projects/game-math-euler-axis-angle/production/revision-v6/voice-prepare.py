"""CPU-only V6 voice inputs and106 beat boundaries; no synthesis or audio edits."""
from pathlib import Path
import hashlib,json,datetime,os
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6/voice';KO=P/'script/revision-v6-article-flow/narration.ko.json';EN=KO.with_name('narration.en.json')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.prepare.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(t,p)
def main():
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 O.mkdir(parents=True,exist_ok=True)
 script=read(KO);assert len(script['scenes'])==41 and sum(len(s['lines']) for s in script['scenes'])==250
 prepared=json.loads(json.dumps(script));overrides=[];scenes=[]
 for s,inp in zip(script['scenes'],prepared['scenes']):
  for i,line in enumerate(s['lines']):
   text=line
   if s['id']=='v6-01' and i==0:text=text.replace('안녕하세요. 얌얌코딩입니다.','안녕하세요, 얌얌코딩입니다.')
   if s['id']=='v6-32' and i==0:text=text.replace('영문 소문자 e입니다.','영문 소문자 이입니다.')
   inp['lines'][i]=text
   if text!=line:overrides.append(dict(scene=s['id'],line=i+1,display=line,speech=text,reason='Approved pronunciation/punctuation alias only; canonical KO remains unchanged.'))
  coverage=[];beats=[]
  for beat in s['teachingBeats']:
   a=beat['speech']['lineNumbers'];b=beat['resultCheckAndConnection']['lineNumbers'];coverage+=a+b
   assert a and a==list(range(a[0],a[-1]+1)) and beat['visual']['afterLine']==a[-1]
   motion=beat['visual'].get('plannedMotionSeconds');hold=beat['hold']['plannedSeconds']
   assert motion is None or motion>=0
   beats.append(dict(id=beat['id'],speechLines=a,resultCheckLines=b,seamAfterLine=a[-1],
    nextLine=a[-1]+1 if a[-1]<len(s['lines']) else None,visual=beat['visual'],hold=beat['hold'],
    plannedObservationBudgetSeconds=None if motion is None else motion+hold,
    placement='After completed speech lines, before result-check/next speech; subtract existing measured quiet duration, never cut words.',
    measuredSeam=None,status='planned; requires source ASR/alignment and PCM seam inspection'))
  assert coverage==list(range(1,len(s['lines'])+1)),s['id']
  scenes.append(dict(id=s['id'],title=s['title'],lineCount=len(s['lines']),
   speechTextSha256=hashlib.sha256(' '.join(inp['lines']).encode('utf8')).hexdigest(),
   output=rel(O/'chunks'/f'{s["id"]}-scene.wav'),beats=beats))
 assert sum(len(s['beats']) for s in scenes)==106
 old=read(P/'production/revision-v3/tts-manifest.json');old_chunks=R/old['tts']['outputDir']/'chunks'
 preserved=[dict(file=rel(f),sha256=sha(f)) for f in sorted(old_chunks.glob('??-scene.wav'))]
 assert len(preserved)==26,'Current approved V5 narration chunks must remain present'
 reference=R/'shared/voice-reference/reference-15-35s.wav';reftext=reference.with_suffix('.ko.txt')
 assert reference.exists() and reftext.exists()
 save(H/'voice-input.ko.json',prepared)
 manifest=dict(schemaVersion=2,slug=P.name,revision='article-flow-v6',
  paths=dict(script=rel(H/'voice-input.ko.json'),scriptEn=rel(EN),captionsKo=rel(O/'body.ko.srt'),captionsEn=rel(O/'body.en.srt')),
  editing=dict(exampleSeconds=0,narrationPlacement='continuous-across-example-and-explanation'),
  tts=dict(engine='qwen3-tts',language='Korean',reference=rel(reference),referenceText=rel(reftext),
   model='qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base',outputDir=rel(O),filenameStem='euler-article-flow-v6',
   renderMode='scene',sceneGapSeconds=.72,tailRatioThreshold=.07,tailDecayMsThreshold=70,maxRenderAttempts=1,
   maxNewTokens=4096,edgeFadeSeconds=0,gpuMinimumFreeMiB=7168,
   gpuProfileReason='Root/user GPU grant2026-10-20: approved BF16 scene batch1 voice;6144MiB allocator cap and7168MiB free. Prior measured peak5498MiB plus margin; existing editor cache remains open. Longest scene841 characters;4096 token ceiling avoids artificial EOS. No speed conversion or automatic tail-heuristic retakes.'),
  executionState='prepared-not-rendered; root GPU allocation required')
 save(H/'voice-tts-manifest.json',manifest)
 plan=dict(schemaVersion=1,revision='article-flow-v6',preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  inputs=dict(ko=rel(KO),koSha256=sha(KO),ttsInput=rel(H/'voice-input.ko.json'),ttsInputSha256=sha(H/'voice-input.ko.json'),
   manifest=rel(H/'voice-tts-manifest.json'),manifestSha256=sha(H/'voice-tts-manifest.json'),
   referenceSha256=sha(reference),referenceTextSha256=sha(reftext)),
  voice=dict(model=manifest['tts']['model'],identity='existing approved reference15–35s; transcript-assisted clone prompt reused across batch',
   settings='BF16, batch1, Korean, non_streaming_mode=True; existing Qwen sampling defaults; no invented Base style instruction or speed parameter',
   gpuMinimumFreeMiB=7168,allocatorCapMiB=6144,englishVoiceRequired=False),
  pacing=dict(policy='article-faithful-teaching-pace-v1',renderUnit='one continuous PCM per scene; not per line/beat',
   seamPolicy='Insert only at complete planned sentence/paragraph boundaries confirmed by actual ASR word times and PCM quiet waveform; preserve original samples.',
   noSpeedChange=True,noFixedPerSentenceSilence=True,noBlanketTrim=True,sceneGapIsNotObservationTime=True,
   observationTimes='planned only; per-beat visual/hold budgets may be extended after measured playback/readability. Never force null motion into zero.',
   measuredTiming='pending source PCM/whole ASR/alignment',actualListening='pending'),
  overrides=overrides,sceneCount=41,lineCount=250,beatCount=106,scenes=scenes,
  preservedV5Chunks=preserved,
  english=dict(file=rel(EN),status='available-unreviewed' if EN.exists() else 'translation-in-progress'),
  execution=dict(prepare='qwen3-tts/.venv/Scripts/python.exe -X utf8 '+rel(H/'voice-prepare.py'),
   tts='qwen3-tts/.venv/Scripts/python.exe -u -X utf8 '+rel(H/'voice-render.py')+' --gpu-approved',
   asr='qwen3-tts/.venv/Scripts/python.exe -u -X utf8 '+rel(H/'voice-review.py')+' --gpu-approved'),
  humanWholeListening='pending',mediaJobsStartedByPreparation=0)
 save(H/'voice-plan.json',plan);print('Prepared41 continuous scenes,250 original paragraphs,106 planned observation seams; no model/audio job launched.')
if __name__=='__main__':main()
