"""Full-resolution local pair with the complete recovered audio bitstream."""
import sys,shutil,html
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();e.D.mkdir(parents=True,exist_ok=True)
staging=e.O/'assembly-staging';staging.mkdir(exist_ok=True)
order=[('intro',120)]+[(s['id'],s['frames']) for s in e.T['scenes']]+[('outro',600)];assert sum(n for _,n in order)==e.T['frames']
records=[]
repair=read(e.H/'composition-polish.json') if (e.H/'composition-polish.json').exists() else None
if repair:
 assert repair['timelineSha256']==sha(e.P/'production/timeline.json')
 assert sha(R/repair['globalAss'])==repair['globalAssSha256']
for sid,n in order:
 replacement=repair['inputs'].get(sid) if repair else None
 path=R/replacement['path'] if replacement else e.O/f'clips/{sid}.mp4'
 if replacement:assert sha(path)==replacement['sha256']
 e.verify(path,n);records.append({'id':sid,'path':rel(path),'sha256':sha(path),'frames':n})
listing=e.O/'concat.txt';listing.write_text('\n'.join("file '"+(R/x['path']).as_posix()+"'" for x in records)+'\n',encoding='utf8')
audio=e.O/'baseline-audio.m4a';assert sha(audio)==read(e.H/'restoration.json')['audioSha256']
save(e.H/'assembly.json',{'timelineSha256':sha(e.P/'production/timeline.json'),'scenes':records,'audioSha256':sha(audio),'captionSha256':sha(e.O/'captions.ko.ass'),'compositionPolish':repair,'directVisualReview':'pending'})
graph='[0:v]settb=expr=1/60,setpts=N,setsar=1,split=2[vclean][vin];[vin]ass=captions.ko.ass[vcaptioned]'
if repair:graph=graph.replace('setsar=1,split','setsar=1,ass=composition-polish.ass,split')
args=['-reinit_filter','0','-f','concat','-safe','0','-i',listing,'-filter_complex',graph]
for kind in ['clean','captioned']:
 args+=['-map',f'[v{kind}]','-frames:v',e.T['frames'],'-an',*ENC,'-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',staging/f'{e.slug}.{kind}.video-only.mp4']
e.ff(args,'full-pair.log',e.O)
# Audio is added after frame-limited encoding, preserving its final AAC packet.
for kind in ['clean','captioned']:
 e.authorized();silent=staging/f'{e.slug}.{kind}.video-only.mp4';dst=e.D/f'{e.slug}.{kind}.mp4'
 e.ff(['-i',silent,'-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',dst],f'full-audio-{kind}.log');e.verify(dst,e.T['frames'])
for lang in ['ko','en']:shutil.copy2(e.O/f'captions.{lang}.srt',e.D/f'{e.slug}.{lang}.srt')
outputs=[{'path':rel(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [e.D/f'{e.slug}.{k}' for k in ['clean.mp4','captioned.mp4','ko.srt','en.srt']]]
save(e.H/'outputs.json',{'outputs':outputs,'frames':e.T['frames'],'seconds':e.T['seconds'],'technicalQa':'pending','humanReview':'pending','uploadAuthorized':False})
title=html.escape(e.entry['title']);name=e.slug
(e.D/'index.html').write_text(f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} · 검수</title>
<style>body{{max-width:1100px;margin:36px auto;padding:0 20px;background:#121915;color:#f6f8f6;font:18px/1.65 system-ui}}h1{{color:#ffdf73;font-size:30px}}a{{color:#8cdbbc}}video{{width:100%;background:black}}nav{{display:flex;gap:20px;flex-wrap:wrap;margin:20px 0}}small{{color:#becbc2}}</style>
<h1>{title}</h1><p>기존 대본·음성·장면 순서를 유지한 시각 보강본입니다. 내부 검사 상태는 작업표에서 확인할 수 있습니다.</p><video controls preload="metadata" src="{name}.captioned.mp4"></video>
<nav><a href="{name}.captioned.mp4">전체 자막 영상</a><a href="{name}.clean.mp4">무자막 영상</a><a href="{name}.ko.srt">한국어 자막</a><a href="{name}.en.srt">영어 자막</a></nav>
<p><a href="../private-game-math-polish/index.html">전체 진행표</a></p><small>1920×1080 · 60fps. 기존 업로드에서 압축 음성을 복구하여 재인코딩 없이 유지했습니다. 원본 PCM과 동일하다는 뜻은 아닙니다. 기존 업로드는 보존했습니다.</small></html>''',encoding='utf8')
print(e.id,'four outputs encoded; internal QA and human review pending',flush=True)
