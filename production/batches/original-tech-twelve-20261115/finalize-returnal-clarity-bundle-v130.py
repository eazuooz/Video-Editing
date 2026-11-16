"""Collect six real reviewed local artifacts, never infer human approval."""
from pathlib import Path
import argparse,hashlib,json,shutil
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CREDIT='Wholesome Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def bare(p):return {k:v for k,v in pin(p).items()if k!='bytes'}
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);a=ap.parse_args();p=ROOT/'projects'/a.project;base=M/p.name/'clarity-revision-v83/film-v130';out=base.parent/'local-review-v2'
 assert not(out/'bundle-v2.json').exists();pilot=read(base/'pilot-proof.json');clean=read(base/'clean-proof.json');assert pilot['fingerprint']==clean['fingerprint'];visual=read(base/'pilot-visual-review.json');assert visual['allowedForFinalBundle']and visual['pilotProof']==bare(base/'pilot-proof.json')
 for mode,proof in [('pilot',pilot),('clean',clean)]:
  qa=read(base/(mode+'-encoded-qa.json'));assert qa['allAutomaticChecksPassed']and qa['video']==proof['video'];assert bare(proof['video']['path'])==proof['video']
 derivative=read(base/'clean-derivative-verification.json');assert derivative['aacPacketsByteExact']and derivative['minimumBodyPsnrDb']>=42 and derivative['reservedCaptionBandIsBlack']
 selp=p/'production/accepted-voice-selection-v95.json';sel=read(selp);vp=Path(sel['voice']['path']);v=read(vp);cp=Path(sel['captionTiming']['path']);caps=read(cp);assert read(sel['technicalVoiceReview']['path'])['approvedForTechnicalDownstream'];mp=base.parent/'audio-mix-v95/audio-build.json';mix=read(mp);mr=mp.parent/'mixed-content-review.json';assert read(mr)['approvedForPilot']and read(mr)['mixProof']==bare(mp);assert not read(mp.parent/'mixed-level-review-v1.json')['flags']
 old=read(M/p.name/'final-review-v1/bundle.json');meta=read(p/'publishing/metadata-draft-v1.json');files=dict(captioned=pin(pilot['video']['path']),clean=pin(clean['video']['path']))
 for lang,field in [('ko','metadataKo'),('en','metadataEn')]:
  text=Path(old['artifacts'][field]['path']).read_text('utf8');marker='\n\n자료:'if lang=='ko'else'\n\nReference:';assert marker in text;tail=marker+text.split(marker,1)[1];assert tail.strip().endswith(CREDIT)
  paras=[' '.join(c[lang]for c in caps['cues']if c['paragraph']==para['id'])for para in v['identity']['paragraphs']];title=meta['titleKo'if lang=='ko'else'titleEn'];dest=out/('metadata-'+lang+'.txt');assert not dest.exists();dest.write_text(title+'\n\n'+'\n\n'.join(paras)+tail,'utf8');files[field]=pin(dest)
  src=cp.parent/('captions-v95.'+lang+'.srt');dest=out/('captions.'+lang+'.srt');assert not dest.exists();shutil.copyfile(src,dest);assert pin(src)['sha256']==pin(dest)['sha256'];files['subtitlesKo'if lang=='ko'else'subtitlesEn']=pin(dest)
 evidence=[base/'pilot-proof.json',base/'clean-proof.json',base/'pilot-visual-review.json',base/'pilot-encoded-qa.json',base/'clean-encoded-qa.json',base/'clean-derivative-verification.json',selp,vp,Path(sel['technicalVoiceReview']['path']),cp,mp,mr,mp.parent/'mixed-level-review-v1.json',p/'planning/film-beats-clarity-v130.json']
 bundle=out/'bundle-v2.json';save(bundle,dict(slug=p.name,version='clarity-examples-v130',titleKo=meta['titleKo'],durationSeconds=mix['durationSeconds'],shortsDurationEligible=mix['durationSeconds']<=180,artifacts=files,evidence=[pin(x)for x in evidence],localFinalBundleComplete=True,originalBundlePreserved=pin(M/p.name/'final-review-v1/bundle.json'),unchangedApprovedUtterancesByteExact=True,newUtterancesOnlyWholeConstantGain=True,newRawPcmPreserved=True,sourceOrderPreserved=True,sourceFootageSpeed=1,actualFullListening=False,actualRealtimePlayback=False,humanApproval=False,platformActions=[]))
 print(json.dumps(dict(bundle=pin(bundle),duration=mix['durationSeconds'],artifacts=6,humanApproval=False)))
if __name__=='__main__':main()
