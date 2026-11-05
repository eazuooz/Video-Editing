"""Render the Korean editorial topic inventory. Source PDF and artwork stay local."""
from collections import Counter
import csv
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = Path('C:/Users/1/Downloads/유니티 로우폴리 에셋/Architectural%20Approach%20to%20Level%20Design.pdf')
CHAPTERS = ['서문·서론','공간 연출의 역사','스케치·설계 도면','레벨 제작 과정','공간 구조·카메라','환경으로 정보 전달','위험과 안전','공간과 보상','첫 레벨과 학습','공간 내러티브','가능성 공간·월드빌딩','절차적 생성','멀티플레이 공간','사운드와 리듬','결론·통합 실습']
ROMAN = {'xix':19,'xxiii':23,'xxix':29,'xxxv':35}
ESSAYS = {1:(44,50),2:(103,108),4:(205,212),5:(249,255),6:(295,298),8:(379,386),9:(425,428),11:(496,502)}
PICKS = [
    ('수레는 통과하는데','실제 제작 과정이 구체적이다. TF2 수레를 세워 놓고 같은 터널에서 사람 한 명이 옆을 지나갈 수 있는지만 보여줘도 된다.','그림 3.1–3.2'),
    ('바다가 딱','벽의 틈 밖에서는 안 보이던 바다가 단 한 걸음에서 열린다. 소리를 꺼도 전후 차이가 읽힌다.','그림 7.6–7.7'),
    ('엄폐물 하나를','플레이어가 다음 엄폐물을 본 순간에만 안전한 곳에서 뛰쳐나온다. 내려다본 사선과 플레이어 시점을 맞추기 좋다.','그림 6.7–6.8'),
    ('무작위 던전은','던전 생성 과정을 필수 길·곁방·위험물 세 겹으로 분리할 수 있다. 책에 소개된 사례와 자체 생성기를 구분해서 보여 준다.','그림 11.10'),
    ('발판이 일정하면','장애물 간격 하나를 바꾸면 눈으로 본 거리와 귀로 들은 입력 박자가 함께 달라진다.','그림 13.6'),
]
ADJACENT = [
    ('지도는 그대로인데 적 배치','기존 좀비 편은 전투 강도, 여기서는 고정 맵의 통행 경로 변화만 다룬다.'),
    ('보이지 않는 적의 울음소리','둠 편은 몬스터 AI가 경보를 받는 규칙, 여기서는 플레이어가 위험음을 학습하는 과정이다.'),
    ('보상은 왜 정답','기존 보상 편과 가까움. 보상의 양보다 샛길을 발견하고 다시 찾는 동선에 집중한다.'),
    ('빨간 사각형','기존 색·가독성 소재와 인접. 첫 학습과 같은 기호의 재등장을 함께 보여 준다.'),
    ('미니맵을 꺼도','맵 유도 참고 채널 소재와 인접. 도시의 다섯 단서 중 어느 단서가 빠졌는지 비교한다.'),
    ('화살표 없이도 탑','맵 유도 소재와 인접. 목표물이 골목에서 사라졌다 다시 보이는 시점만 다룬다.'),
]
LONG = ('네 번 다르게','세 가지로 고칠','다섯','도시','단계','비례','MMO','카메라 때문','길 하나뿐인','종이에서는','그림자','하나뿐인','단서','서사','이야기','만들 때','맵 설계는','복도에서는','같은 방을 쓰면','훈련','튜토리얼','네모난','자유롭게','PCG','목표','여러','낙하','소설','심리','학습','건축','메뉴','자료','3인칭')

def book_page(label):
    return int(label)+46 if label.isdigit() else ROMAN[label]

def load():
    rows=[]
    for line in (HERE/'topics.txt').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):continue
        ch,span,hook,principle,demo=line.split('|');ch=int(ch)
        start,end=(book_page(x) for x in span.split('-'))
        kind='기고·인터뷰' if ch in ESSAYS and ESSAYS[ch][0]<=int(span.split('-')[0])<=ESSAYS[ch][1] else ('도입·종합' if ch in (0,14) else '본문')
        flag=next((note for prefix,note in ADJACENT if note and hook.startswith(prefix)),'')
        rank=next((i+1 for i,(s,_,__) in enumerate(PICKS) if hook.startswith(s)),None)
        form='쇼츠' if rank or not any(t in hook for t in LONG) else '강의·연작'
        rows.append(dict(ch=ch,span=span,first=start,last=end,hook=hook,principle=principle,demo=demo,kind=kind,overlap=flag,rank=rank,form=form))
    rows.sort(key=lambda x:(x['ch'],x['first']))
    seq=Counter()
    for r in rows:
        seq[r['ch']]+=1;r['id']=f"{r['ch']:02}.{seq[r['ch']]:02}"
    return rows

def page_link(row):
    return f'{BOOK.as_uri()}#page={row["first"]}'

def main():
    rows=load();counts=Counter(r['ch'] for r in rows)
    assert set(counts)==set(range(15)) and len({r['hook'] for r in rows})==len(rows)
    assert sum(bool(r['rank']) for r in rows)==len(PICKS)
    with (HERE/'topics.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        w=csv.writer(stream);w.writerow(['번호','장','구분','제안 제목','게임 제작 기법','자체 비교 시연','책 인쇄쪽','PDF쪽','우선 검수 순위','추천 형식','겹침 검토'])
        for r in rows:w.writerow([r['id'],CHAPTERS[r['ch']],r['kind'],r['hook'],r['principle'],r['demo'],r['span'],f"{r['first']}-{r['last']}",r['rank'] or '',r['form'],r['overlap']])
    esc=escape
    options=''.join(f'<option value="{c}">{esc(CHAPTERS[c])} ({counts[c]})</option>' for c in range(15))
    shortlist=''
    for i,(start,reason,fig) in enumerate(PICKS,1):
        r=next(r for r in rows if r['rank']==i)
        shortlist+=f'<li><a href="#t{r["id"]}">{esc(r["hook"])}</a><p>{esc(reason)} <small>책 {r["span"]}쪽 · {fig}</small></p></li>'
    sections=[]
    for c,name in enumerate(CHAPTERS):
        articles=[]
        for r in (r for r in rows if r['ch']==c):
            tags=' · '.join(x for x in [r['kind'],r['form'],'우선 '+str(r['rank']) if r['rank'] else ''] if x)
            overlap=f'<p class="related"><b>겹침 검토</b> {esc(r["overlap"])}</p>' if r['overlap'] else ''
            articles.append(f'''<article id="t{r['id']}" data-ch="{c}" data-rank="{r['rank'] or ''}" data-overlap="{int(bool(r['overlap']))}" data-kind="{r['kind']}"><div class="line"><span>{r['id']} · {tags}</span><a href="{page_link(r)}" target="_blank" rel="noopener">책 {r['span']}쪽 ↗ <small>PDF {r['first']}–{r['last']}</small></a></div><h3>{esc(r['hook'])}</h3><p>{esc(r['principle'])}</p><p class="demo"><b>시연</b> {esc(r['demo'])}</p>{overlap}</article>''')
        sections.append(f'<section class="chapter" data-ch="{c}"><h2>{str(c)+"장 · " if 1<=c<=13 else ""}{esc(name)} <small>{counts[c]}개</small></h2>'+''.join(articles)+'</section>')
    out='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>책에서 찾은 레벨 디자인 영상 주제 · 얌얌코딩</title><style>
*{box-sizing:border-box}body{margin:0;background:#101513;color:#f3f4ed;font:16px/1.7 "Malgun Gothic",sans-serif}main{max-width:960px;margin:auto;padding:32px 22px 64px}h1{font-size:clamp(27px,4vw,42px);line-height:1.24;margin:10px 0}h2{margin:32px 0 12px;color:#ffdc81;font-size:22px}h3{font-size:19px;line-height:1.5;margin:6px 0} p{margin:6px 0 10px}a{color:#8ce4c5}small,.intro{color:#c1cbc3}.line{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:13px;color:#b8c5bd}.line a{text-decoration:none}.line small{white-space:nowrap}article{border-top:1px solid #48534d;padding:16px 0;scroll-margin-top:12px}.demo b,.related b{color:#a8e0c9}.related{color:#ded1ab}label{display:block;font-size:14px}input,select,button{display:block;padding:9px 10px;border:1px solid #778a7d;background:#1c2721;color:white;font:inherit;border-radius:3px;max-width:100%}button{cursor:pointer}.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end}.chapter[hidden],article[hidden]{display:none}ol{padding-left:24px}li::marker{color:#ffdc81;font-weight:bold}.summary{border-left:3px solid #f5d788;padding:0 14px}.line small{color:#b8c5bd}#summary{font-size:14px;color:#c1cbc3}@media(max-width:550px){main{padding:18px 14px}.controls>*{min-width:0;flex:1 1 140px}article{padding:13px 0}}@media print{body{background:white;color:black}a,h2,.intro,small,.line,.line small,#summary,.demo b,.related{color:#263e31}.controls{display:none}article{break-inside:avoid}}
</style></head><body><main><h1>게임으로 보여줄 수 있는 레벨 디자인</h1>'''
    out+=f'<p>Christopher W. Totten, <i>An Architectural Approach to Level Design</i>, 제2판(2019) · 영상 주제 <b>{len(rows)}개</b></p>'
    out+='<p class="intro">본문 13장과 서문·결론, 실습과 개발자 기고를 검토해 하나의 플레이 질문으로 묶었다. 각 항목의 쪽수는 책의 근거이고, ‘시연’은 얌얌코딩에서 새로 만들 장면이다. 시연 결과나 상용 게임의 내부 구현을 확인했다는 뜻은 아니다.</p>'
    out+='<h2>먼저 만들어 볼 5편</h2><ol>'+shortlist+'</ol>'
    out+='<details><summary>검수 범위와 페이지 읽는 법</summary><p>첨부 PDF의 626페이지를 기준으로 본문 1–556쪽, 서문·서론, 장 끝 요약·실습, 8개 기고·인터뷰 구간을 확인했다. 인쇄 1쪽은 PDF 47페이지이며 본문에서는 인쇄쪽에 46을 더한다. 표지·서지·감사·주석·색인은 독립 주제로 세지 않았다. 원리와 변수가 같은 사례·연습은 합쳤고 기획 의도가 달라지는 사례는 분리했다.</p><p>본문 텍스트와 도판 캡션을 전 장에서 대조하고 28개 대표 페이지를 이미지로 확인했다. 쪽수 링크는 제공받은 원본의 로컬 경로로 연결된다. 페이지 이미지·스크린샷은 납품 목록에 복제하지 않았다. 실제 게임 장면을 쓸 후보는 제작 단계에서 별도 촬영·근거·사용 조건을 확인한다.</p></details>'
    out+=f'<h2>전체 주제</h2><p><a href="topics.csv" download>검수표 CSV 내려받기</a></p><div class="controls"><label>검색<input id="q" placeholder="예: 엄폐, 체크포인트"></label><label>범위<select id="ch"><option value="">전체 장</option>{options}</select></label><label>모아보기<select id="mode"><option value="">전체</option><option value="rank">우선 검수 5편</option><option value="related">기존·참고 소재와 인접</option><option value="essay">기고·인터뷰</option></select></label><button id="reset">필터 초기화</button></div><p id="summary" aria-live="polite">{len(rows)}개 표시</p>'
    out+=''.join(sections)+r'''</main><script>
const q=document.querySelector('#q'), ch=document.querySelector('#ch'), mode=document.querySelector('#mode');
function update(){let n=0;for(const s of document.querySelectorAll('.chapter')){let count=0;for(const a of s.querySelectorAll('article')){const ok=(!ch.value||a.dataset.ch===ch.value)&&(!mode.value||(mode.value==='rank'&&a.dataset.rank)||(mode.value==='related'&&a.dataset.overlap==='1')||(mode.value==='essay'&&a.dataset.kind==='기고·인터뷰'))&&q.value.toLowerCase().trim().split(/\s+/).every(w=>a.innerText.toLowerCase().includes(w)||a.textContent.toLowerCase().includes(w));a.hidden=!ok;if(ok)count++}s.hidden=!count;n+=count}document.querySelector('#summary').textContent=n?n+'개 표시':'일치하는 주제가 없습니다.'}
q.oninput=ch.onchange=mode.onchange=update;function clear(){q.value=ch.value=mode.value='';update()}document.querySelector('#reset').onclick=clear;document.querySelectorAll('ol a').forEach(a=>a.onclick=clear);
</script></body></html>'''
    (HERE/'catalog.html').write_text(out,encoding='utf8')
    print(f'{len(rows)} topics across chapters:',dict(sorted(counts.items())))

if __name__=='__main__':main()
