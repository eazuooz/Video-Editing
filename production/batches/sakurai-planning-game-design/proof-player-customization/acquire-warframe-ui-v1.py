"""Acquire one already-observed official UI chapter; no audio or narration production."""
import json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path('D:/Github/Video-Editing')
LOCAL=ROOT/'shared/output/player-customization/research/game-sources'
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-player-customization'
LOCAL.mkdir(parents=True,exist_ok=True)
statepath=PROOF/'official-source-acquisition-v1.json'
url='https://www.youtube.com/watch?v=ovxaYxLbUNE'
out=LOCAL/'ovxaYxLbUNE-ui-qol-3900-4980.mp4'
if out.exists() or statepath.exists(): raise SystemExit('Existing acquisition checkpoint: inspect it instead of repeating this job.')
gate=subprocess.run(['node','scripts/review-video-duplicates.cjs','player-customization','--check'],cwd=ROOT)
if gate.returncode: raise SystemExit(gate.returncode)
cmd=['D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe','-X','utf8','-m','yt_dlp',
 '--no-playlist','--write-info-json','--no-write-thumbnail','--no-overwrites',
 '--retries','2','--fragment-retries','2','--socket-timeout','30',
 '--js-runtimes','node:C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
 '--ffmpeg-location','C:/ProgramData/HP/LCDDisplayHelper/bin',
 '-f','bv[height<=1080][ext=mp4][vcodec^=avc]/bv[height<=1080][ext=mp4]/bv[height<=1080]',
 '--download-sections','*01:05:00-01:23:00','--downloader-args','ffmpeg:-threads 2',
 '-o',str(LOCAL/'ovxaYxLbUNE-ui-qol-3900-4980.%(ext)s'),url]
now=lambda:datetime.now(timezone.utc).isoformat()
state={'schemaVersion':1,'startedAt':now(),'wrapperPid':os.getpid(),'wrapperCommandLine':[sys.executable,*sys.argv],
 'sourceUrl':url,'officialOwner':'PlayWarframe / @Warframe','discoveredAt':'Official Devstream180 article embeds this exact YouTube video; current CUA verified owner/title and description chapter times.',
 'requestedSourceRangeSeconds':[3900,4980],'status':'running','commandLine':cmd,'threadsTarget':2,'gpu':0,
 'videoOnly':True,'sourceAudioUsed':False,'rawFilesLocalOnly':True,'rightsStatus':'conditional-policy-reviewed; required beginning notice and no-endorsement/no-third-party-art conditions not yet implemented or approved',
 'nativePixelsApproved':False,'narrationWritten':False,'footageQuotaApproved':False,'finalUploaded':False}
def save(): statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save()
with (LOCAL/'download.log').open('w',encoding='utf-8') as log:
 child=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 state['downloadPid']=child.pid;save()
 print(json.dumps({'wrapperPid':os.getpid(),'downloadPid':child.pid,'state':str(statepath)},ensure_ascii=False),flush=True)
 code=child.wait()
state.update({'downloadExitCode':code,'finishedAt':now(),'status':'download-finished-native-probe-and-review-pending' if code==0 else 'download-failed'})
state['downloadedFiles']=[{'path':str(p),'bytes':p.stat().st_size} for p in LOCAL.iterdir() if p.is_file() and p.suffix.lower() in ['.mp4','.webm']]
save()
print(json.dumps({'exitCode':code,'status':state['status'],'files':state['downloadedFiles']},ensure_ascii=False),flush=True)
raise SystemExit(code)
