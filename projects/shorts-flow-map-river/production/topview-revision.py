"""V3: observed overhead gameplay first, followed by the intact Unity explanation.

No TTS, GPU scene rendering, platform mutation, or overwrite of earlier masters.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
L = P / 'production/local/topview-v3'
O = P / 'production/local/final-topview-v3'
BASE = P / 'production/local/final-reviewed'
A = P / 'production/local/audio'
SOURCE = L / 'zelda-river.mp4'
REV = 'flow-map-topview-v3'
N, CUT, SOURCE_IN = 3067, 264, 253.5

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p, value): Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).relative_to(R).as_posix()
def run(args):
    result = subprocess.run(args, cwd=R, capture_output=True)
    if result.returncode: raise RuntimeError(result.stderr.decode(errors='replace')[-4000:])
    return result.stdout

def guard():
    control = read(R / 'shared/publishing/video-production-control.json')
    cp = read(P / 'production/checkpoint.json')
    assert control['selectedShortVideo'] == P.name and not control['automaticNextVideoEnabled']
    assert cp['revision'] == REV and cp['revisionAuthorization']['id'] == REV
    assert sha(BASE / 'captioned.mp4') == cp['baselineV1']['finalMaster']['sha256']
    assert sha(P / cp['baselineV2']['masterPath'].split(P.name + '/')[1]) == cp['baselineV2']['masterSha256']

def build():
    guard(); O.mkdir(exist_ok=True)
    assert not (O / 'clean.mp4').exists() and not (O / 'captioned.mp4').exists()
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(SOURCE)]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    assert (video['width'], video['height'], video['r_frame_rate']) == (1920, 1080, '60/1')
    header = (P / 'production/header.ass').read_text(encoding='utf-8')
    header = '\n'.join(s for s in header.splitlines() if '우리 Unity 구현' not in s) + '\n'
    header += r'Dialogue: 0,0:00:00.00,0:00:04.40,Header,,0,0,0,,{\pos(840,480)\fs34\b0\c&H00BCC3B8&}실제 게임 화면' + '\n'
    header += r'Dialogue: 0,0:00:04.40,0:00:51.12,Header,,0,0,0,,{\pos(840,480)\fs34\b0\c&H00BCC3B8&}우리 Unity 구현' + '\n'
    (O / 'fixed-header.ass').write_text(header, encoding='utf-8')
    labels = header.split('[Events]')[0] + '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    labels += r'Dialogue: 0,0:00:00.00,0:00:04.40,Header,,0,0,0,,{\pos(520,562)\fs36\c&H005AD2FF&}젤다의 전설: 지혜의 투영' + '\n'
    # Observed stone between two water channels. This is an editorial outline,
    # following camera translation for its short reveal, never a velocity measure.
    labels += r'Dialogue: 1,0:00:00.10,0:00:00.70,Header,,0,0,0,,{\an7\move(440,986,208,1026)\p1\bord6\shad0\1a&HFF&\3c&H00CDD773&\fad(100,100)}m -59 -27 b -78 -6 -77 34 -52 54 b -24 75 23 68 45 42 b 65 17 58 -20 33 -34{\p0}' + '\n'
    labels += r'Dialogue: 2,0:00:00.10,0:00:00.70,Header,,0,0,0,,{\move(440,922,208,962)\fs33\bord3\shad0\c&H00CDD773&\fad(100,100)}바위' + '\n'
    (O / 'game-labels.ass').write_text(labels, encoding='utf-8')
    # 1248x840 is a contextual crop of the native FHD capture. Uniform 5/6
    # scaling enlarges the water within the portrait layout without stretching.
    # Only nonessential combat/minimap UI at the outer edges is cropped.
    filt = [
        '[1:v]trim=duration=4.4,setpts=PTS-STARTPTS,fps=60,crop=1248:840:360:160,scale=1040:700:flags=lanczos,setsar=1[game]',
        "[0:v]drawbox=x=0:y=420:w=1080:h=900:color=black:t=fill:enable='lt(t,4.4)'[base]",
        "[base][game]overlay=20:600:eof_action=pass:enable='lt(t,4.4)'[insert]",
        '[insert]drawbox=x=0:y=0:w=1080:h=540:color=black:t=fill,ass=' + rel(O / 'fixed-header.ass') + ',ass=' + rel(O / 'game-labels.ass') + '[v]',
    ]
    (O / 'composition.ffmpeg').write_text(';\n'.join(filt), encoding='utf-8')
    run(['ffmpeg', '-v', 'error', '-n', '-filter_complex_threads', '3', '-i', str(BASE / 'clean.mp4'),
         '-ss', str(SOURCE_IN), '-t', str(CUT / 60), '-i', str(SOURCE), '-/filter_complex', str(O / 'composition.ffmpeg'),
         '-map', '[v]', '-map', '0:a:0', '-frames:v', str(N), '-t', str(N / 60), '-c:v', 'libx264', '-threads', '4',
         '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', str(O / 'clean.mp4')])
    run(['ffmpeg', '-v', 'error', '-n', '-i', str(O / 'clean.mp4'), '-vf', 'ass=' + rel(A / 'captions.ko.ass'),
         '-c:v', 'libx264', '-threads', '4', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
         '-movflags', '+faststart', str(O / 'captioned.mp4')])
    run(['ffmpeg', '-v', 'error', '-n', '-i', str(O / 'clean.mp4'), '-vn', '-c:a', 'copy', str(O / 'final-mix.m4a')])
    audio_hashes = {}
    for name, file in [('baseline', BASE / 'clean.mp4'), ('clean', O / 'clean.mp4'), ('captioned', O / 'captioned.mp4')]:
        raw = run(['ffmpeg', '-v', 'error', '-i', str(file), '-vn', '-f', 'f32le', '-acodec', 'pcm_f32le', 'pipe:1'])
        audio_hashes[name] = hashlib.sha256(raw).hexdigest()
    assert len(set(audio_hashes.values())) == 1, 'Voice and BGM must remain sample-identical.'
    save(O / 'build.json', dict(revision=REV, createdAt=datetime.now(timezone.utc).isoformat(), frames=N, duration=N / 60,
         source=rel(SOURCE), sourceSha256=sha(SOURCE), sourceProbe=probe, sourceIn=SOURCE_IN, sourceOut=SOURCE_IN+CUT/60,
         gameplayFrames=[0, CUT], crop=[360,160,1248,840], placement=[20,600,1040,700], speed=1,
         sourceAudio='Excluded inseparable third-party commentary; verified baseline narration+BGM retained exactly.',
         baselineSha256=sha(BASE / 'captioned.mp4'), voiceSha256=sha(A / 'voice/flow-map.wav'), audioPcmHashes=audio_hashes,
         narrationChanged=False, captionsChanged=False, cleanSha256=sha(O / 'clean.mp4'), captionedSha256=sha(O / 'captioned.mp4')))

def qa():
    guard(); reports=[]
    for name in ['clean', 'captioned']:
        f=O/(name+'.mp4');run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'])
        info=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(f)]))
        v=next(s for s in info['streams'] if s['codec_type']=='video')
        assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames'])) == (1080,1920,'60/1',N)
        reports.append(dict(path=rel(f),sha256=sha(f),probe=info,decodePass=True))
    q=O/'qa';q.mkdir(exist_ok=True)
    times=[0,.2,.5,.68,.8,1.5,2.5,3.5,4.38,4.4,4.6,6,15.5,25.7,37,49.5]
    for i,t in enumerate(times):
        f=q/f'{i:02}.jpg'
        if not f.exists():run(['ffmpeg','-v','error','-n','-ss',str(t),'-i',str(O/'captioned.mp4'),'-frames:v','1','-q:v','2',str(f)])
    for start in range(0,len(times),8):
        sheet=Image.new('RGB',(1500,1400),'#222222');d=ImageDraw.Draw(sheet)
        for k,t in enumerate(times[start:start+8]):
            im=Image.open(q/f'{start+k:02}.jpg');im.thumbnail((375,667));x=k%4*375;y=k//4*700
            sheet.paste(im,(x,y));d.text((x+10,y+672),str(t),fill='white')
        sheet.save(q/f'sheet{start//8}.jpg')
    save(O/'integrity.json',dict(status='pass',outputs=reports,checkedFrames=times,humanReview='not-claimed'))
    (O/'playback.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>플로 맵 · 탑뷰 도입 수정본</title><style>body{background:#171b19;color:white;font:16px sans-serif;margin:20px}video{width:375px;max-width:100%}button{padding:10px;margin:6px}</style><h2>플로 맵 · 탑뷰 도입 수정본</h2><p>1080×1920 · 60fps · 51초</p><button onclick="v.currentTime=0;v.play()">첫 장면부터</button><button onclick="v.currentTime=3;v.play()">시연 연결</button><button onclick="v.style.width='810px'">큰 화면</button><button onclick="v.style.width='375px'">모바일 크기</button><br><video id="v" src="captioned.mp4" controls preload="auto"></video></html>''',encoding='utf-8')

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['build','qa']);args=parser.parse_args();globals()[args.command]()
