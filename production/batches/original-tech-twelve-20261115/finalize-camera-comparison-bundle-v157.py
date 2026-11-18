"""Collect the new camera comparison and its actual technical evidence."""
from pathlib import Path
import json,hashlib,shutil
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-mario64-lakitu-camera';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CREDIT='Wholesome Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def main():
 base=M/P.name/'camera-music-v139/film-v154';out=base.parent/'local-review-v5';pp=base/'pilot-proof.json';pilot=read(pp);clean=read(base/'clean-proof.json');visual=read(base/'pilot-visual-review.json');assert visual['allowedForFinalBundle']and visual['pilotProof']['sha256']==pin(pp)['sha256']and pilot['fingerprint']==clean['fingerprint']
 for mode,v in [('pilot',pilot),('clean',clean)]:
  qa=read(base/(mode+'-encoded-qa.json'));assert qa['allAutomaticChecksPassed']and qa['video']==v['video']and qa['truePeakDbtp']<=-1.5
 derivative=read(base/'clean-derivative-verification.json');assert derivative['aacPacketsByteExact']and derivative['minimumBodyPsnrDb']>=42 and derivative['reservedCaptionBandIsBlack']
 mp=base.parent/'audio-mix-v150/audio-build.json';mix=read(mp);mixed=mp.parent/'mixed-content-review-v151.json';assert read(mixed)['approvedForRemux']
 selection=P/'production/accepted-voice-selection-v147.json';sel=read(selection);assert read(sel['technicalVoiceReview']['path'])['approvedForTechnicalDownstream'];caps=read(sel['captionTiming']['path']);voice=read(sel['voice']['path']);assert len(voice['identity']['reusedUnits'])==21 and len(voice['identity']['newEngineUnits'])==8
 previous=read(H/'local-final-review-manifest-v4.json')['projects'][1];old=previous['artifacts'];files=dict(captioned=pin(pilot['video']['path']),clean=pin(clean['video']['path']))
 for lang,meta,subs in [('ko','metadataKo','subtitlesKo'),('en','metadataEn','subtitlesEn')]:
  text=Path(old[meta]['path']).read_text('utf8');marker='\n\n자료:'if lang=='ko'else'\n\nReference:';assert marker in text and text.strip().endswith(CREDIT);tail=marker+text.split(marker,1)[1];tail=tail.rstrip()[:-len(CREDIT)].rstrip()
  source=('비교 영상: 바이오하자드2 원작(1998), PS5 클래식판 녹화. 마리오64(1996)보다 먼저 나온 게임이라는 뜻은 아닙니다. 최초의 게임 카메라라는 주장을 하지 않습니다.'if lang=='ko'else'Comparison footage: original Resident Evil2 (1998), recorded through the PS5 classic release. Super Mario64 (1996) came earlier. This video makes no first-ever game-camera claim.')
  sources='\n\n'+source+'\nWorld of Longplays · longplays.org · Spazbo4\nhttps://longplays.org/infusions/forum/viewthread.php?thread_id=16081\nhttps://archive.org/download/ps5-longplay-resident-evil-2-1998/PS5_Longplay_Resident_Evil_2_1998.mp4\nReuse conditions: https://longplays.org/infusions/faq/faq.php?cat_id=1\nMario64 release: https://www.nintendo.co.jp/wii/vc/vc_sm64/vc_mb_01.html\nResident Evil2 release: https://www.capcom.co.jp/ir/english/data/pdf/annual/2013/annual_2013_01.pdf'
  change=('배경음악은 음성에 맞춰 음량을 조절하고, 시작과 끝에 0.45초 페이드를 적용했습니다.'if lang=='ko'else'Music level adjusted under narration, with 0.45-second fades at the beginning and end.')
  title=text.splitlines()[0];paras=[' '.join(c[lang]for c in caps['cues']if c['paragraph']==para['id'])for para in voice['identity']['paragraphs']];target=out/('metadata-'+lang+'.txt');assert not target.exists();target.write_text(title+'\n\n'+'\n\n'.join(paras)+tail+sources+'\n\n'+change+'\n\n'+CREDIT+'\n','utf8');files[meta]=pin(target)
  target=out/('captions.'+lang+'.srt');assert not target.exists();shutil.copyfile(P/'production'/('captions-v147.'+lang+'.srt'),target);files[subs]=pin(target)
 evidence=[pp,base/'clean-proof.json',base/'pilot-visual-review.json',base/'pilot-encoded-qa.json',base/'clean-encoded-qa.json',base/'clean-derivative-verification.json',mp,mixed,selection,Path(sel['technicalVoiceReview']['path']),Path(sel['captionTiming']['path']),P/'planning/film-beats-comparison-v154.json',P/'planning/camera-comparison-source-review-v147.json']
 bundle=dict(slug=P.name,version='mario-re2-camera-comparison-v154-bgm150',titleKo=previous['titleKo'],durationSeconds=mix['durationSeconds'],artifacts=files,evidence=[pin(p)for p in evidence],localFinalBundleComplete=True,oldBundlePreserved=previous['bundle'],reusedApprovedUtterances=21,newComparisonUtterances=8,wholeSourceWordsPositive=True,gameSourceSpeed=1,originalGameAudioAdopted=False,originalRe2ClassicRecording=True,rightsAndInPictureCreditsVerified=True,releaseChronologyLabelled=True,musicMedianDbBelowVoice=mix['medianMusicMinusVoiceDb'],uniformMasterGain=mix['masterConstantGain'],actualFullListening=False,actualRealtimePlayback=False,humanApproval=False,platformActions=[])
 p=out/'bundle-v5.json';assert not p.exists();p.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(bundle=pin(p),duration=mix['durationSeconds'])))
if __name__=='__main__':main()
