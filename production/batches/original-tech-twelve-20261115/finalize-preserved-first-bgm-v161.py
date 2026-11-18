"""Finish only the first file's ledger after its already passed encoded QA."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');slug='shorts-oot-ninja-show-z-targeting'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
 base=M/slug/'camera-music-v139/remux-v152';out=base/'local-review-v5';qp=base/'encoded-audio-and-picture-equivalence-v155.json';qa=read(qp);row=next(x for x in read(H/'audible-bgm-baseline-bindings-v144.json')['projects']if x['order']==1);mp=base.parent/'audio-mix-v144/audio-build.json';mix=read(mp);assert qa['allAutomaticChecksPassed']and qa['compressedVideoAndPtsUnchanged']and qa['aacPacketsByteExact']and qa['truePeakDbtp']<=-1.5
 assert pin(qa['captioned']['path'])==qa['captioned']and pin(qa['clean']['path'])==qa['clean']
 files=dict(captioned=qa['captioned'],clean=qa['clean'],metadataKo=pin(out/'metadata-ko.txt'),metadataEn=pin(out/'metadata-en.txt'),subtitlesKo=pin(out/'captions.ko.srt'),subtitlesEn=pin(out/'captions.en.srt'))
 for field in ['subtitlesKo','subtitlesEn']:assert files[field]['sha256']==row['baseline']['artifacts'][field]['sha256']
 for field in ['metadataKo','metadataEn']:assert Path(files[field]['path']).read_text('utf8').strip().endswith('http://creativecommons.org/licenses/by/4.0/')
 b=dict(slug=slug,version='audible-bgm-v155-preserved-encode',titleKo=(out/'metadata-ko.txt').read_text('utf8').splitlines()[0],durationSeconds=mix['durationSeconds'],artifacts=files,evidence=[pin(qp),pin(mp),pin(mp.parent/'mixed-content-review-v149.json'),pin(base/'captioned-remux.log'),pin(base/'clean-remux.log')],localFinalBundleComplete=True,oldBundlePreserved=row['baseline']['bundle'],unchangedApprovedVoiceRawPcm=True,uniformMasterGain=mix['masterConstantGain'],internalNarrationEnvelopeChanged=False,videoPacketsAndCaptionFilesUnchanged=True,musicMedianDbBelowVoice=mix['medianMusicMinusVoiceDb'],completedEncodedWorkRepeated=False,actualFullListening=False,actualRealtimePlayback=False,humanApproval=False,platformActions=[])
 p=out/'bundle-v5.json';assert not p.exists();p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(bundle=pin(p),encoderRerun=False)))
if __name__=='__main__':main()
