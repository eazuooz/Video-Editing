from pipeline import *
import html, argparse, re
D=L/'delivery/output/animation-exaggeration'
def deliver():
 plan=read(H/'edit-plan.json');q=read(L/'edit/structural-verification.json');assert q['status']=='pass' and q['identicalContinuousAudio']
 asr=read(H/'final-audio-asr-review.json');assert asr['matchedCharacterCoverage']>.95
 pixels=read(H/'final-pixel-review.json');assert pixels['status']=='sampled-pixels-reviewed'
 D.mkdir(parents=True,exist_ok=True);files=[]
 for role in ['captioned.mp4','clean.mp4','ko.srt','en.srt']:
  source=L/('edit/animation-exaggeration-'+role if role.endswith('.mp4') else 'edit/captions.'+role);dest=D/('animation-exaggeration.'+role)
  copy_verified(source,dest);files.append(dict(artifact(dest),role=role,name=dest.name))
 secs=plan['totalFrames']/60;sec=round(secs);now=datetime.datetime.now(datetime.timezone.utc).isoformat(); cap=files[0]
 baseline=O/'delivery/output/animation-exaggeration/animation-exaggeration.captioned.mp4'
 assert sha(baseline)==read(H/'authorization.json')['preservation']['captionedMasterSha256']
 m={'episode':'A02','slug':P.name,'revision':V,'status':'local-delivery-user-review-pending','createdAt':now,'directory':rel(D),'format':{'width':1920,'height':1080,'fps':60,'frames':plan['totalFrames'],'durationSeconds':secs},'files':files,'captionedMasterSha256':cap['sha256'],'verification':{'structuralFinalPair':'pass','sampledEncodedPixels':pixels['status'],'encodedSpeechCoverage':asr['matchedCharacterCoverage'],'humanFinalViewingAndListening':False},'measuredBodySharePercent':{k:round(n*100/plan['bodyFrames'],2) for k,n in plan['measuredScreenTime'].items()},'baselinePreserved':artifact(baseline),'platformMutation':False}
 save(D/'delivery-manifest.json',m)
 by={c['id']:c for c in plan['cuts']};beats=read(H/'analysis-beats.json')
 links=''.join(f'<li><a href="{f["name"]}" download>{name}</a> · {f["bytes"]/1e6:.1f} MB</li>' for name,f in zip(['한글 자막 영상','자막 없는 영상','한글 SRT','English SRT'],files))
 buttons=''.join(f'<button data-t="{by[cid]["startFrame"]/60:.4f}">{name}</button>' for cid,name in [('A02-F11',beats['moves'][0]['chapter']),('A02-F21',beats['moves'][1]['chapter']),('A02-E015','언리얼 · 손목 이동 1.0배 / 1.8배'),('A02-F31',beats['moves'][2]['chapter'])])
 page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A02 · 쿨라와 리리의 동작</title><style>body{{margin:0;background:#0b0d0b;color:#f5f4ee;font:17px/1.65 'Malgun Gothic',sans-serif}}main{{max-width:1120px;margin:30px auto;padding:0 20px 48px}}.brand,a{{color:#e8cf83}}h1{{font-size:clamp(23px,4vw,31px);line-height:1.35}}video{{width:100%;aspect-ratio:16/9;background:#000}}small{{color:#bec4b8;overflow-wrap:anywhere}}button{{color:#fff;border:1px solid #6a705e;background:transparent;padding:8px 12px;margin:3px;font:inherit;cursor:pointer}}</style><main><div class="brand">얌얌코딩 · 애니메이션 A02</div><h1>동작의 과장 | 게임 캐릭터는 왜 현실보다 과장되게 움직일까?</h1><p>1920×1080 · 60fps · {sec//60}분 {sec%60}초</p><video id="m" controls playsinline preload="metadata" src="{cap['name']}"></video><p><a href="{cap['name']}">전체 자막 영상 열기</a></p><p>{buttons}</p><p>빨간 네모가 나타나면 바로 앞에서 본 동작을 0.25배로 다시 보고 있는 구간입니다. 네모는 캐릭터의 자세를 짚어 주는 편집 표시입니다. 언리얼 비교에서는 카메라와 재생 속도를 고정하고 손목이 이동하는 거리를 30cm와 54cm로 나눴습니다.</p><ul>{links}</ul><details><summary>검수 기록과 출처</summary><a href="sources.txt">영상·음악 출처</a> · <a href="delivery-manifest.json">파일 기록</a><p><small>마스터 SHA256: {cap['sha256']}</small></p></details></main><script>document.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{{m.currentTime=+b.dataset.t;m.play()}})</script></html>'''
 (D/'index.html').write_text(page,encoding='utf-8')
 sources='영상 출처 · 더보기 제일 아래용\n\n'+(H/'sources/description-bottom.txt').read_text(encoding='utf-8').strip()+'\n\n'
 tail=(O/'delivery/output/animation-exaggeration/sources.txt').read_text(encoding='utf-8').split('Kirby Needle evolution',1)[1]
 (D/'sources.txt').write_text(sources+'Kirby Needle evolution'+tail,encoding='utf-8')
 ledger={'episode':'A02','revision':V,'status':m['status'],'updatedAt':now,'directory':rel(D),'index':rel(D/'index.html'),'captioned':cap,'files':files,'manifest':artifact(D/'delivery-manifest.json'),'sourcePlan':artifact(H/'edit-plan.json'),'qa':{'structure':artifact(L/'edit/structural-verification.json'),'pixels':artifact(H/'final-pixel-review.json'),'audio':artifact(H/'final-audio-asr-review.json')},'humanFinalReview':False,'platformMutation':False,'baselinePreserved':m['baselinePreserved']}
 ledger['qa']['nativeUnrealCompressedAssetMeasurements']=artifact(H/'unreal-stage/ue-evaluated-amplitude.json')
 ledger['qa']['unrealMotionPixels']=artifact(H/'unreal-stage/encoded-motion-evidence.json');ledger['qa']['unrealJointPixels']=artifact(H/'unreal-stage/joint-pixel-review.json')
 save(H/'local-delivery-ledger.json',ledger);save(H/'checkpoint.json',{'episode':'A02','revision':V,'status':m['status'],'updatedAt':now,'index':rel(D/'index.html'),'localCaptionedMaster':cap['path'],'captionedMasterSha256':cap['sha256'],'durationSeconds':secs,'durationFrames':plan['totalFrames'],'screenTime':plan['measuredScreenTime'],'nativeThenIdenticalQuarterSpeed':True,'previousReviewPreserved':m['baselinePreserved'],'originalSpeechRetention':'14 preserved paragraphs and newly voiced local Qwen fighter inserts; identical old source sample ranges','userReview':'pending: watch and listen to this exact hash','publishState':'local only','platformMutation':False})
 cp=read(H/'checkpoint.json');cp['nativeUnrealCompressedAssetMeasurements']=ledger['qa']['nativeUnrealCompressedAssetMeasurements'];cp['nativeUnrealSummary']='Six new Game Animation Sample pairs. Evaluated wrist travel ratio ~1.800000, fixed left shoulder, same camera and time.';save(H/'checkpoint.json',cp)
 manifest=read(P/'project.json')
 if manifest['revision']!=V:
  assert manifest['revision']=='fighters-v3';manifest['preservedDeliveries'].append({'revision':'fighters-v3','delivery':manifest['delivery']})
 manifest.update(revision=V,status=m['status'],updatedAt=now,publishReady=False)
 manifest['editing'].update(measuredBodyGameplayShare=plan['expectedGameplayShare'],measuredBodyExplanationShare=1-plan['expectedGameplayShare'],ratioChoiceRecord=rel(H/'ratio-choice.json'),scenePlan=rel(H/'edit-plan.json'))
 manifest['voice'].update(additionalGeneration=artifact(H/'qwen-voice-record.json'),finalEncodedAudioReview=artifact(H/'final-audio-asr-review.json'))
 manifest['delivery']={'status':'four-outputs-complete','directory':rel(D),'manifest':rel(D/'delivery-manifest.json'),'captionedMasterSha256':cap['sha256']}
 save(P/'project.json',manifest)
 own=[P/'project.json',*sorted(S.glob('*')),*sorted(f for f in H.rglob('*') if '__pycache__' not in f.parts and f.suffix not in ('.pyc','.mp4','.wav'))]
 save(H/'owned-paths.json',{'status':'final-delivered','paths':sorted(set(rel(p) for p in own if p.is_file())|{rel(H/'owned-paths.json')})})
 print(json.dumps(m,ensure_ascii=False,indent=2))
if __name__=='__main__':deliver()
