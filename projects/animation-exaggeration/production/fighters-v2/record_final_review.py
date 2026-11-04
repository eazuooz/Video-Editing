"""Record inspected encoded pixels and the bounded, non-listening audio review."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,numpy as np,soundfile as sf
import audio_pipeline as ap
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v2'
def main():
 stamp=datetime.now(timezone.utc).isoformat();q=ap.read(L/'edit/structural-verification.json');assert q['status']=='pass'
 source=L/'edit/animation-exaggeration-captioned.mp4';digest=ap.sha(source)
 assert digest==q['outputs']['captioned']['sha256']
 files=[p for pat in ['scenes-*.jpg','captions-*.jpg','*-mobile.png'] for p in sorted((L/'qa/final').glob(pat))]
 files += [L/'qa/final'/name for name in ['A02-F23-fhd.png','A02-F32-fhd.png','intro.png','outro.png','sol-horizontal.png']]
 assert len(files)==23 and all(p.exists() for p in files)
 ap.save(H/'final-pixel-review.json',{'status':'sampled-pixels-reviewed','reviewedAt':stamp,'master':ap.artifact(source),'sceneMidpointsReviewed':41,'captionMidpointsReviewed':132,'mobileWidth':375,'mobileSamplesReviewed':6,'fullResolutionDetailedSamples':['A02-F23','A02-F32'],'additionalSamples':['branding','membership outro','Sol horizontal swing at100.4s'],'artifacts':[ap.artifact(p) for p in files],'findings':['KOF and Guilty Gear independent FHD gameplay visibly included with original aspect and HUD/watermark.','Horizontal and rising attacks match the revised Sol passage.','Three short arrows point to preparation/raised arm/rising direction and stay above the fixed caption zone.','All132 caption samples render without clipping; retained Unity comparisons remain legible.','Game intro and membership end retained; no coaching TTS added.'],'blockingFindings':[],'fullContinuousHumanViewing':False,'humanUserReview':False})
 annotation=ap.read(H/'annotation-review.json');annotation['finalPixelReview']='Reviewed actual encoded F31/F32/F23 at FHD and375px; details final-pixel-review.json';ap.save(H/'annotation-review.json',annotation)
 audio=ap.read(H/'final-audio-asr-review.json')
 old,sr=sf.read(H.parent/'local/grid-v1/edit/narration-stem.wav',dtype='int32',always_2d=True)
 new,nsr=sf.read(L/'edit/narration-stem.wav',dtype='int32',always_2d=True);assert sr==nsr==48000
 inserts=ap.read(H/'narration-insert-map.json')['inserts'];proof=[];start=0;offset=0
 for ins in inserts:
  end=ins['originalAtFrame']*800
  assert np.array_equal(old[start:end],new[start+offset:end+offset])
  proof.append({'oldSamples':[start,end],'newStartSample':start+offset,'equal':True});start=end;offset+=ins['frames']*800
 assert np.array_equal(old[start:],new[start+offset:start+offset+len(old)-start])
 proof.append({'oldSamples':[start,len(old)],'newStartSample':start+offset,'equal':True})
 audio.update(fullRecognizedTextRead=True,all17ParagraphsReviewed=True,sourcePcmRetention=proof,sourceAndFinalSpeechSpeed=1,semanticReview={'missingMeaningfulSentences':[],'differences':['Game title transliteration and spacing: 킹오프파이터스15 corresponds to spoken 킹 오브 파이터즈 피프틴.','Number transcription0/100/110/10cm corresponds to spoken 영/백/백십/십 센티미터.','같/갖, 의/에, 맡/맞 are ASR orthography substitutions.'],'duplicateAsrPassage':{'rangeSeconds':[171,177.04],'finding':'Chunk aggregation repeats the same lifting-arm words at the same backward-jumping timestamps171–177; not a second recording in the timeline. The retained original PCM interval is exactly equal once and captions place the sentence once.','waveformRepetitionAdded':False}},actualListeningPerformed=False,finalListeningStatus='User contextual listening remains pending; ASR and PCM verification do not establish human listening.',reviewedAt=stamp)
 ap.save(H/'final-audio-asr-review.json',audio)
 print(json.dumps({'pixels':len(files),'captions':132,'unchangedOriginalPcmSegments':len(proof),'coverage':audio['matchedCharacterCoverage']}))
if __name__=='__main__':main()
