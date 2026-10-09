"""Prepare a serial CPU2 native-input builder; actual execution requires voice approval."""
from pathlib import Path
P=Path(__file__).parent
t=(P/'build-measured-native-inputs-v8.py').read_text('utf-8')
t=t.replace("pp=BASE/'measured-timeline-candidate-v7.json'","pp=BASE/'revision-balatro60-v2/measured-editorial-candidate-v3.json'")
t=t.replace("vp=ROOT/plan['currentVoiceSelection'];v=read(vp)","vp=ROOT/plan['voiceSelection'];v=read(vp)")
t=t.replace("plan['currentVoiceSelectionSha256'] and v['currentVoiceApproved']","plan['voiceSelectionSha256'] and v['currentCompleteVoiceApproved']")
t=t.replace("assert len(rows)==12 and sum(s['frames'] for s in rows)==10999","assert len(rows)==18 and sum(s['frames'] for s in rows)==plan['actualFrames']\nassert plan['finalPlanAdopted'] and plan['currentCompleteVoiceApproved']")
t=t.replace('shared/output/presenting-game-scores/measured-native-inputs-v8','shared/output/presenting-game-scores/revision-balatro60-v2/measured-native-inputs-v1')
t=t.replace("EP=BASE/'measured-native-inputs-execution-v8.json'","EP=BASE/'revision-balatro60-v2/measured-native-inputs-execution-v1.json'")
t=t.replace("'projects/presenting-game-scores/production/native-end-duration-failure-review-v8.json'","'Preserved baseline v8 files; new approved source/timing only'")
t=t.replace("    for s in rows:\n        dest=", "    old=read(BASE/'measured-native-inputs-execution-v8.json');assert old['exitCode']==0\n    for s in rows:\n        reuse=next((x for x in old['results'] if x['sourceSha256']==s['sourceSha256'] and x['sourceStartFrame']==s['sourceStartFrame'] and x['sourceEndFrameExclusive']==s['sourceEndFrameExclusive'] and x['frames']==s['frames'] and x['framing']==s['framing']),None)\n        if reuse:\n            assert sha(ROOT/reuse['path'])==reuse['sha256'] and reuse['allPtsVerified'] and reuse['wholeDecodeExitCode']==0\n            result={**reuse,'id':s['id'],'reusedUnchangedVerifiedBaselineInput':True,'baselineExecution':'projects/presenting-game-scores/production/measured-native-inputs-execution-v8.json','encodeRepeated':False,'decodeRepeated':False,'finalCuePixelsReviewed':False}\n            state['results'].append(result);state['completed']+=1;save(EP,state);queue(state)\n            print('Reused unchanged verified input '+s['id'],flush=True);continue\n        dest=")
t=t.replace("        if shift:\n", "        if s['source']=='balatro-longplay':\n            filters=f'[0:v]{trim},split=2[b][f];[b]scale=1920:1080,gblur=sigma=28:steps=2,eq=brightness=-0.3[bg];[f]scale=1600:900[fg];[bg][fg]overlay=160:0:shortest=1[fit];[fit]drawbox=x=8:y=308:w=144:h=170:color=black@0.92:t=fill[creditbg];'\n            prior='creditbg'\n            for i,line in enumerate(['Footage:','Squeaky','Whale','Gameplay','Archive']):\n                label='credit'+str(i);filters+=f'[{prior}]drawtext=fontfile=C\\\\:/Windows/Fonts/segoeuib.ttf:text={line}:fontcolor=white:fontsize=22:x=12:y={320+i*29}[{label}];';prior=label\n            filters+=f'[{prior}]null[framed];'\n        elif shift:\n")
# Recompute credit from actual render pixels later; do not inherit old pixel approvals.
t=t.replace("newRasterGitAdditions=0,sourceAudio=False", "preparedWorkerVersion='revision-native-v1',newRasterGitAdditions=0,sourceAudio=False")
t=t.replace("if x['slug']=='presenting-game-scores')", "if x['slug']=='presenting-game-scores')")
t=t.replace("status='building-measured-native-inputs-v8'","status='building-Balatro60-revision-native-inputs-v1'")
dst=P/'build-revision-native-inputs-v1.py';assert not dst.exists();dst.write_text(t,'utf-8')
import py_compile;py_compile.compile(str(dst),doraise=True)
print('Prepared-only native worker; all source/voice/adoption/resource gates required. Encodes0/models0.')
