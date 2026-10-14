"""Preserve failed takes, then allow a bounded retry of only the same guide."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(R).as_posix()
e=read(P/'part1-complete-close-tts-execution-v284.json');assert e['exitCode']==1 and e['results'][0]['technicalTailGatePassed']==False
w=e['actualIdentity'];assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
mp=P/'part1-complete-close-retry-tts-manifest-v285.json';base=read(P/'part1-complete-close-tts-manifest-v284.json')
out='shared/output/narration/game-lighting-history-04/qwen3-1.7b-part1-complete-close-retry-v285';stem='game-lighting-history-04-part1-complete-close-retry-v285'
base['paths'].update(narration=f'{out}/{stem}.wav',captionsKo=f'{out}/{stem}.srt',captionsEn=f'{out}/{stem}.en.srt')
base['tts'].update(outputDir=out,filenameStem=stem,maxRenderAttempts=8,maxNewTokensReason='Bounded identical-text single-guide retry after all three actual v284 terminal checks failed. Archive every attempted PCM locally; established tail criteria unchanged.')
assert not mp.exists();mp.write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n','utf-8')
request=read(P/'part1-complete-close-tts-request-v284.json');request.update(preparedAt=datetime.now(timezone.utc).isoformat(),manifestOverride=rel(mp),reason='Actual v284 three attempts failed tail criteria; reuse exactly its two-sentence KO/EN meaning. Maximum8 attempts in one exclusive batch; archive each unapproved attempt. No original PCM regenerated.',scenes=[{'id':'outer-comparison-before','path':f'{out}/chunks/outer-comparison-before-scene.wav'}])
request['protectedInputs'] += [{'path':rel(p),'sha256':sha(p)} for p in [P/'part1-complete-close-tts-execution-v284.json',R/e['results'][0]['path'],mp]]
rp=P/'part1-complete-close-retry-tts-request-v285.json';assert not rp.exists();rp.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf-8')
code=(R/'production/research/game-lighting-history/render-part1-complete-close-v284.py').read_text('utf-8-sig').replace('part1-complete-close-tts-request-v284','part1-complete-close-retry-tts-request-v285').replace('part1-complete-close-tts-execution-v284','part1-complete-close-retry-tts-execution-v285').replace('episode04Part1CompleteCloseTtsV284','episode04Part1CompleteCloseRetryTtsV285').replace('.tts284.tmp','.tts285.tmp')
needle=" Qwen3TTSModel.from_pretrained=classmethod(load)"
archive="""
 generate_original=Qwen3TTSModel.generate_voice_clone
 attempt_counter=[0]
 def generate_archived(self,*args,**kwargs):
  wavs,sr=generate_original(self,*args,**kwargs)
  folder=ROOT/'"""+out+"""/attempts';folder.mkdir(parents=True,exist_ok=True)
  for wav in wavs:
   attempt_counter[0]+=1;dest=folder/f'attempt-{attempt_counter[0]:02d}.wav'
   if dest.exists():raise RuntimeError('Preserve prior attempt archive')
   sf.write(dest,wav,sr,subtype='PCM_16')
  return wavs,sr
 Qwen3TTSModel.generate_voice_clone=generate_archived
"""
assert code.count(needle)==1;code=code.replace(needle,needle+archive)
p=R/'production/research/game-lighting-history/render-part1-complete-close-retry-v285.py';assert not p.exists();p.write_text(code,'utf-8')
print(json.dumps({'sameText':True,'maxAttempts':8,'archiveEveryAttempt':True,'qualityGateUnchanged':True,'priorSession85707Closed':True}))
