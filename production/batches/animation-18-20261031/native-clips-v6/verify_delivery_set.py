"""Verify exact final files, caption clocks and unchanged narration ownership."""
from pathlib import Path
import subprocess
from prepare import HERE,WORK,OUTPUT,read,save
from finish_episode import sha
from assemble_delivery import srt

def main():
    rows=[]
    for selected in read(HERE/'plan.json')['episodes']:
        ep=selected['id'];delivery=read(OUTPUT/ep/'delivery.json')
        assert delivery['frames']==selected['baseline']['frames']+600
        assert delivery['summaryFrames']==600 and delivery['sourcePcmOutsideSummaryUnchanged']
        assert not delivery['humanReviewed'] and not delivery['platformChanged']
        files={r['kind']:r for r in delivery['files']}
        assert set(files)=={'clean.mp4','captioned.mp4','ko.srt','en.srt'}
        for kind,row in files.items():
            assert sha(Path(row['path']))==row['sha256'],(ep,kind,'changed delivered file')
            if kind.endswith('.mp4'):assert row['fullDecode']=='passed'
            else:
                cues=srt(Path(row['path']))
                assert cues and all(0<=a<b<=delivery['durationSeconds']+.001 for a,b,t in cues)
                assert all(x[1]<=y[0]+.002 for x,y in zip(cues,cues[1:])),(ep,kind,'caption overlap')
        final=read(WORK/ep/'encoded-final-check/evidence.json')
        assert final['captionedMasterSha256']==files['captioned.mp4']['sha256']
        audio_hashes=[subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',files[k]['path'],
             '-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).decode().strip()
             for k in ('clean.mp4','captioned.mp4')]
        assert audio_hashes[0]==audio_hashes[1],(ep,'clean/captioned audio mismatch')
        rows.append({'episode':ep,'captionedMasterSha256':files['captioned.mp4']['sha256'],
                     'summaryFrames':600,'durationSeconds':delivery['durationSeconds'],
                     'fullDecodeBothMasters':'passed','captionClocks':'passed',
                     'identicalAacPayload':audio_hashes[0],
                     'encodedRecapAudioSimilarity':final['encodedSummaryAudioSimilarity'],
                     'internalSampleReviewPending':delivery['visualReviewPending'],'humanReviewed':False})
    save(HERE/'delivery-review-manifest.json',{'revision':'native-clips-v6','episodes':rows,
         'uploadedEpisodesExcluded':['A01','A02'],'preservedStudy':'A06',
         'reviewUrl':'http://127.0.0.1:9300/','outputFolder':str(OUTPUT),
         'platformChanged':False,'humanReviewed':False})
    print('Verified',len(rows),'complete four-file deliveries.')

if __name__=='__main__':main()
