"""Single metadata read for the clearer official Timberborn developer stream."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
META=V/'source-research-v2'
META.mkdir(exist_ok=True)
sid='6TNjosDftog'
target=META/(sid+'.info.json')
assert not target.exists(), 'Do not reread completed stream metadata'
python=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
result=subprocess.run([str(python),'-X','utf8','-m','yt_dlp','--dump-single-json','--skip-download',
    '--no-playlist','--js-runtimes','node:'+node,'https://www.youtube.com/watch?v='+sid],
    cwd=ROOT,capture_output=True,text=True,encoding='utf8')
(META/(sid+'.metadata.log.txt')).write_text(result.stderr,'utf8')
assert result.returncode==0,result.stderr
info=json.loads(result.stdout)
target.write_text(result.stdout,'utf8')
assert info['id']==sid and info['channel']=='Timberborn'
source=dict(game='Timberborn',videoId=sid,expectedChannel='Timberborn',title=info['title'],
    channel=info['channel'],channelId=info.get('channel_id'),uploadDate=info.get('upload_date'),
    duration=info.get('duration'),chapters=info.get('chapters'),success=True,actualMetadataExitCode=0,
    previousShortSourceHeld='Jsc7003gSu0',actionSelectionApproved=False,sourceAudioForFinal=False)
(META/'metadata-observation-v1.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
    sources=[source],phase='new official stream metadata only; original three sources not repeated'),
    ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(source,ensure_ascii=False))
