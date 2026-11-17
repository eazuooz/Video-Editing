"""Make the selected tutorial's local copyable requests, beside the full review."""
from pathlib import Path
import html,json,shutil
P=Path(__file__).resolve().parents[1];F=P/'production/local/full-video-v5/final';F.mkdir(exist_ok=True)
j=json.loads((P/'planning/reproduction-recipes.json').read_text('utf-8'))
labels=['방의 기준 이미지','캐릭터 입력 이미지','헤드폰 입력 이미지','Tripo 생성·정리·내보내기','작업할 프로젝트와 보존 범위','방과 가구 배치','텍스처와 재질','생활 동작과 중간 전환','소파 독서와 테이블·책 접촉','머리카락의 지연','식물과 창밖','창문 안의 비','불꽃·빛·소리','잠든 삼색고양이','열 곡과 레코드','메모와 집중 타이머','Unity Web 빌드']
labels=dict(zip(['room-image', 'hero-image', 'headphone-image', 'tripo', 'unity-scope', 'layout', 'materials', 'actions', 'book-contact', 'hair', 'plants-window', 'rain', 'fire', 'cat', 'radio', 'notes-timer', 'web-build'],labels));labels.update({'sofa-image':'목재·라탄 소파 입력','table-image':'낮은 우드 테이블 입력'})
cards=[]
for i,r in enumerate(j['recipes'],1):
    label=labels[r['id']]
    value=r.get('request','\n'.join(r.get('settings',[])))
    cards.append(f'<article id="{r["id"]}"><small>{i:02} · {html.escape(r["tool"])}</small><h2>{label}</h2><p>입력 · {html.escape(r["input"])}</p><pre>{html.escape(value)}</pre><button>요청문 복사</button><p><b>받을 결과</b> · {html.escape(r["output"])}</p><p><b>확인할 점</b> · {html.escape(r["check"])}</p></article>')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>같은 LOFI 방 만들기 · 요청문</title><style>body{background:#0c1913;color:#e9e8d6;font:19px/1.8 system-ui,sans-serif;margin:0}main{max-width:980px;margin:36px auto;padding:24px}h1{font-size:32px;color:#ebd38b}h2{font-size:25px}small,a{color:#89cdbc}article{border-top:1px solid #3d5146;margin:40px 0;padding-top:22px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:19px/1.8 inherit;background:#192a22;padding:22px}button{font:inherit;color:#e7e6cf;background:#2e4d3b;border:1px solid #719277;padding:8px 16px;cursor:pointer}</style><main><a href="index.html">← 전체 영상 검수</a><h1>AI 도구로 같은 LOFI 방 만들기</h1><p>재현용 요청문 19개입니다. 프로젝트와 입력 파일 경로를 바꿔 사용할 수 있습니다. Tripo는 실제 입력 이미지와 H3.1을 사용했고 추가 텍스트는 비워 두었습니다.</p><p>&lt;PROJECT_PATH&gt;, &lt;HERO_FBX&gt;, &lt;ANIMATION_FOLDER&gt;는 직접 준비한 프로젝트와 파일의 실제 경로로 바꿔 주세요.</p><p><a href="https://www.yamyamcoding.com/41b0b1ff-a61e-8171-8cf1-fa0b0af02ece">설계와 구현 상세 위키</a> · <a href="reproduction-recipes.json" download>요청문 JSON</a></p>'''+''.join(cards)+'''</main><script>document.querySelectorAll('article button').forEach(b=>b.onclick=async()=>{try{await navigator.clipboard.writeText(b.previousElementSibling.textContent);b.textContent='복사했어요';}catch{b.textContent='위 요청문을 선택해 복사해 주세요';}});</script></html>'''
(F/'requests.html').write_text(page,'utf-8');shutil.copy2(P/'planning/reproduction-recipes.json',F/'reproduction-recipes.json')
print('Prepared 19 copyable local requests')
