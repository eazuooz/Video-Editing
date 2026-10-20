"""Convert our own browser screencasts to 1920x1080/60fps H.264 sources and
record the inventory (url, hash, duration, disclosure observations)."""
from pathlib import Path
import json, hashlib, subprocess, datetime
R = Path(__file__).resolve().parents[3]; P = R / 'projects/steam-next-fest-ai-flood'
REC = P / 'production/local/recordings'; OUT = P / 'sources/recordings.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def probe(p):
    v = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,nb_frames:format=duration', '-of', 'json', str(p)]))
    s = v['streams'][0]; return {'width': s['width'], 'height': s['height'], 'fps': s['r_frame_rate'], 'frames': int(s.get('nb_frames') or 0), 'duration': float(v['format']['duration'])}
existing = json.loads(OUT.read_text(encoding='utf8')) if OUT.exists() else {'recordings': {}}
inv = existing['recordings']
for webm in sorted(REC.glob('*.webm')):
    meta_path = webm.with_suffix('.json')
    if not meta_path.exists(): continue
    meta = json.loads(meta_path.read_text(encoding='utf8'))
    mp4 = webm.with_suffix('.mp4'); src_sha = sha(webm)
    rec = inv.get(webm.stem, {})
    if not (mp4.exists() and rec.get('webmSha256') == src_sha):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(webm), '-vf', 'fps=60,setsar=1', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-video_track_timescale', '60000', str(mp4)], check=True)
    info = probe(mp4); assert (info['width'], info['height'], info['fps']) == (1920, 1080, '60/1'), info
    inv[webm.stem] = {'file': mp4.relative_to(R).as_posix(), 'webmSha256': src_sha, 'sha256': sha(mp4), **info,
                      'url': meta.get('url'), 'urlAfterLoad': meta.get('urlAfterLoad'), 'pickedFromSearch': meta.get('pickedFromSearch'),
                      'extension': meta.get('extension'), 'pageTitle': meta.get('pageTitle'), 'recordedAt': meta.get('startedAt'),
                      'disclosureOnPage': meta.get('disclosureOnPage'), 'tiles': meta.get('tiles'), 'disclosedCount': meta.get('disclosedCount'),
                      'role': 'own-browser-recording', 'rights': 'Our own screen recording of public web pages; platform UI and third-party marks preserved; no gameplay footage'}
    print(webm.stem, info['duration'], 's')
OUT.write_text(json.dumps({'updatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'recorder': 'projects/steam-next-fest-ai-flood/production/record-browser.cjs', 'extension': 'AI warning for Steam 1.1.2 (seeeeew, MIT) loaded from source', 'recordings': inv}, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print('inventory', len(inv))
