"""Record only actually inspected final pixels; human listening stays pending."""
from pathlib import Path
import datetime,numpy as np,soundfile as sf
import audio_pipeline as ap
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3'
def main():
 q=ap.read(L/'edit/structural-verification.json');assert q['status']=='pass';p=ap.read(H/'edit-plan.json')
 master=L/'edit/animation-exaggeration-captioned.mp4';assert ap.sha(master)==q['outputs']['captioned']['sha256']
 extraction=ap.read(L/'qa/final/extraction.json');files=sorted((L/'qa/final').glob('*.jpg'))+sorted((L/'qa/final').glob('*mobile.png'))
 assert extraction['cutMidpoints']==43 and extraction['captionMidpoints']==131
 ap.save(H/'final-pixel-review.json',{'status':'sampled-pixels-reviewed','reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'master':ap.artifact(master),'sceneMidpointsReviewed':43,'captionMidpointsReviewed':131,'mobileWidth':375,'artifacts':[ap.artifact(f) for f in files],'findings':['Large native Unreal sample mannequins replace the six humanoid explanation cuts.','Left shoulder fixed, right shoulder/chest move with the same local hand target; pose-derived guides visibly align.','Shermie and Giovanna appear at native speed before labeled0.25x analysis. Red hollow guides follow the observed body regions; short labels stay in the left gutter.','Fixed white captions, gray animation grid, black header/footer, original branding/member end and channel BGM retained.'],'fullHumanViewingAndListening':False})
 voice,sr=sf.read(L/'edit/narration-stem.wav',dtype='float32',always_2d=True);old,rate=sf.read(H.parent/'local/grid-v1/edit/narration-stem.wav',dtype='float32',always_2d=True);assert sr==rate==48000
 inserts=ap.read(H/'narration-insert-map.json')['inserts'];previous=offset=0;proof=[]
 for row in inserts:
  end=row['originalAtFrame']*800;assert np.array_equal(old[previous:end],voice[previous+offset:end+offset])
  proof.append({'oldSamples':[previous,end],'newStartSample':previous+offset,'exactEquality':True});previous=end;offset+=row['frames']*800
 assert np.array_equal(old[previous:],voice[previous+offset:]);proof.append({'oldSamples':[previous,len(old)],'newStartSample':previous+offset,'exactEquality':True})
 a=ap.read(H/'final-audio-asr-review.json');a.update(sourcePcmRetention=proof,all17ParagraphsTextReviewed=True,actualListeningPerformed=False,reviewNotes={'fullAacUnpromptedAsrCoverage':a['matchedCharacterCoverage'],'numbers':'Source/final PCM is identical for the0→100→110→100cm worked example. ASR writes numbers as digits.','asrChunkJoin':'The duplicate phrase around305.58–309.80s repeats with backward timestamps in the ASR result. It is not an extra inserted voice interval; exact original PCM retained once.','pendingListening':'Contextual pronunciation of 셸미/길티기어 and the voice transition remain part of final human listening; automated transcription does not certify these.'})
 ap.save(H/'final-audio-asr-review.json',a)
 print('Final inspected-pixel and exact original-PCM retention evidence recorded')
if __name__=='__main__':main()
