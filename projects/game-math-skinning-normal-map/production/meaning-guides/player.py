"""Portable review page for M22. Only the approved lecture's encoded files are linked."""
from html import escape
from pathlib import Path
import json

CHAPTERS = [(0,'마리오의 착지에서 표면까지'),(2,'라이더의 무릎과 골격'),
 (4,'팔꿈치가 굽으면 소매의 점은 어디로 갈까?'),(10,'단추로 보는 기준 자세와 현재 자세'),
 (13,'비틀 때 소매가 가늘어지는 이유'),(15,'둠 3의 손전등과 표면 요철'),
 (19,'표면에 붙은 세 축 T · B · N'),(20,'빨강 채널과 법선 방향'),
 (25,'모델의 변과 UV 삼각형'),(28,'두 공간에서 같은 이동 따라가기'),
 (32,'법선에 수직인 접선 만들기'),(35,'한 캐릭터에 두 기법 연결하기')]

def review_page(dest,queue):
 slug=queue['project'];scenes=json.loads(Path(queue['wordAlignment']).read_text('utf-8-sig'))['scenes']
 links=[]
 for ix,label in CHAPTERS:
  sec=(120+scenes[ix]['startFrame'])/60
  links.append(f'<a data-t="{sec:.3f}" href="#t={sec:.3f}"><time>{int(sec)//60}:{int(sec)%60:02d}</time> {escape(label)}</a>')
 duration=(720+queue['bodyFrames'])/60
 page=r"""<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>스키닝과 노멀 맵 · 게임수학 M22</title><style>
:root{color-scheme:dark}body{max-width:1024px;margin:auto;background:#101311;color:#f4f4ef;padding:clamp(12px,3vw,32px);font:17px/1.6 system-ui,sans-serif} h1{font-size:clamp(24px,5vw,38px);margin:.25em 0}h2{font-size:21px}small,time{color:#e9ce83}video{width:100%;display:block;background:black;aspect-ratio:16/9}a{color:#8fdbcd} nav{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(290px,100%),1fr));gap:.25em 1em} nav a{padding:.25em 0;text-decoration:none}time{display:inline-block;min-width:3.1em;font-variant-numeric:tabular-nums}a:focus-visible{outline:2px solid #e9ce83}</style>
<small>얌얌코딩 · 게임수학 M22</small><h1>스키닝과 노멀 맵</h1>
<p>팔꿈치를 굽히면 소매는 어떻게 따라올까요? 겉모양을 움직이는 뼈에서 시작해, 빛을 받는 표면의 방향까지 따라갑니다.</p>
<video controls playsinline preload="metadata" src="SLUG.captioned.mp4"></video>
<p>DURATION · 1920 × 1080 · 60 fps　 <a href="SLUG.captioned.mp4">자막 포함 MP4 열기</a></p>
<h2>장면 바로 보기</h2><nav>CHAPTERLINKS</nav>
<p><a href="SLUG.clean.mp4">자막 없는 MP4</a>　 <a href="SLUG.ko.srt">한국어 자막</a>　 <a href="SLUG.en.srt">English subtitles</a></p>
<script>const v=document.querySelector('video');let initial=Number((location.hash.match(/^#t=([\d.]+)$/)||[])[1]);if(Number.isFinite(initial)){let seek=()=>{v.currentTime=initial};if(v.readyState)seek();else v.addEventListener('loadedmetadata',seek,{once:true})}document.querySelectorAll('[data-t]').forEach(el=>el.addEventListener('click',e=>{e.preventDefault();let t=Number(el.dataset.t);let go=()=>{v.currentTime=t;v.play().catch(()=>{})};if(v.readyState)go();else v.addEventListener('loadedmetadata',go,{once:true});history.replaceState(null,'',el.hash)}))</script></html>"""
 (dest/'index.html').write_text(page.replace('SLUG',slug).replace('DURATION',f'{int(duration)//60}분 {int(duration)%60}초').replace('CHAPTERLINKS',''.join(links)),encoding='utf-8')
