"""Validate and materialize drafted episodes; never call drafts or candidates finished videos."""
from __future__ import annotations
import hashlib
import html
import json
from datetime import datetime
from pathlib import Path
from initialize import ROOT,HERE,MEDIA,read,save

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def paragraph_numbers(row):
    if 'paragraphs' in row:return row['paragraphs']
    if 'paragraphIndexes' in row:return row['paragraphIndexes']
    if 'paragraph' in row:return [row['paragraph']]
    if 'paragraphIndex' in row:return [row['paragraphIndex']]
    return []

def main():
    batch=read(HERE/'batch.json');expected={r['topicId']:r for r in batch['projects']}
    plans={};inputs={};problems=[]
    for name,chapters in [('a',set(range(5))),('b',set(range(5,10))),('c',set(range(10,15)))]:
        path=HERE/f'planning-{name}.json'
        if not path.exists():continue
        source=read(path);inputs[path.name]=digest(path)
        for episode in source['episodes']:
            ident=episode['topicId'];assert ident in expected and expected[ident]['chapter'] in chapters, ident
            assert ident not in plans,ident
            ko=episode['narrationKo'];en=episode['paragraphsEn']
            if not isinstance(ko,list) or not isinstance(en,list) or len(ko)!=len(en) or len(ko)<4:
                raise ValueError('KO/EN correspondence failed: '+ident)
            if any(not isinstance(p,str) or len(p.strip())<30 for p in ko+en):
                raise ValueError('Empty/fragment narration: '+ident)
            if not all(episode.get(k) for k in ['glossary','sourceMapping','sceneBeats','gameFootageCandidates','technicalClaimLimits']):
                raise ValueError('Missing editorial evidence: '+ident)
            mapped=set(n for m in episode['sourceMapping'] for n in paragraph_numbers(m))
            if mapped != set(range(1,len(ko)+1)):
                problems.append(dict(topicId=ident,issue='source-paragraph-coverage',expected=list(range(1,len(ko)+1)),observed=sorted(mapped)))
            plans[ident]=episode
    override=ROOT/'projects/shorts-leveldesign-03-02/narration-editorial-v1.json'
    if override.exists():
        d=read(override)
        if d.get('readyForDraftIntegration'):
            plans['03.02']=d
    now=datetime.now().astimezone().isoformat();work=read(HERE/'worklist.json');rows=[]
    total_paragraphs=0;verified_sources=0
    for row in batch['projects']:
        item=dict(row);ident=item['topicId'];project=ROOT/item['project'];folder=project.parent
        if ident in plans:
            e=plans[ident];total_paragraphs+=len(e['narrationKo'])
            path=folder/'narration-draft.json';data=json.dumps(e,ensure_ascii=False,indent=2)+'\n'
            if path.exists() and path.read_text(encoding='utf8')!=data:
                archive=MEDIA/item['slug']/'draft-history'/('narration-'+digest(path)+'.json')
                if not archive.exists():archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(path.read_bytes())
            path.write_text(data,encoding='utf8')
            save(folder/'scene-plan-draft.json',dict(topicId=ident,status='planned-not-rendered',sceneBeats=e['sceneBeats'],
                gameFootageCandidates=e['gameFootageCandidates'],technicalClaimLimits=e['technicalClaimLimits']))
            item.update(status='source-mapped-script-draft',draftParagraphCount=len(e['narrationKo']),
                        narrationDraft=f'projects/{item["slug"]}/narration-draft.json',narrationDraftSHA256=digest(path))
        else:item.update(status='script-preparation',draftParagraphCount=0)
        footage=folder/'source-footage.json'
        if footage.exists():
            records=read(footage).get('sources',[])
            good=[s for s in records if s.get('selectedForCut') and s.get('decodedDimensionsVerified') and s.get('rightsReviewed') and s.get('visualSequenceInspected')]
            if good:
                verified_sources+=1;item['footageStatus']='selected-source-reviewed';item['sourceFootageRecord']=footage.relative_to(ROOT).as_posix()
            elif records:
                item['footageStatus']='candidate-reviewed-not-adopted';item['sourceFootageRecord']=footage.relative_to(ROOT).as_posix()
        item.setdefault('footageStatus','candidate-search-required')
        item['productionComplete']=False;item['humanApproval']=False;item['platformStatus']='not-uploaded'
        rows.append(item)
        d=read(project);d.update(status=item['status'],narrationDraft=item.get('narrationDraft'),
            scriptSourceVerification='source-mapped-draft; footage-conformance and editorial audit pending' if ident in plans else 'pending-draft',
            footageSelection=item['footageStatus']);save(project,d)
        cp=read(folder/'checkpoint.json')
        changes=dict(stage=item['status'],narrationDraftSHA256=item.get('narrationDraftSHA256'),
                     draftParagraphCount=item['draftParagraphCount'],footageVerified=item['footageStatus']=='selected-source-reviewed')
        if any(cp.get(k)!=v for k,v in changes.items()):
            cp.update(updatedAt=now,**changes);save(folder/'checkpoint.json',cp)
    save(HERE/'worklist.json',dict(schemaVersion=1,batchId=batch['batchId'],updatedAt=now,rows=rows))
    batch.update(projects=rows,scriptDraftCount=len(plans),completedLocalReviewCount=0,currentPhase='source-mapped-drafts-and-scene-preparation')
    save(HERE/'batch.json',batch)
    cp=read(HERE/'checkpoint.json');cp.update(updatedAt=now,scriptDraftCount=len(plans),draftKoParagraphCount=total_paragraphs,
        draftEnParagraphCount=total_paragraphs,verifiedFootageCount=verified_sources,planningInputSHA256=inputs,
        draftValidationIssues=problems,completedLocalReviewCount=0,completedVoiceCount=0)
    save(HERE/'checkpoint.json',cp)
    report=dict(schemaVersion=1,checkedAt=now,expectedTopics=111,draftedTopics=len(plans),missingTopics=sorted(set(expected)-set(plans)),
        koParagraphs=total_paragraphs,enParagraphs=total_paragraphs,sourceParagraphCoverageIssues=problems,inputSHA256=inputs,
        validationScope='Catalog ID/assigned-chapter/bilingual paragraph/schema/source-map coverage only. Not a full fact, rights, voice, timing or visual approval.',
        renderedVideos=0,humanReviewedVideos=0)
    save(HERE/'planning-validation.json',report)
    build_html(batch,rows,plans,cp)
    print(json.dumps({k:report[k] for k in ['draftedTopics','koParagraphs','enParagraphs','renderedVideos']},ensure_ascii=False))
    if problems:print('SOURCE COVERAGE REVIEW REQUIRED:',len(problems))

def build_html(batch,rows,plans,cp):
    esc=html.escape
    cards=[]
    for row in rows:
        ident=row['topicId'];e=plans.get(ident);parts=''
        if e:
            for i,(ko,en) in enumerate(zip(e['narrationKo'],e['paragraphsEn']),1):
                parts+=f'<p><b>{i}.</b> {esc(ko)}</p><p class="en" lang="en">{esc(en)}</p>'
            gloss=' / '.join(g['english']+' ('+g['korean']+')' for g in e['glossary'] if isinstance(g,dict) and g.get('english') and g.get('korean'))
            parts+=f'<p class="terms">{esc(gloss)}</p>'
            body=f'<details><summary>대본 초안 · 한영 {len(e["narrationKo"])}문단</summary>{parts}<p class="note">독립 실제 영상과 대조한 최종 대본·음성·완성 영상 검수는 아직입니다.</p></details>'
        else:body='<p class="note">원문을 대조하며 대본 작성 중</p>'
        footage=('실제 장면 선택·확인' if row['footageStatus']=='selected-source-reviewed' else
                 '실제 장면 후보 검토 중 · 채택 전' if row['footageStatus']=='candidate-reviewed-not-adopted' else '실제 장면 확보·검토 예정')
        cards.append(f'<article data-ready="{int(bool(e))}"><p class="meta">제작 {row["order"]:03} · {ident} · {esc(row["chapterName"])} · 책 {esc(row["printPages"])}쪽</p><h2>{esc(row["title"])}</h2><p class="status">{footage} · 음성·렌더 전 · 사용자 영상 검수 전</p>{body}</article>')
    out='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>레벨 디자인 111편 제작 현황 · 얌얌코딩</title><style>
*{box-sizing:border-box}body{margin:0;background:#101513;color:#f2f5ef;font:16px/1.75 "Malgun Gothic",sans-serif}main{max-width:970px;margin:auto;padding:28px 22px 80px}h1{font-size:32px;line-height:1.3}h2{font-size:21px;line-height:1.5;margin:7px 0}p{margin:9px 0}.summary{border-left:4px solid #ffdb79;padding-left:16px}.meta,.note,.en{color:#b8c5bf}.meta{font-size:14px}.status{font-size:14px;color:#ffdb79}article{padding:18px 0 25px;border-bottom:1px solid #435149}summary{cursor:pointer;color:#8de3c0;font-weight:bold}details>p{margin-top:16px}.en{font-size:15px;border-left:2px solid #42534b;padding-left:12px}.terms{font-size:14px}label{display:block;font-size:14px}input,select{font:inherit;color:white;background:#1b2820;border:1px solid #879a8e;padding:10px;border-radius:3px;max-width:100%}.filters{display:flex;gap:16px;flex-wrap:wrap}a{color:#8de3c0}#shown{font-size:14px;color:#b8c5bf}[hidden]{display:none!important}@media(max-width:500px){main{padding:18px 15px 50px}h1{font-size:27px}h2{font-size:20px}.filters>*{flex:1 1 140px}}
</style><main>'''
    out+='<style>body{word-break:keep-all;overflow-wrap:anywhere}</style><h1>레벨 디자인 111편 제작 현황</h1>'
    out+=f'<div class="summary"><p>선택한 주제 <b>111편</b> · 한영 대본 초안 <b>{cp["scriptDraftCount"]}편</b> · 완성 검수본 <b>0편</b></p><p>실제 게임 현상 → 작동 원리 → 한 변수 비교 → 실제 게임 확인 순서로 제작합니다. 같은 수레·사람·터널을 유지하는 첫 편의 Unity 소스와 충돌 실험을 준비했습니다. 다른 제작의 GPU 렌더링을 보존하며 자료와 대본을 먼저 진행하고 있습니다.</p></div>'
    out+='<p class="note">이 페이지는 제작·대본 현황입니다. 아직 완성 영상 플레이어가 아닙니다. 실제 완성 MP4가 검증되면 그 파일과 한영 자막을 별도로 연결합니다. Google Drive·YouTube 업로드와 공개·예약은 실행하지 않았습니다.</p>'
    out+='<div class="filters"><label>검색<input id="q" placeholder="제목·기법·대본 검색"></label><label>상태<select id="stage"><option value="">전체 111편</option><option value="1">대본 초안 있음</option><option value="0">대본 작성 중</option></select></label></div><p id="shown"></p>'
    out+=''.join(cards)+r'''</main><script>const q=document.getElementById('q'),s=document.getElementById('stage');function filter(){let n=0;for(const a of document.querySelectorAll('article')){const ok=(!s.value||a.dataset.ready===s.value)&&q.value.toLowerCase().trim().split(/\s+/).every(t=>a.textContent.toLowerCase().includes(t));a.hidden=!ok;n+=ok}document.getElementById('shown').textContent=n+'편 표시'}q.oninput=s.onchange=filter;filter()</script></html>'''
    (HERE/'worklist.html').write_text(out,encoding='utf8')
    delivery=MEDIA/'delivery';delivery.mkdir(exist_ok=True);(delivery/'index.html').write_text(out,encoding='utf8')

if __name__=='__main__':main()
