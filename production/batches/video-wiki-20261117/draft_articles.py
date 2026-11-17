"""Make editable full-lesson drafts, retaining all instructional speech; never publish."""
import difflib, hashlib, json, re
from pathlib import Path
ROOT=Path('D:/Github/VideoEditing');HERE=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def norm(s):return re.sub('[^가-힣a-zA-Z0-9]','',s).lower()
def scene_lines(s):
    lines=s.get('lines',s.get('paragraphs',[]))
    if isinstance(lines,str):return [lines]
    return [v if isinstance(v,str) else v.get('text',v.get('koText','')) for v in lines]
def prose(text):
    text=re.sub(r'<[^>]+>','',text)
    for a,b in [('안녕하세요. 얌얌코딩입니다.',''),('안녕하세요, 얌얌코딩입니다.',''),
        ('이번 영상에서는','이 장에서는'),('오늘은','이 장에서는'),('오늘의 질문','이 장의 질문'),
        ('이번에는','이제'),('영상에서는','설명에서는'),('여러분도','직접'),
        ('에프 피 에스','FPS'),('에프피에스','FPS'),('초당 예순 프레임','초당 60프레임')]:text=text.replace(a,b)
    sentences=re.split(r'(?<=[.?!])\s+',text.strip())
    out=[];buf=[]
    for sentence in sentences:
        if not sentence:continue
        buf.append(sentence)
        if len(buf)>=3 or len(' '.join(buf))>=260:
            out.append(' '.join(buf));buf=[]
    if buf:out.append(' '.join(buf))
    return '\n\n'.join(out)

def sections(row):
    project=ROOT/'projects'/row['slug'];doc=row.get('sceneDocument')
    if doc is None:
        candidates=[project/'production/series-v1/narration.ko.json',ROOT/'production/batches/animation-18-20261031/scripts'/row['id']/'narration.ko.json']
        p=next((x for x in candidates if x.exists()),None)
        if p:doc=rd(p);row['sceneSource']=str(p)
    scenes=doc.get('scenes',[]) if isinstance(doc,dict) else (doc or [])
    scenes=[s for s in scenes if isinstance(s,dict) and not re.search('멤버|아웃트로|엔딩|감사',s.get('title',''))]
    cues=row.get('cues',[])
    if not cues:
        return [dict(title=s.get('title','핵심 원리'),text=prose(' '.join(scene_lines(s)))) for s in scenes]
    useful=[]
    for cue in cues:
        if re.search('멤버십|멤버쉽|구독과 좋아요|시청해 주셔서 감사합니다|프로그래밍 코칭',cue['text']):break
        useful.append(cue)
    if not useful:return []
    text=' '.join(c['text'] for c in useful); normalized=norm(text)
    char_to_cue=[]
    for i,c in enumerate(useful):char_to_cue.extend([i]*len(norm(c['text'])))
    starts=[(0,scenes[0].get('title','장면에서 시작하기') if scenes else '장면에서 시작하기')]
    cursor=0
    for s in scenes[1:]:
        ref=norm(' '.join(scene_lines(s)))
        if not ref:continue
        match=difflib.SequenceMatcher(None,ref,normalized[cursor:],autojunk=False).find_longest_match()
        if match.size<14:continue
        pos=cursor+match.b
        cue_index=char_to_cue[min(pos,len(char_to_cue)-1)]
        while cue_index>0 and not re.search(r'[.!?。？！]$',useful[cue_index-1]['text'].strip()):
            cue_index-=1
        if cue_index<=starts[-1][0]:continue
        starts.append((cue_index,s.get('title','다음 단계')))
        cursor=pos+min(match.size,12)
    result=[]
    for i,(start,title) in enumerate(starts):
        end=starts[i+1][0] if i+1<len(starts) else len(useful)
        result.append(dict(title=title,seconds=useful[start]['seconds'],text=prose(' '.join(c['text'] for c in useful[start:end]))))
    return result

def main():
    sources=rd(HERE/'sources.json');pub=rd(HERE/'publication.json');ready=[]
    (HERE/'drafts').mkdir(exist_ok=True)
    for row in sources['rows']:
        if row['id']=='D10':continue
        prior=HERE/'drafts'/f"{row['id']}.json"
        if prior.exists() and rd(prior).get('status','').startswith('editorially-reviewed'):
            continue
        ss=sections(row)
        if not ss:continue
        ident=row['id'];title=row['title'].split(' #')[0]
        if row['series']=='game-animation':title=ident+'. '+title
        content='\n\n'.join('## '+s['title']+'\n\n'+s['text'] for s in ss if s['text'])
        flags=[]
        if any(x in content for x in ['사쿠라이','원영상','원본 영상에서는']):flags.append('source-creator-framing-needs-editorial-rewrite')
        if len(content)<650:flags.append('needs-more-prerequisites-and-detailed-explanation')
        if '마네킹' in content or '로봇' in content:flags.append('check-latest-game-and-diagram-binding')
        draft=dict(id=ident,title=title,series=row['series'],videoId=row.get('videoId'),sections=ss,
            body=content,baseBody=content,status='editorial-draft-not-published',flags=flags,
            sources={k:row[k] for k in ['textSource','textSourceSha256','sceneSource','sceneSourceSha256'] if k in row})
        wr(HERE/'drafts'/f'{ident}.json',draft)
        ready.append(dict(id=ident,series=row['series'],chars=len(content),flags=flags,
            existingPage=pub['pages'].get(ident),status=draft['status']))
    wr(HERE/'draft-index.json',dict(status='editorial-review-pending',rows=ready))
    print('Editable complete-lesson drafts:',len(ready),'(no Notion writes).')

if __name__=='__main__':main()
