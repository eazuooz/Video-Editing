"""Finalize exact12 local review artifacts only after real encoded/visual proofs."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');DROOT=ROOT/'shared/output/original-tech-twelve-20261115'
CREDIT='Wholesome Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/'
FOOTAGE={
 'PcL6zmz4GM8':('Royalty Free Game Clips','Journey / PS5'),
 'JxqdU3IKHoo':('Indian Samurais','Horizon Zero Dawn / PS5'),
 '9rwA7qvYnds':('PressStartPlay','INSIDE / Xbox'),
 '5Q4AfoUX1eU':('PressStartPlay','Marvel\'s Spider-Man Remastered / PC'),
 'TVfahIR7lYQ':('PressStartPlay','Control / Xbox Series S'),
 '8-OJj2JoPfQ':('NoHUD Gameplays','Returnal / PC recording'),
 '640-703':('Royalty Free Game Clips','Ratchet & Clank: Rift Apart / PS5'),
 '2tXXuiAU1Xs':('Generic Bomb','DOOM / 2016'),
 'HOoB7BtZDfE':('Generic Bomb','DOOM / 2016'),
 '3060-3130':('Archive64','The Legend of Zelda: Breath of the Wild / Cemu recording'),
 'npz4T7sznog':('Royalty Free Gameplay','Mario Kart 8 / hardware unconfirmed')}
URL_ID={'640-703':'aIfUk6AadK4','3060-3130':'kjSH8R2fk2c'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def bare(p):return {k:v for k,v in pin(p).items()if k!='bytes'}
def verify(row):assert pin(row['path'])['sha256']==row['sha256']
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);a=p.parse_args();assert a.project in[x['slug']for x in read(HERE/'batch.json')['projects']];slug=a.project;P=ROOT/'projects'/slug;bundle=MEDIA/slug/'final-review-v1'
 if(bundle/'bundle.json').exists():
  d=read(bundle/'bundle.json');assert d['localFinalBundleComplete'];[verify(x)for x in d['artifacts'].values()];print(json.dumps(dict(reusedExisting=True,bundle=pin(bundle/'bundle.json'))));return
 if slug in ['shorts-oot-ninja-show-z-targeting','shorts-mario64-lakitu-camera']:
  subprocess.run([sys.executable,'-u','-X','utf8',str(HERE/'finalize-local-bundle-v1.py'),'--project',slug],cwd=ROOT,check=True);return
 boundpath=P/('production/film-inputs-v33.json'if(P/'production/film-inputs-v33.json').exists()else'production/film-inputs-v27.json'if(P/'production/film-inputs-v27.json').exists()else'production/film-inputs-v25.json'if(P/'production/film-inputs-v25.json').exists()else'production/film-inputs-v10.json');bound=read(boundpath);base=MEDIA/slug/'film-v10';pp=base/'pilot-proof.json';cl=base/'clean-proof.json';pr=base/'pilot-visual-review.json';pq=base/'pilot-encoded-qa.json';cq=base/'clean-encoded-qa.json';pilot=read(pp);clean=read(cl);visual=read(pr);assert pilot['fingerprint']==clean['fingerprint'];assert visual['allowedForFinalBundle']and visual['pilotProof']==bare(pp)
 for proof,qa in [(pilot,read(pq)),(clean,read(cq))]:
  verify(proof['video']);assert qa['allAutomaticChecksPassed']and qa['video']==proof['video'];assert Path(proof['video']['path']).resolve().is_relative_to((DROOT/slug/'final-review-v1').resolve())
 cp=Path(bound['captionTiming']['path']);verify(bound['captionTiming']);captions=read(cp);vp=Path(captions['voice']['path']);vr=Path(captions['technicalVoiceReview']['path']);voice=read(vp);assert read(vr)['approvedForTechnicalDownstream'];mp=Path(bound['mixProofPath']);mix=read(mp);mr=mp.parent/'mixed-content-review.json';ml=mp.parent/'mixed-level-review-v1.json';assert read(mr)['approvedForPilot']and read(mr)['mixProof']==bare(mp)and not read(ml)['flags'];assert mix['frames']==voice['canonical']['frames']and mix['voiceGain']==1 and not mix['voiceDsp']and not mix['knownStemResidual']['exceedsKnownStemTolerance'];np=Path(bound['nativeFullProofPath']);nv=Path(bound['nativeVisualReviewPath']);assert read(np)['allPixelsRoundTripVerified']and read(nv)['allowedForFilm']and read(nv)['fullProof']==bare(np)
 meta=read(P/'publishing/metadata-draft-v1.json');sources=[]
 for beat in pilot['identity']['beats']:
  if beat['kind']=='game'and beat['source']['path']not in[x['path']for x in sources]:verify(beat['source']);sources.append(beat['source'])
 credits=[]
 for source in sources:
  key=next(k for k in FOOTAGE if k in Path(source['path']).name);who,version=FOOTAGE[key];credits.append(who+' — '+version+'\nhttps://www.youtube.com/watch?v='+URL_ID.get(key,key))
 assets=[];extra_evidence=[]
 if any(x in slug for x in ['spiderman','ratchet','doom']):assets.append('3D character: KayKit Adventurers — Kay Lousberg (CC0)\nhttps://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0')
 if'horizon'in slug:
  ap=P/'planning/asset-selection-v1.json';asset=read(ap);assets.append('Vegetation assets: '+asset['product']+' — '+asset['publisher']+'\n'+asset['publicProductUrl']);extra_evidence.append(ap)
 if'inside'in slug:
  assets.append('Temporal reprojection source: Playdead (MIT License)\nCopyright (c) <2015> <Playdead>\nhttps://github.com/playdeadgames/temporal');assert mix['originalGameAudioPaired']and mix['pairedFilmPlan']==bare(Path(bound['filmPlan']['path']));extra_evidence.append(Path(mix['identity']['pairedSourceClockProof']['path']))
 common='\n\nFootage:\n'+'\n\n'.join(credits)+('\n\n'+'\n\n'.join(assets)if assets else'')+'\n\n';ko='\n\n'.join(x['ko']for x in voice['identity']['paragraphs']);en='\n\n'.join(' '.join(c['en']for c in captions['cues']if c['paragraph']==para['id'])for para in voice['identity']['paragraphs'])
 ko+='\n\n자료: '+meta['technicalReference']+'\n실제 게임 녹화와 직접 만든 해설용 비교 장면을 함께 사용했습니다.'+common;en+='\n\nReference: '+meta['technicalReference']+'\nActual game recordings are shown alongside authored teaching comparisons.'+common
 if'inside'in slug:ko+='게임 소리는 해당 녹화의 영상과 같은 시각에 맞춰 사용하고 해설 아래로 음량을 조절했습니다.\n\n';en+='Game sound uses the same source clock as its matching recording, at a lower volume under commentary.\n\n'
 ko+='음악은 영상 길이에 맞춰 발췌하고 음량과 끝부분 페이드를 조절했습니다.\n\n'+CREDIT;en+='Music excerpted to match the video, with volume adjustment and an ending fade.\n\n'+CREDIT;files=dict(captioned=pin(pilot['video']['path']),clean=pin(clean['video']['path']));bundle.mkdir(parents=True,exist_ok=True);titleko=meta['titleKo'];titleen=meta['titleEn'].replace('Mario64','Mario 64').replace('Kart8','Kart 8')
 for lang,title,text in [('ko',titleko,ko),('en',titleen,en)]:
  assert text.strip().endswith(CREDIT);f=bundle/('metadata-'+lang+'.txt');assert not f.exists();f.write_text(title+'\n\n'+text+'\n','utf8');files['metadataKo'if lang=='ko'else'metadataEn']=pin(f);src=cp.parent/(cp.name.replace('caption-timing-','captions-').replace('.json','.'+lang+'.srt'));dest=bundle/('captions.'+lang+'.srt');assert not dest.exists();shutil.copyfile(src,dest);assert pin(src)['sha256']==pin(dest)['sha256'];files['subtitlesKo'if lang=='ko'else'subtitlesEn']=pin(dest)
 metapath=bundle/'metadata.json';save(metapath,dict(titleKo=titleko,titleEn=titleen,descriptionKo=ko,descriptionEn=en,technicalReference=meta['technicalReference'],footage=sources,localOnly=True,posted=False,humanApproval=False));evidence=[boundpath,pp,cl,pr,pq,cq,cp,vp,vr,mp,mr,ml,np,nv,metapath]+extra_evidence
 checks=dict(automatic=dict(size=[1080,1920],fps=60,videoFrames=pilot['actualVideoFrames'],bodyAudioFrames=mix['frames'],audioRate=24000,wholeWordCaptionCues=len(captions['cues']),decodedWordWindows=len(read(pq)['wordLevelWindows']),voiceGainAtMix=1,voiceDspAtMix=False,priorMasterProcessing=voice['identity'].get('processing'),sourceSpeed=1,knownStemResidualExact=True,originalGameAudioPaired=mix.get('originalGameAudioPaired',False)),technicalVisual=dict(encodedCaptionSamples=len(read(pq)['captionSamples']),displayWidth=375,approvedPilotReview=pin(pr),sourceNativeReview=pin(nv)),actualRealtimePlayback=False,actualFullListening=False,humanApproval=False)
 save(bundle/'bundle.json',dict(schemaVersion=2,slug=slug,version='film-v10-'+cp.stem+('-native-review-v25'if'horizon'in slug else''),localFinalBundleComplete=True,actualMixSeconds=mix['durationSeconds'],shortsDurationEligible=mix['durationSeconds']<=180,artifacts=files,evidence=[pin(f)for f in evidence],captionWordAnchorsReviewed=True,voiceTechnicalReviewPassed=True,mixedAsrContentReviewed=True,nativeVisualReviewPassed=True,encodedAudioVideoQaPassed=True,checks=checks,humanApproval=False,platformActions=[]));print(json.dumps(dict(bundle=pin(bundle/'bundle.json'),duration=mix['durationSeconds'],humanApproval=False)))
if __name__=='__main__':main()
