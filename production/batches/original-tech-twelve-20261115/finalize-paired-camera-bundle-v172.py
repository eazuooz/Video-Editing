"""Collect only the requested second video's paired-camera revision."""
from pathlib import Path
import json,hashlib,shutil
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-mario64-lakitu-camera';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CREDIT='Wholesome Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/'
TITLE='3D 게임의 판도를 바꾼 마리오64'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def main():
 base=M/P.name/'camera-paired-v164/film-v171';out=base.parent/'local-review-v6-r171';pilot=read(base/'pilot-proof.json');clean=read(base/'clean-proof.json');visual=read(base/'pilot-visual-review.json');assert pilot['fingerprint']==clean['fingerprint']and visual['allowedForFinalBundle']and visual['pilotProof']['sha256']==pin(base/'pilot-proof.json')['sha256']
 for mode,v in [('pilot',pilot),('clean',clean)]:
  qa=read(base/(mode+'-encoded-qa.json'));assert qa['allAutomaticChecksPassed']and qa['encodedAudioPacketsByteExact']and qa['video']==v['video']
 derived=read(base/'clean-derivative-verification.json');assert derived['aacPacketsByteExact']and derived['reservedCaptionBandIsBlack']and derived['minimumBodyPsnrDb']>=42
 fixed=base.parent/'native-v166/accepted-full.json';fv=fixed.parent/'full-visual-review-v167.json';assert read(fv)['allowedForFilm']and read(fixed)['framesPerCamera']==720 and read(fixed)['allPixelsRoundTripVerified']
 old=read(H/'local-final-review-manifest-v5.json')['projects'][1];files=dict(captioned=pin(pilot['video']['path']),clean=pin(clean['video']['path']))
 for lang,meta,subs,title in [('ko','metadataKo','subtitlesKo',TITLE),('en','metadataEn','subtitlesEn','Super Mario 64 Changed 3D Gaming')]:
  text=Path(old['artifacts'][meta]['path']).read_text('utf8');assert text.strip().endswith(CREDIT);body=text.split('\n',1)[1].lstrip('\n').rstrip()[:-len(CREDIT)].rstrip()
  note=('Unity 좌우 비교: 같은 캐릭터와 장면에 고정 구도와 시점 조작을 적용한 자체 제작 시연입니다. 카메라 위치와 구역 경계는 설명용으로 정했으며 상용 게임의 원본 구현이 아닙니다.'if lang=='ko'else'Unity comparison: an authored fixed-shot camera and player-controlled camera use the same actor and world. Example poses and zone boundaries illustrate the principle, rather than reproduce either commercial game engine.')
  p=out/('metadata-'+lang+'.txt');assert not p.exists();p.write_text(title+'\n\n'+body+'\n\n'+note+'\n\n'+CREDIT+'\n','utf8');files[meta]=pin(p)
  p=out/('captions.'+lang+'.srt');assert not p.exists();shutil.copyfile(old['artifacts'][subs]['path'],p);files[subs]=pin(p);assert files[subs]['sha256']==old['artifacts'][subs]['sha256']
 evidence=[base/'pilot-proof.json',base/'clean-proof.json',base/'pilot-visual-review.json',base/'pilot-encoded-qa.json',base/'clean-encoded-qa.json',base/'clean-derivative-verification.json',fixed,fv,Path(read(fixed)['pairedStateComparison']['path']),P/'planning/film-beats-paired-v171.json',H/'user-camera-paired-revision-v164.json']
 b=dict(slug=P.name,version='mario-title-and-paired-fixed-camera-v171',titleKo=TITLE,durationSeconds=93.2,artifacts=files,evidence=[pin(p)for p in evidence],localFinalBundleComplete=True,previousBundle=old['bundle'],nativeFixedModes=5,nativeFramesPerMode=720,sameActorModelStatesCompared=3600,actualNewUnityCapture=True,simultaneousActualGameAndNativeComparisons=True,sourceAspectsPreserved=True,sourceSpeed=1,acceptedVoiceMusicAndAacByteExact=True,subtitlesByteExact=True,actualFullListening=False,actualRealtimePlayback=False,humanApproval=False,platformActions=[])
 p=out/'bundle-v6.json';assert not p.exists();p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(bundle=pin(p),title=TITLE,duration=93.2)))
if __name__=='__main__':main()
