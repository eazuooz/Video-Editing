"""Package the actual Unity build with the authored browser shell. Local review only."""
from pathlib import Path
import hashlib,json,shutil
P=Path(__file__).resolve().parents[1];L=P/'production/local/living-room-v8';W=L/'webgl'
report=json.loads((L/'web-build.json').read_text('utf-8-sig'))
assert report['result']=='Succeeded' and not report['errors'],report
def one(pattern):
    files=list((W/'Build').glob(pattern));assert len(files)==1,(pattern,files)
    return 'Build/'+files[0].name
config={'loader':one('*.loader.js'),'config':{'dataUrl':one('*.data.unityweb'),'frameworkUrl':one('*.framework.js.unityweb'),'codeUrl':one('*.wasm.unityweb'),'streamingAssetsUrl':'StreamingAssets','companyName':'YamyamCoding','productName':'Yamyam Lofi Room','productVersion':'0.8'}}
for name in ('index.html','room.css','room.js'):
    raw=(P/'game-web'/name).read_text('utf-8')
    if name=='index.html':
        raw=raw.replace('<button id="quality">화질: 기본</button>','')
        for resource in ('room.js','room.css'):
            digest=hashlib.sha256((P/'game-web'/resource).read_bytes()).hexdigest()[:12]
            raw=raw.replace('"'+resource+'"','"'+resource+'?v='+digest+'"')
    (W/name).write_text(raw,'utf-8')
(W/'build-config.js').write_text('const LOFI_BUILD='+json.dumps(config)+';\n','utf-8')
(W/'credits.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>방의 재료들</title><link rel="stylesheet" href="room.css"><main style="max-width:850px;margin:4rem auto;line-height:1.9;padding:24px"><a href="index.html">← 방으로</a><h1>방의 재료들</h1><p>얌얌코딩의 자체 방·코드·배치·식물·환경 셰이더. 캐릭터와 헤드폰은 자체 참고 이미지로 Tripo Studio에서 생성·정리했습니다. 가구와 인터랙션은 별도 제작했습니다.</p><h2>움직임과 음악</h2><p>걷기·대기: Tripo 생성 캐릭터의 내보낸 모션.<br>앉기·눕기·일어나기: <a href="https://kaylousberg.itch.io/kaykit-character-animations">KayKit Character Animations 1.1 / Kay Lousberg</a> — CC0 1.0.<br>독서: <a href="https://emaceart.itch.io/philipp-stylized-modular-low-poly-character">PHILIPP / EmacEArt</a> — 프로젝트 사용 허용 라이선스, 원본 파일 별도 배포 없음.<br>HoliznaCC0 — CC0 1.0 로파이 열 곡. 전체 곡 목록은 아래에 표시합니다.<br><a href="https://opengameart.org/content/fireplace-sound-loop">Fireplace Sound loop — PaGDev</a>, CC0 1.0.</p><p>메모·설정·타이머는 이 주소의 브라우저 저장소에 남습니다. 서버로 메모를 보내지 않습니다. 브라우저 데이터를 지우거나 다른 주소로 열면 이전 메모가 보이지 않을 수 있습니다.</p><p>Unity 6000.6 · URP · WebGL 2 / WebAssembly. 현 버전은 로컬 검수용입니다.</p></main></html>''','utf-8')
import html
playlist=json.loads((P/'production/living-v8-music.json').read_text('utf-8'))['tracks']
credit=W/'credits.html';body=credit.read_text('utf-8');body=body.replace('</main>', '<h2>음악 열 곡</h2><ul>'+''.join('<li>'+html.escape(t['title'])+' — '+html.escape(t['artist'])+' · CC0 1.0</li>' for t in playlist)+'</ul><p><a href="https://opengameart.org/content/lo-fi-and-chill-collection">작곡가 배포·라이선스 원문</a></p></main>');credit.write_text(body,'utf-8')
files=[{'path':f.relative_to(W).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest()} for f in W.rglob('*') if f.is_file()]
(L/'web-files.json').write_text(json.dumps({'build':report,'config':config,'files':files,'publicDeployment':False},indent=2)+'\n','utf-8')
print(json.dumps({'files':len(files),'bytes':sum(f['bytes'] for f in files),'gameRoot':str(W)}))
