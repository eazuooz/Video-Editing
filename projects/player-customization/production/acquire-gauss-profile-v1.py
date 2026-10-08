"""Acquire the CUA-verified official 2019 profile, then inspect native video only."""
import hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('D:/Github/Video-Editing')
LOCAL = ROOT / 'shared/output/player-customization/research/gauss-profile-v1'
STATE = ROOT / 'projects/player-customization/production/gauss-profile-execution-v1.json'
FFMPEG = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FFPROBE = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
URL = 'https://www.youtube.com/watch?v=gb9JKmJ5-6g'
if STATE.exists() or (LOCAL / 'gb9JKmJ5-6g.mp4').exists():
    raise SystemExit('Existing checkpoint: inspect rather than repeat acquisition.')
LOCAL.mkdir(parents=True, exist_ok=True)
now = lambda: datetime.now(timezone.utc).isoformat()
state = dict(schemaVersion=1, startedAt=now(), wrapperPid=os.getpid(),
    commandLine=[sys.executable, *sys.argv], status='running', cpuThreads=2, gpu=0,
    singleJob=True, sourceUrl=URL, officialOwner='PlayWarframe / @Warframe',
    sourceDate='2019-08-27', variant='Original Gauss; not Gauss Prime 2024 or the specific 2024 configuration.',
    observedPage='shared/output/player-customization/preflight/warframe-gauss-profile-details.txt',
    resourceEvidence='shared/output/player-customization/research/resources-before-gauss-v1.json',
    sourceAudioUsed=False, allMediaLocalOnly=True, operations=[],
    directPixelsReviewed=False, continuousActionsReviewed=False, footageQuotaApproved=False,
    finalPublicRightsApproved=False, narrationWritten=False, ttsStarted=False)
def save(): STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def run(name, command):
    op=dict(name=name, commandLine=command, startedAt=now())
    state['operations'].append(op); save()
    with (LOCAL/(name+'.log')).open('w',encoding='utf-8') as log:
        child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        op['pid']=child.pid; save(); code=child.wait()
    op.update(exitCode=code,finishedAt=now()); save()
    if code: raise RuntimeError(name+' failed; inspect local log')
save()
try:
    gate=subprocess.run(['node','scripts/review-video-duplicates.cjs','player-customization','--check'],cwd=ROOT)
    if gate.returncode: raise RuntimeError('Current duplicate gate changed')
    run('download',['D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe','-X','utf8','-m','yt_dlp',
        '--no-playlist','--write-info-json','--no-write-thumbnail','--no-overwrites',
        '--retries','2','--fragment-retries','2','--socket-timeout','30',
        '--js-runtimes','node:C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
        '--ffmpeg-location','C:/ProgramData/HP/LCDDisplayHelper/bin',
        '-f','bv[height<=1080][ext=mp4][vcodec^=avc]/bv[height<=1080][ext=mp4]/bv[height<=1080]',
        '--downloader-args','ffmpeg:-threads 2','-o',str(LOCAL/'gb9JKmJ5-6g.%(ext)s'),URL])
    source=LOCAL/'gb9JKmJ5-6g.mp4'
    state['sourceSha256']=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
    state['sourceBytes']=source.stat().st_size
    result=subprocess.run([FFPROBE,'-v','error','-show_streams','-show_format','-of','json',str(source)],capture_output=True,text=True,encoding='utf-8')
    if result.returncode: raise RuntimeError('native probe failed')
    (LOCAL/'probe.json').write_text(result.stdout,encoding='utf-8')
    probe=json.loads(result.stdout)
    if any(s['codec_type']=='audio' for s in probe['streams']): raise RuntimeError('Unexpected source audio')
    state['nativeProbe']=[{k:s.get(k) for k in ['codec_type','codec_name','width','height','r_frame_rate','time_base','duration','nb_frames']} for s in probe['streams']]
    save()
    run('whole-decode',[FFMPEG,'-nostdin','-v','error','-threads','2','-i',str(source),'-an','-f','null','-'])
    native=LOCAL/'native'; native.mkdir(exist_ok=True)
    run('sample-2sec',[FFMPEG,'-nostdin','-v','error','-threads','2','-i',str(source),'-vf','fps=1/2',
        '-fps_mode','vfr','-an','-threads','2',str(native/'frame-%03d.png')])
    boards=LOCAL/'boards'; boards.mkdir(exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
    samples=sorted(native.glob('*.png'))
    boardRows=[]
    for first in range(0,len(samples),4):
        board=Image.new('RGB',(1920,1170),'white'); draw=ImageDraw.Draw(board)
        entries=[]
        for j,path in enumerate(samples[first:first+4]):
            image=Image.open(path).convert('RGB'); image.thumbnail((960,540))
            x=(j%2)*960; y=(j//2)*585
            board.paste(image,(x,y+45)); index=int(path.stem.split('-')[-1]); t=(index-1)*2
            draw.text((x+12,y+8),f'{path.name} | nominal {t}s | native sample, not exact boundary',font=font,fill='black')
            entries.append(dict(path=str(path.relative_to(ROOT)),nominalSeconds=t))
        path=boards/f'board-{len(boardRows)+1:02d}.png'; board.save(path)
        boardRows.append(dict(path=str(path.relative_to(ROOT)),entries=entries))
    state.update(status='native-decoded-samples-ready-direct-review-pending',finishedAt=now(),exitCode=0,
        nativeSampleCount=len(samples),boardCount=len(boardRows),boards=boardRows,
        next='Directly read every board, continuous action and logo/caption-safe crop; no quota approval from samples alone.')
    save(); print(json.dumps({k:state[k] for k in ['status','wrapperPid','sourceSha256','nativeSampleCount','boardCount','exitCode']},ensure_ascii=False),flush=True)
except Exception as error:
    state.update(status='failed',finishedAt=now(),exitCode=1,error=str(error));save();raise
