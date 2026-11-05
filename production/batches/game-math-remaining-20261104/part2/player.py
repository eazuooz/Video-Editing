"""Local review player with links to the actual recorded game and formula examples."""
import html,json
from pathlib import Path

def render(destination,queue):
    read=lambda p:json.loads(p.read_text("utf-8-sig"))
    root=Path(__file__).resolve().parents[4];project=root/"projects"/queue["project"]
    draft=read(project/"planning/production-plan.json")["localReviewPresentation"]
    title=html.escape(draft["selectedTitleKo"])
    plan=read(project/"planning/part2-picture-plan.json")
    timeline=read(Path(queue["wordAlignment"]))
    game={c["scene"]:c for c in queue["cuts"] if c["kind"]=="actual-gameplay"}
    scenes={s["id"]:s for s in timeline["scenes"]}
    original=read(project/"planning/scene-bindings.json")["scenes"]
    links=[]
    for row in original:
        sid=row["id"];c=game.get(sid);figure=plan["teachingFigures"].get(sid)
        if not (c or figure):continue
        frame=(c["globalStartFrame"] if c else scenes[sid]["startFrame"])+120
        sec=frame/60
        label=row["actualGamePart"]["game"]+" · 게임 장면" if c else figure["purpose"]
        links.append(f'<a href="#t={sec:.3f}" data-t="{sec:.3f}"><time>{int(sec)//60:02}:{int(sec)%60:02}</time> {html.escape(label)}</a>')
    slug=queue["project"];duration=(720+queue["bodyFrames"])/60
    page=r'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TITLE</title>
<style>:root{color-scheme:dark}body{max-width:1040px;margin:auto;padding:clamp(12px,3vw,32px);background:#101412;color:#f1f2ec;font:17px/1.6 system-ui}h1{font-size:clamp(26px,4vw,40px)}h2{font-size:21px}a{color:#8ed6c7}video{width:100%;aspect-ratio:16/9;background:black}time{color:#e9ce83;font-variant-numeric:tabular-nums}nav{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(275px,100%),1fr));gap:8px 20px}nav a{text-decoration:none}a:focus-visible{outline:2px solid #e9ce83}</style>
<a href="../game-math-remaining-20261104/index.html">← 파트 2 검수표</a><h1>TITLE</h1><p>SUMMARY</p>
<video controls playsinline preload="metadata" src="SLUG.captioned.mp4"></video>
<p>DURATION · 1080p60　<a href="SLUG.captioned.mp4">자막판 MP4 열기</a></p>
<h2>게임 예시와 수식 설명</h2><nav>LINKS</nav>
<p><a href="SLUG.clean.mp4">무자막 MP4</a>　<a href="SLUG.ko.srt">한국어 자막</a>　<a href="SLUG.en.srt">English subtitles</a></p>
<script>const v=document.querySelector('video');function seek(t,play){const go=()=>{v.currentTime=t;if(play)v.play().catch(()=>{})};v.readyState?go():v.addEventListener('loadedmetadata',go,{once:true})}const initial=location.hash.match(/^#t=([\d.]+)$/);if(initial)seek(Number(initial[1]),false);document.querySelectorAll('[data-t]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();seek(Number(a.dataset.t),true);history.replaceState(null,'',a.hash)}))</script></html>'''
    (destination/"index.html").write_text(page.replace("TITLE",title).replace("SUMMARY",html.escape(draft["viewerPromiseKo"])).replace("SLUG",slug).replace("DURATION",f"{int(duration)//60}분 {int(duration)%60}초").replace("LINKS","".join(links)),encoding="utf8")
