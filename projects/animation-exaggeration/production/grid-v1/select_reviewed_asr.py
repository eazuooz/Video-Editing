"""Select complete reviewed CPU recognition, preserving the failed GPU evidence."""
from pathlib import Path
import json, shutil
import audio_pipeline as ap
H=Path(__file__).resolve().parent
V=H.parent/'local/grid-v1/voice'
def main():
    ap.require_authorized('split')
    registration=ap.read(H/'source-asr-recovery-registration-v2.json')
    review_path=ap.repo_path(registration['review']['path'])
    assert ap.sha(review_path)==registration['review']['sha256']
    review=ap.read(review_path)
    assert review['all14ParagraphsRead'] and review['allCoreSentencesFound']
    assert review['coverage']['wordCount']==554 and review['coverage']['normalizedWordConcatenationEqualsFullRecognizedText']
    audio=V/'narration-source.wav';before=ap.sha(audio)
    assert before==registration['sourcePcm']['sha256']
    receipt=H/'source-asr-selection.json'
    assert not receipt.exists(),'Review existing selection; do not rewrite it.'
    archive=V/'prior-gpu-asr-v1';archive.mkdir(exist_ok=True)
    pairs=[('whole-source-asr.json','recoveredCandidate'),('whole-source-comparison.json','candidateComparison')]
    preserved=[];selected=[]
    for name,key in pairs:
        target=V/name;prior=next(x for x in registration['preservedPriorFiles'] if x['path']==ap.relative(target))
        candidate=ap.repo_path(registration[key]['path'])
        assert ap.sha(target)==prior['sha256'] and ap.sha(candidate)==registration[key]['sha256']
        copy=archive/name
        if copy.exists():assert ap.sha(copy)==prior['sha256']
        else:shutil.copyfile(target,copy)
        preserved.append(ap.artifact(copy))
        shutil.copyfile(candidate,target)
        assert ap.sha(target)==registration[key]['sha256']
        selected.append(ap.artifact(target))
    assert ap.sha(audio)==before
    ap.save(receipt,{'episode':'A02','status':'selected-reviewed-complete-CPU-word-timestamps',
        'createdAt':ap.now(),'review':ap.artifact(review_path),'preservedPrior':preserved,
        'selectedCanonical':selected,'sourceAudioSha256':before,'sourceAudioModified':False,
        'originalCpuCandidatesRetained':True,'actualHumanListening':False})
    ap.save(H/'source-asr-split-review.json',{
        'episode':'A02','audioSha256':before,'comparisonSha256':ap.sha(V/'whole-source-comparison.json'),
        'fullTextDirectlyCompared':True,'directReview':ap.artifact(review_path),
        'selection':ap.artifact(receipt),'notes':'Complete14paragraphs compared by delegated reviewer and root; core content intact. Numeral spelling and Korean homophones are alignment issues, not invented audio corrections.',
        'humanListening':False,'sourceAudioModified':False})
    print('Complete CPU words selected; old GPU files and continuous PCM preserved.')
if __name__=='__main__':main()
