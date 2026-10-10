"""Prepare read-only source viewing on the existing loopback helper; no encode."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

root = Path(__file__).resolve().parents[3]
raw = root / 'shared/assets/presenting-game-scores/raw'
batch = root / 'production/batches/unpublished-teaching-clarity-revision'
record_path = batch / 'motion-native-reading-preparation-v1.json'
assert not record_path.exists(), 'Read actual follow-up; preserve this preparation'
sources = [
    ('PF5L_2g9UVQ', 'd2fff989d106762f66971c6e85172f79ce0bb6782c75f318d348447e11161612'),
    ('6slinvkF0Rs', 'fbed04f31a31326bb80eb175bb8893be11d0227b0f5651c4acff8822d299067f'),
]
records = []
for source_id, expected in sources:
    source = root / f'shared/assets/game-footage/motion-sickness-games/{source_id}.mp4'
    digest = hashlib.file_digest(source.open('rb'), 'sha256').hexdigest()
    assert digest == expected
    link = raw / f'motion-source-{source_id}-native-v1.mp4'
    if link.exists():
        assert os.path.samefile(source, link)
    else:
        os.link(source, link)
    records.append({'sourceId': source_id, 'source': source.relative_to(root).as_posix(),
                    'sameFileLink': link.relative_to(root).as_posix(), 'sha256': digest,
                    'bytes': source.stat().st_size, 'sameInode': os.path.samefile(source, link)})

windows = [
    ('전체 시야와 노즐 / view and nozzle', 'PF5L_2g9UVQ', 48, 69),
    ('Independent aim against posts', 'PF5L_2g9UVQ', 99, 118),
    ('Aim then edge turn', 'PF5L_2g9UVQ', 132, 169),
    ('Water, dirt and task result', 'PF5L_2g9UVQ', 187, 227),
    ('Reposition and refacing', 'PF5L_2g9UVQ', 268, 309.8),
    ('Upper then lower surfaces', 'PF5L_2g9UVQ', 310, 357.8),
    ('Overhead target', 'PF5L_2g9UVQ', 247.5, 267),
    ('Lower target and next face', 'PF5L_2g9UVQ', 359, 383),
    ('Slide target and task', 'PF5L_2g9UVQ', 408, 460),
    ('Same tower from other positions', 'PF5L_2g9UVQ', 465, 552.4),
    ('Talos trailer: separate puzzle shots', '6slinvkF0Rs', 15.8, 52.4),
]
window_data = [{'label': label, 'sourceId': sid, 'inSeconds': start, 'outSeconds': end}
               for label, sid, start, end in windows]
html = '''<!doctype html><html lang="ko"><meta charset="utf-8"><title>Motion source reading · preserved native footage</title>
<style>body{background:#111;color:#eee;font:16px system-ui;margin:16px}button{margin:4px;padding:8px}video{width:100%;max-height:76vh}p{margin:8px}#status{white-space:pre-wrap}</style>
<h1>게임 행동과 처음 보는 사람의 이해도 검토</h1><p>원본 1× / 음소거. 브라우저 시작·끝은 native PTS 컷 승인과 별개입니다. Talos는 서로 다른 예고편 쇼트입니다.</p>
<div id="buttons"></div><video id="source" controls muted playsinline preload="metadata"></video><p id="status">아직 재생하지 않았습니다.</p>
<script>
const windows=WINDOWS;
const video=document.getElementById('source'); const status=document.getElementById('status'); let selected=null; let started=null;
function describe(){status.textContent=JSON.stringify({window:selected,startedAt:started,time:video.currentTime,duration:video.duration,paused:video.paused,muted:video.muted,rate:video.playbackRate,browserEndpointsAreNotNativeCuts:true},null,2);}
video.addEventListener('timeupdate',()=>{if(selected&&video.currentTime>=selected.outSeconds)video.pause();describe();});
video.addEventListener('pause',describe);video.addEventListener('playing',describe);
for(const window of windows){let button=document.createElement('button');button.textContent=window.label+' '+window.inSeconds+'–'+window.outSeconds+'s';button.onclick=async()=>{video.pause();selected=window;started=null;const next='motion-source-'+window.sourceId+'-native-v1.mp4';if(video.getAttribute('src')!==next){video.src=next;await new Promise(resolve=>video.addEventListener('loadedmetadata',resolve,{once:true}));}video.muted=true;video.playbackRate=1;video.currentTime=window.inSeconds;await new Promise(resolve=>video.addEventListener('seeked',resolve,{once:true}));started=new Date().toISOString();await video.play();describe();};document.getElementById('buttons').append(button);}
</script></html>'''.replace('WINDOWS', json.dumps(window_data, ensure_ascii=False))
page = raw / 'motion-source-native-reading-v1.html'
assert not page.exists()
page.write_text(html, encoding='utf-8')
record = {'schemaVersion': 1, 'preparedAt': datetime.now(timezone.utc).isoformat(),
          'existingHelperPid': 27140, 'helperCreationObserved': '2026-10-09T10:34:26.837781+09:00',
          'sources': records, 'windows': window_data,
          'url': 'http://127.0.0.1:9250/motion-source-native-reading-v1.html',
          'newSourceBytesCopied': 0, 'encodeJobs': 0, 'decodeJobs': 0, 'newServers': 0,
          'sourceAdoptionApproved': False, 'normalSpeedUiPlaybackObserved': False,
          'allContinuousNativeFramesViewed': False, 'allFinalCuePixelsApproved': False,
          'baselineModified': False, 'nextHeavyProducerStarted': False, 'gitImagesAdded': 0}
record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'prepared': True, 'sameFileLinks': len(records), 'encodedMedia': 0, 'serverStarted': 0}))
