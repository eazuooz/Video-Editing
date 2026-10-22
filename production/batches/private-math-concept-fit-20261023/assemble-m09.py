"""Produce the local clean/captioned pair and matching plain KO/EN SRT."""
from common import *
import shutil,html
import runpy
ENC=runpy.run_path(str(B/'compose-m09.py'))['ENC']
P=R/'projects/game-math-lines-circles-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';D=R/'output/game-math-lines-circles-v2-concept-fit-v2';D.mkdir(exist_ok=True)
T=read(H/'timeline.json');comp=read(H/'composition.json');authorized('M09');assert comp['completed']
base=R/'projects/game-math-lines-circles-v2/production/local/private-polish-v1/clips'
order=[dict(path=rel(base/'intro.mp4'),frames=120)]+comp['scenes']+[dict(path=rel(base/'outro.mp4'),frames=600)]
for r in order:
 path=R/r['path'];v=next(s for s in probe(path)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==r['frames'] and v['r_frame_rate']=='60/1';assert sha(path)==r.get('sha256',sha(path))
listing=O/'concat-concept-fit.txt';listing.write_text('\n'.join("file '"+(R/x['path']).as_posix()+"'" for x in order)+'\n',encoding='utf8')
mix=read(H/'audio-mix.json');assert sha(R/mix['path'])==mix['sha256']
def ff(args,log):
 with (O/log).open('w',encoding='utf8') as f:subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y',*map(str,args)],cwd=O,stdout=f,stderr=f,check=True)
repairs=runpy.run_path(str(B/'preserve-math-overlays.py'))['prepare'](P.name)
graph='[0:v]settb=expr=1/60,setpts=N,setsar=1,'+(repairs+',' if repairs else '')+'split=2[vclean][vin];[vin]ass=captions.ko.ass[vcaptioned]'
args=['-reinit_filter','0','-f','concat','-safe','0','-i',listing,'-filter_complex_threads','2','-filter_complex',graph]
slug='game-math-lines-circles-v2'
for kind in ['clean','captioned']:args+=['-map',f'[v{kind}]','-frames:v',T['frames'],'-an',*ENC,O/f'{kind}-video-only.mp4']
print('Encode complete clean/captioned pair',flush=True);ff(args,'final-pair.log')
for kind in ['clean','captioned']:
 authorized('M09');ff(['-i',O/f'{kind}-video-only.mp4','-i',R/mix['path'],'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',D/f'{slug}.{kind}.mp4'],f'final-mux-{kind}.log')
for lang in ['ko','en']:shutil.copy2(O/f'captions.{lang}.srt',D/f'{slug}.{lang}.srt')
outputs=[dict(path=rel(p),sha256=sha(p),bytes=p.stat().st_size) for p in [D/f'{slug}.{ext}' for ext in ['clean.mp4','captioned.mp4','ko.srt','en.srt']]]
save(H/'outputs.json',dict(outputs=outputs,frames=T['frames'],seconds=T['seconds'],status='encoded-internal-qa-pending',humanReview='pending',actualWholeListening=False,uploadAuthorized=False))
(D/'index.html').write_text(f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>직선과 경계 ① 두 점으로 연결선을 계산하기 · 수정본</title><style>body{{max-width:1200px;margin:30px auto;padding:0 20px;background:#101512;color:#f3f5f3;font:18px/1.6 system-ui}}h1{{color:#ffdf73}}a{{color:#8cdbbc}}video{{width:100%}}nav{{display:flex;gap:20px;flex-wrap:wrap}}</style><h1>직선과 경계 ① 두 점으로 연결선을 계산하기</h1><p>기존 강의의 수학 설명과 순서는 보존하고, 그래플의 두 끝점·배선과 계산용 선분 비교로 게임 예시를 수정했습니다. 1080p60 · {T["seconds"]/60:.1f}분.</p><p>내부 검수 진행 중 · 최종 사용자 시청/청취 대기</p><video controls preload="metadata" src="{slug}.captioned.mp4"></video><nav><a href="{slug}.captioned.mp4">전체 자막 영상</a><a href="{slug}.clean.mp4">무자막 영상</a><a href="{slug}.ko.srt">한국어 자막</a><a href="{slug}.en.srt">영어 자막</a></nav><p><a href="../private-game-math-polish/index.html">전체 진행표</a></p></html>''',encoding='utf8')
print('Four outputs encoded; internal QA pending',flush=True)
