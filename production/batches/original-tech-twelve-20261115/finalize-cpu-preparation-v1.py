"""Record the actual source-preparation boundary without touching foreign work."""
from pathlib import Path
import datetime, hashlib, html, importlib.util, json, re, sys

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
REF=MEDIA/'ten-cpu-prep-20261115'
KEY='explicitOriginalTechTwelve20261115'
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
    with p.open('rb') as h: digest=hashlib.file_digest(h,'sha256').hexdigest()
    return dict(path=str(p.resolve()),sha256=digest)
def save(p,d,new=False):
    if new: assert not p.exists(),p
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def replace_value(text,key,value):
    matches=list(re.finditer(r'"'+re.escape(key)+r'"\s*:\s*',text));assert len(matches)==1
    start=matches[0].end();_,n=json.JSONDecoder().raw_decode(text[start:])
    replacement=json.dumps(value,ensure_ascii=False,indent=2).replace('\n','\n  ')
    return text[:start]+replacement+text[start+n:]
def replace_rows(text,rows):
    pos=re.search(r'"rows"\s*:\s*\[',text).end();changes=[];decoder=json.JSONDecoder()
    while True:
        while text[pos].isspace() or text[pos]==',': pos+=1
        if text[pos]==']':break
        value,n=decoder.raw_decode(text[pos:])
        if value.get('id') in rows:
            replacement=json.dumps(rows[value['id']],ensure_ascii=False,indent=2).replace('\n','\n    ')
            changes.append((pos,pos+n,replacement))
        pos+=n
    assert len(changes)==len(rows)==12
    for a,z,s in reversed(changes):text=text[:a]+s+text[z:]
    return text

def main():
    validation_path=HERE/'cpu-preparation-current-validation-v1.json'
    assert not validation_path.exists(),'Current CPU source unit already finalized'
    batch=read(HERE/'batch.json');assert len(batch['projects'])==12
    assert batch['authorization']['fullProductionAuthorized']
    assert batch['authorization']['intermediateApprovalRequired'] is False
    paragraph_count=0;local_links=[]
    for row in batch['projects']:
        folder=ROOT/'projects'/row['slug'];planning=folder/'planning'
        draft_path=sorted(planning.glob('narration-draft-v*.json'))[-1];draft=read(draft_path)
        ids=[p['id'] for p in draft['paragraphs']]
        assert len(ids)==len(set(ids)) and all(p['ko'].strip() and p['en'].strip() for p in draft['paragraphs'])
        assert not draft['approvedForTts'] and not draft['narrationLocked']
        source_map=read(ROOT/draft['sourceOrderMap']);assert source_map['mapping']
        scene=read(ROOT/row['scenePlan'])
        assert {p for beat in scene['beats'] for p in beat['paragraphs']}==set(ids)
        assert not scene['nativeCaptureStarted']
        metadata=read(folder/'publishing/metadata-draft-v1.json')
        assert metadata['titleKo'] and metadata['titleEn'] and not metadata['posted']
        assert not row['voiceGenerated'] and not row['finalOutputsVerified'] and not row['humanApproval']
        if row['order']>2:
            review=read(planning/'primary-source-review-v1.json')
            for item in review['source']['inputs']+review['source']['visualEvidence']:
                assert pin(Path(item['path']))['sha256']==item['sha256'],item['path']
            assert review['source']['fullRelevantScopeReviewed'] and not review['fullSpokenLectureReviewed']
        paragraph_count+=len(ids)
    acquisition=read(HERE/'independent-source-acquisition-progress-v1.json')
    assert acquisition['independentSourcesAcquired']==sum(r['independentFootageAcquired'] for r in batch['projects'])==7
    observation=pin(REF/'resource-observation-v2.json')
    assert read(Path(observation['path']))['reason'] is not None
    batch['delivery'].update(videoCompletionCount=0,bilingualDraftCount=12,scenePlanCount=12,
        independentSourceContainers=7,acceptedFullActionMaps=0)
    save(HERE/'batch.json',batch)
    cp=read(HERE/'checkpoint.json');cp.update(updatedAtKst=NOW,
        phase='all12-bilingual-source-and-scene-preparation;7-source-candidates;external-media-guarded',
        sourceNarrationDraftCount=12,sourceOrderMapCount=12,scenePlanCount=12,metadataDraftCount=12,
        paragraphsKo=paragraph_count,paragraphsEn=paragraph_count,independentSourcesAcquired=7,
        decodedFhdSources=7,resourceObservation=observation,localFinalVideos=0,actualGpuJobsStarted=0,
        intermediateApprovalRequired=False,
        nextStep='Continue exact source-action and publisher/version checks, remaining independent footage and native scene preparation. Run a ready costly stage only after a fresh full guard; current external media worker is preserved.')
    save(HERE/'checkpoint.json',cp)
    continuation=read(HERE/'local-production-continuation-v1.json')
    continuation.update(resourceObservation=observation['path'],currentState=cp['phase'],
        candidateSourceProgress=pin(HERE/'independent-source-acquisition-progress-v1.json'))
    save(HERE/'local-production-continuation-v1.json',continuation)

    # Shared files: splice only our owned key and12 rows; validate the exact
    # surrounding foreign text as well as foreign parsed values before writing.
    shared_receipts=[]
    for rel in ['shared/publishing/video-worklist.json','shared/publishing/video-production-control.json']:
        path=ROOT/rel;original=path.read_bytes();bom=b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b''
        text=original.decode('utf-8-sig');current=json.loads(text);value=dict(current[KEY])
        value.update(updatedAtKst=NOW,sourceNarrationDraftCount=12,sourceOrderMapCount=12,
            scenePlanCount=12,metadataDraftCount=12,independentSourcesAcquired=7,decodedFhdSources=7,
            localFinalVideos=0,resourceStatus=read(REF/'resource-observation-v2.json')['reason'],
            reviewPage='production/batches/original-tech-twelve-20261115/preproduction-v3.html')
        result=replace_value(text,KEY,value)
        if path.name=='video-worklist.json':
            selected={row['id']:dict(row) for row in current['rows'] if row['id'].startswith('OT12-')}
            assert len(selected)==12
            for row in batch['projects']:
                selected[row['id']]['productionStatus']=('1차 자료·한영 대본·장면 준비 / 독립 원본·후보 행동 대조 중'
                    if row['independentFootageAcquired'] else '1차 자료·한영 대본·장면 준비 / 독립 게임 영상 확보 중')
                evidence=selected[row['id']].get('evidence',[])+[row.get('sourceCandidateReview',row['currentSourceReview'])]
                selected[row['id']]['evidence']=list(dict.fromkeys(evidence))
            result=replace_rows(result,selected)
            neutral={id:{'id':id} for id in selected}
            assert replace_rows(replace_value(text,KEY,{}),neutral)==replace_rows(replace_value(result,KEY,{}),neutral)
        else:assert replace_value(text,KEY,{})==replace_value(result,KEY,{})
        assert path.read_bytes()==original,'Concurrent shared file update; reread instead of overwriting'
        path.write_bytes(bom+result.encode('utf8'))
        shared_receipts.append(dict(path=rel,foreignTextPreserved=True,after=pin(path)))

    # The worklist document is a current status table, not the final review.
    path=ROOT/'docs/VIDEO_WORKLIST.md';original=path.read_bytes();text=original.decode('utf-8-sig')
    start='<!-- ORIGINAL-TECH-TWELVE-20261115 -->';end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->'
    a=text.index(start);z=text.index(end)+len(end)
    block=start+'\n## 새 게임 개발 기술 쇼츠12편\n\n'
    block+='2026-11-15 최신 요청에 따라 대기 중 나머지10편의 자료·한영 대본을 준비했다. 현재12편 모두 선택한 1차 자료 범위 검토·한영 대본·자료 순서 대응·장면 구성·제목/설명 초안 준비. 총73문단씩이며, 독립 원본/후보7편의 FHD 이상 컨테이너를 확인했다. 정확한 행동·판본·권리의 최종 대조는 별도이며 음성·Unity 촬영·최종 영상은0편이다. 마지막 전체 자원 검사는 다른 미디어 작업을 감지했다. 중간 확인 없이 이12편을 로컬 최종 검수까지 제작하는 허가는 유지되며 게시·다른 자동화는 변경하지 않는다.\n\n'
    block+='| 순서 | 토픽 | 현재 준비 |\n|---:|---|---|\n'
    for row in batch['projects']:
        status='자료·KO/EN 대본·장면 준비 / 독립 후보 대조 중' if row['independentFootageAcquired'] else '자료·KO/EN 대본·장면 준비 / 독립 영상 확보 중'
        block+=f'| {row["order"]} | {row["title"]} | {status} |\n'
    block+='\n[12편 자료·대본·진행표](../production/batches/original-tech-twelve-20261115/preproduction-v3.html) — 최종 영상 검수표가 아님.\n'+end
    result=text[:a]+block+text[z:];assert path.read_bytes()==original
    path.write_bytes((b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf')else b'')+result.encode('utf8'))
    assert result[:a]==text[:a] and result[a+len(block):]==text[z:]

    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('ot12_page',HERE/'prepare-remaining-ten-v1.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.render_page(batch,new=False)
    page=(HERE/'preproduction-v3.html').read_text(encoding='utf8')
    assert page.count('<article ')==12 and page.count('lang="en"')==paragraph_count
    assert '최종 영상0/12' in page and '독립 영상7편' in page
    for uri in re.findall(r'href="(file:[^"]+)"',page):
        from urllib.parse import urlparse, unquote
        local=unquote(urlparse(html.unescape(uri)).path).lstrip('/')
        assert Path(local).is_file(),local
        local_links.append(local)
    source_paths=[]
    for folder in [HERE]+[ROOT/'projects'/row['slug'] for row in batch['projects']]:
        source_paths.extend(p for p in folder.rglob('*') if p.is_file() and p.suffix in ['.json','.md','.html','.py'] and '__pycache__' not in p.parts)
    source_paths.extend(ROOT/rel for rel in ['shared/publishing/video-production-control.json','shared/publishing/video-worklist.json','docs/VIDEO_WORKFLOW.md','docs/VIDEO_WORKLIST.md'])
    save(validation_path,dict(schemaVersion=1,checkedAtKst=NOW,exactTopicCount=12,
        relevantPrimaryScopesReviewed=12,bilingualDrafts=12,scenePlans=12,metadataDrafts=12,
        koParagraphs=paragraph_count,enParagraphs=paragraph_count,sourceOrderMaps=12,
        independentSourceContainers=7,completeActionMapsAccepted=0,localFinalVideos=0,
        modelJobsStarted=0,nativeCaptureJobsStarted=0,productionRenderJobsStarted=0,
        existingFullGuard=observation,resourcesReady=False,sourceOnlyCpuPreparation=True,
        allNarrationUnlocked=True,humanApproval=False,newRecurringAutomationCreated=False,
        platformActions=[],localHtmlLinksChecked=len(local_links),sharedPreservation=shared_receipts,
        repairNote='The one-shot packet writer completed its source writes but initially failed rendering the older OOT map schema. Only its page renderer was repaired/rerun; existing preparation was not repeated.',
        acquisitionLimits=['MarioKart public-file acquisition exceeded a bounded timeout; partial file preserved, not adopted.','DOOM sparse frame extraction exceeded its bounded timeout; existing8frames preserved, not relabelled full viewing.','Spider-Man first range rejected for action mismatch; different250–310s range acquired and sparse-inspected.'],
        sourceInputs=[pin(p) for p in sorted(set(source_paths))]),new=True)
    print(json.dumps(dict(drafts=12,paragraphs=paragraph_count,scenePlans=12,independentContainers=7,
        finalFilms=0,resourceGuard=read(REF/'resource-observation-v2.json')['reason'],
        sourcePaths=len(set(source_paths)),htmlLinksChecked=len(local_links)),ensure_ascii=False))

if __name__=='__main__':main()
