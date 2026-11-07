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

def assert_preproduction_only(*, root=ROOT, here=HERE, media=MEDIA):
    """Read-only guard: this draft initializer must never roll back production.

    A later-stage merge needs a different, progress-preserving operation. Counts
    here are evidence to reject, never values to infer or repair from artifacts.
    """
    root,here,media=Path(root),Path(here),Path(media)
    batch=read(here/'batch.json');reasons=[]
    safe_statuses={'script-preparation','preproduction-in-progress',
                   'source-mapped-script-draft'}

    def reject_record(record,label):
        for key in ('completedLocalReviewCount','completedVoiceCount',
                    'completedNativeCount','completedOutputCount','renderedVideos',
                    'humanReviewedVideos'):
            if record.get(key):reasons.append(f'{label}: {key} is nonzero')
        for key in ('productionComplete','humanApproval','voiceGenerated',
                    'finalOutputsVerified','actualSceneFilesSaved',
                    'editableUnityScenesSaved','savedScenePaths'):
            if record.get(key):reasons.append(f'{label}: {key} records production')
        if record.get('humanReview') not in (None,False,'','not-delivered','not-started'):
            reasons.append(f'{label}: human review already has a state')
        if record.get('platformStatus') not in (None,'','not-uploaded'):
            reasons.append(f'{label}: platform status must be preserved')
        if record.get('platformActions'):
            reasons.append(f'{label}: platform actions already recorded')
        for key in ('youtubeVideoId','videoId','driveFileId'):
            if record.get(key):reasons.append(f'{label}: {key} already recorded')
        completed=record.get('completedStages',[])
        if completed:
            # Only explicitly preproduction entries can be reset by this helper.
            allowed={'planning','script-draft','source-mapping','footage-selection'}
            if not isinstance(completed,list) or any(s not in allowed for s in completed):
                reasons.append(f'{label}: completed stages go beyond draft preparation')

    reject_record(batch,'batch')
    checkpoint=here/'checkpoint.json'
    if checkpoint.exists():reject_record(read(checkpoint),'batch checkpoint')
    worklist=here/'worklist.json'
    if worklist.exists():
        for row in read(worklist).get('rows',[]):
            reject_record(row,f'worklist {row.get("topicId","?")}')
            if row.get('status') not in (None,'',*safe_statuses):
                reasons.append(f'worklist {row.get("topicId","?")}: later/unknown status')

    for row in batch['projects']:
        ident=row['topicId'];reject_record(row,f'batch {ident}')
        if row.get('status') not in (None,'',*safe_statuses):
            reasons.append(f'batch {ident}: later/unknown status')
        project=root/row['project'];folder=project.parent
        for path in (project,folder/'checkpoint.json',folder/'review-ledger.json'):
            if path.exists():
                record=read(path);reject_record(record,f'{ident} {path.name}')
                for key in ('status','stage'):
                    if record.get(key) not in (None,'',*safe_statuses):
                        reasons.append(f'{ident} {path.name}: later/unknown {key}')
        # Prepared voice manifests are allowed; actual PCM, even before its
        # checkpoint is updated, is not. Read only this episode's TTS output.
        voice=folder/'voice-manifest.json'
        if voice.exists():
            record=read(voice);reject_record(record,f'{ident} voice manifest')
            output=record.get('tts',{}).get('outputDir')
            if output:
                output=Path(output);output=output if output.is_absolute() else root/output
                if output.exists() and any(output.rglob('*.wav')):
                    reasons.append(f'{ident}: generated voice PCM exists')
        for output in (root/'output'/row['slug'],media/row['slug']):
            if output.exists():
                for pattern in ('*clean*.mp4','*captioned*.mp4','*.wav'):
                    if next(output.rglob(pattern),None) is not None:
                        reasons.append(f'{ident}: produced/partial media exists ({pattern})')
                for native in output.glob('native*'):
                    if native.is_dir() and next((p for p in native.rglob('*') if p.is_file()),None):
                        reasons.append(f'{ident}: native capture artifacts exist')

    proof=here/'first-native-evidence.json'
    if proof.exists():reasons.append('first native evidence already exists')
    prep=here/'first-unity-preparation.json'
    if prep.exists():
        record=read(prep);reject_record(record,'first Unity preparation')
        capture_project=record.get('project')
        if capture_project:
            capture_project=Path(capture_project)
            if not capture_project.is_absolute():capture_project=root/capture_project
            for scene in record.get('intendedScenes',[]):
                if (capture_project/scene).is_file():
                    reasons.append('a prepared native scene has actually been saved')
    native_sources=root/'unity/VideoEditing/Assets/VideoScenes'/batch['batchId']
    if native_sources.exists() and next(native_sources.rglob('*.unity'),None) is not None:
        reasons.append('saved native scenes exist in the source Unity project')
    state=media/'first-native-progress.json'
    if state.exists():
        record=read(state)
        if record.get('gpuStarted') or record.get('completed'):
            reasons.append('native worker has started production; preserve its progress')
    if reasons:
        raise RuntimeError('Preproduction integration refused before writes; '
                           'preserve generated/review/platform progress. '+
                           '; '.join(dict.fromkeys(reasons)))
    return {'projectsChecked':len(batch['projects']),'writes':0,
            'result':'draft-only integration allowed'}

def main():
    assert_preproduction_only()
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
    # Input validation can take time: recheck immediately before the first write.
    assert_preproduction_only()
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

def build_html(batch,rows,plans,cp,*,write_delivery=True):
    esc=html.escape
    cards=[];selected=cp.get('currentTopicId',cp.get('selectedFirstTopic'));current_status={}
    for row in rows:
        ident=row['topicId'];e=plans.get(ident);parts=''
        # This renderer may run after production begins. Show the existing
        # project draft when available, never roll its prose back to the
        # original planning bundle. All source JSON remains read-only.
        if row.get('narrationDraft'):
            draft=(ROOT/row['narrationDraft']).resolve()
            if draft.is_relative_to((ROOT/'projects').resolve()) and draft.is_file():
                current=read(draft)
                if current.get('topicId')==ident:e=current
        if e:
            for i,(ko,en) in enumerate(zip(e['narrationKo'],e['paragraphsEn']),1):
                parts+=f'<p><b>{i}.</b> {esc(ko)}</p><p class="en" lang="en">{esc(en)}</p>'
            gloss=' / '.join(g['english']+' ('+g['korean']+')' for g in e['glossary'] if isinstance(g,dict) and g.get('english') and g.get('korean'))
            parts+=f'<p class="terms">{esc(gloss)}</p>'
            body=f'<details><summary>대본 초안 · 한영 {len(e["narrationKo"])}문단</summary>{parts}<p class="note">아래는 대본·자료 기록입니다. 완성 영상의 재생·전체 청취·사용자 검수 완료를 뜻하지 않습니다.</p></details>'
        else:body='<p class="note">원문을 대조하며 대본 작성 중</p>'
        final=row.get('localFinalReview')
        if isinstance(final,dict) and all(final.get(key) for key in ('index','captioned','cover')):
            links={key:esc(Path(final[key]).resolve().as_uri(),quote=True) for key in ('index','captioned','cover')}
            player=(f'<div class="final-review"><p><a href="{links["index"]}">완성 검수본 열기</a> · '
                    f'<a href="{links["captioned"]}">전체 자막 MP4</a> · <a href="{links["cover"]}">썸네일</a></p>'
                    f'<video controls preload="none" playsinline src="{links["captioned"]}" poster="{links["cover"]}"></video></div>')
            body=player+body
        footage=('실제 장면 선택·확인' if row.get('footageStatus')=='selected-source-reviewed' else
                 '후보 장면 확인 · 채택 전' if row.get('footageStatus')=='candidate-reviewed-not-adopted' else '실제 장면 확보·검토 예정')
        stages=[footage]
        pilot=row.get('nativePilot')
        pilot_revision=(ident=='11.05' and isinstance(pilot,dict)
                        and not any(row.get(key) for key in ('nativeCaptureVerified','voiceGenerated','productionComplete'))
                        and pilot.get('capturedModes')==['construction']
                        and pilot.get('capturedCount')==1 and pilot.get('totalRequiredModes')==8
                        and pilot.get('structuralValidationPassed') is True
                        and pilot.get('allModesComplete') is False
                        and type(pilot.get('actualVisualReviewPassed')) is bool
                        and pilot.get('voicePreparationAllowed') is False
                        and all(isinstance(pilot.get(key),dict) and pilot[key].get('path')
                                and pilot[key].get('sha256') for key in ('evidence','sampledVisualReview')))
        revision=row.get('nativeRevision')
        remaining_modes_running=(pilot_revision and pilot['actualVisualReviewPassed'] is True
                                 and isinstance(revision,dict)
                                 and isinstance(revision.get('requestedModes'),list)
                                 and len(revision['requestedModes'])==8
                                 and all(isinstance(mode,str) for mode in revision['requestedModes'])
                                 and set(revision['requestedModes'])=={'construction','branches-a','branches-b','templates-a','templates-b','threats-a','threats-b','broken-link'}
                                 and revision.get('workerObservedAlive') is True
                                 and isinstance(revision.get('observedAt'),str) and bool(revision['observedAt'].strip())
                                 and isinstance(revision.get('workerSnapshot'),dict)
                                 and all(isinstance(revision['workerSnapshot'].get(key),str)
                                         and bool(revision['workerSnapshot'][key].strip()) for key in ('path','sha256')))
        if pilot_revision:
            stages.append('Unity 파일럿 1/8모드 촬영 · 표본 화면 확인' if pilot['actualVisualReviewPassed']
                          else 'Unity 파일럿 1/8모드 촬영 · 구조 검증 복구')
        elif row.get('nativeCaptureVerified'):
            stages.append('Unity 캡처 완료 · 표본 화면 확인' if row.get('nativeVisualQa') else 'Unity 캡처 완료 · 화면 검수 전')
        stage=str(row.get('status',''))
        repair=cp.get('firstS03LevelRepair',{}) if ident=='03.02' else {}
        if 'S03-only-level-repair-in-progress' in stage or 'S03-only-level-repair-in-progress' in str(repair.get('stage','')):
            stages.append('세 번째 문단 음량 보완 중')
            stages.append('새 음성 대조·최종 편집·전체 청취 전')
        elif row.get('voiceRepairQueued'):
            stages.append('원본 음성 보존 · 짧은 의미 단위로 음성 보완 작업 대기/진행')
            stages.append('새 음성 대조·최종 편집·전체 청취 전')
        elif row.get('productionComplete'):
            stages.append('로컬 완성본 제작 기록 있음')
        elif row.get('voiceGenerated'):
            stages.append('음성 생성 · 최종 편집·전체 청취 전')
        elif pilot_revision:
            stages.append('남은 7모드 제작 중 · 음성·최종 편집 전' if remaining_modes_running
                          else '남은 7모드 제작 전 · 음성·최종 편집 전' if pilot['actualVisualReviewPassed']
                          else '보행·시야 가림·테마 대비 보완 필요 · 음성·최종 편집 전')
        elif row.get('nativePreparation'):
            stages.append('Unity 소스 준비 · 실제 촬영·화면 검수 대기')
        elif row.get('nativeCaptureVerified'):
            stages.append('음성·최종 편집 진행 전')
        else:
            stages.append('대본 초안 · 시연·음성·완성본 제작 전')
        stages.append('사용자 검수 승인 기록 있음' if row.get('humanApproval') else '사용자 영상 검수 전')
        status=' · '.join(stages);current_status[ident]=status
        cards.append(f'<article data-ready="{int(bool(e))}" data-topic="{esc(ident)}"><p class="meta">제작 {row["order"]:03} · {ident} · {esc(row["chapterName"])} · 책 {esc(row["printPages"])}쪽</p><h2>{esc(row["title"])}</h2><p class="status">{esc(status)}</p>{body}</article>')
    out='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>레벨 디자인 111편 제작 현황 · 얌얌코딩</title><style>
*{box-sizing:border-box}body{margin:0;background:#101513;color:#f2f5ef;font:16px/1.75 "Malgun Gothic",sans-serif}main{max-width:970px;margin:auto;padding:28px 22px 80px}h1{font-size:32px;line-height:1.3}h2{font-size:21px;line-height:1.5;margin:7px 0}p{margin:9px 0}.summary{border-left:4px solid #ffdb79;padding-left:16px}.meta,.note,.en{color:#b8c5bf}.meta{font-size:14px}.status{font-size:14px;color:#ffdb79}article{padding:18px 0 25px;border-bottom:1px solid #435149}summary{cursor:pointer;color:#8de3c0;font-weight:bold}details>p{margin-top:16px}.en{font-size:15px;border-left:2px solid #42534b;padding-left:12px}.terms{font-size:14px}label{display:block;font-size:14px}input,select{font:inherit;color:white;background:#1b2820;border:1px solid #879a8e;padding:10px;border-radius:3px;max-width:100%}.filters{display:flex;gap:16px;flex-wrap:wrap}a{color:#8de3c0}#shown{font-size:14px;color:#b8c5bf}[hidden]{display:none!important}@media(max-width:500px){main{padding:18px 15px 50px}h1{font-size:27px}h2{font-size:20px}.filters>*{flex:1 1 140px}}
</style><main>'''
    out+='<style>body{word-break:keep-all;overflow-wrap:anywhere}.final-review video{display:block;width:100%;max-height:70vh;background:#000}</style><h1>레벨 디자인 111편 제작 현황</h1>'
    native_count=sum(bool(row.get('nativeCaptureVerified')) for row in rows)
    complete_count=int(cp.get('completedLocalReviewCount',0))
    first_status=current_status.get(selected,'현재 제작 상태를 확인하고 있습니다.')
    preserved=int(cp.get('previousCompletedVoiceVersionCount',0))
    history=(f' 이전 음성 {preserved}개 버전은 보존되어 있습니다.' if preserved else '')
    resource=(' 다른 작업의 GPU 사용이 끝나기를 기다리고 있습니다.'
              if cp.get('currentResourceConstraint') and not cp.get('firstVoiceWorker',{}).get('completed') else '')
    out+=f'<div class="summary"><p>선택한 주제 <b>{len(rows)}편</b> · 한영 대본 초안 <b>{cp["scriptDraftCount"]}편</b> · Unity 캡처 기록 <b>{native_count}편</b> · 완성 검수본 <b>{complete_count}편</b></p><p>실제 게임 현상 → 작동 원리 → 한 변수 비교 → 실제 게임 확인 순서로 제작합니다.</p><p>현재 선택 {esc(str(selected))}: {esc(first_status)}.{esc(history)}{esc(resource)}</p></div>'
    player_note=('완성 검수본은 해당 항목에서 재생하거나 검수 모음을 열 수 있습니다. 전체 청취·실시간 재생·사용자 최종 검수 여부는 각 검수 기록에서 확인하세요.'
                 if complete_count>0 else '아직 완성 영상 플레이어가 아닙니다. 실제 완성 MP4가 검증되면 그 파일과 한영 자막을 별도로 연결합니다.')
    out+=f'<p class="note">이 페이지는 제작·대본 현황입니다. {player_note} Google Drive·YouTube 업로드와 공개·예약은 실행하지 않았습니다.</p>'
    out+='<div class="filters"><label>검색<input id="q" placeholder="제목·기법·대본 검색"></label><label>상태<select id="stage"><option value="">전체 111편</option><option value="1">대본 초안 있음</option><option value="0">대본 작성 중</option></select></label></div><p id="shown"></p>'
    out+=''.join(cards)+r'''</main><script>const q=document.getElementById('q'),s=document.getElementById('stage');function filter(){let n=0;for(const a of document.querySelectorAll('article')){const ok=(!s.value||a.dataset.ready===s.value)&&q.value.toLowerCase().trim().split(/\s+/).every(t=>a.textContent.toLowerCase().includes(t));a.hidden=!ok;n+=ok}document.getElementById('shown').textContent=n+'편 표시'}q.oninput=s.onchange=filter;filter()</script></html>'''
    (HERE/'worklist.html').write_text(out,encoding='utf8')
    if write_delivery:
        delivery=MEDIA/'delivery';delivery.mkdir(exist_ok=True);(delivery/'index.html').write_text(out,encoding='utf8')

if __name__=='__main__':main()
