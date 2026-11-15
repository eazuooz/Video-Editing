"""Record a separate observed technical review after opening actual375px samples."""
from pathlib import Path
import argparse,hashlib,json
H=Path(__file__).resolve().parent;M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--notes-file',type=Path,required=True);a=p.parse_args();assert a.project in[x['slug']for x in read(H/'batch.json')['projects']];base=M/a.project/'film-v10';pilot=base/'pilot-proof.json';qa=base/'pilot-encoded-qa.json';d=read(qa);notes=read(a.notes_file);assert d['allAutomaticChecksPassed']and d['renderProof']==pin(pilot);assert notes['project']==a.project and notes['actualEncodedSamplesInspected']==len(d['captionSamples']);assert notes['findings']and notes['allCaptionSamplesOpened']and notes['sourceOrderAndAspectReviewed']and notes['captionMarginsAndSubjectVisibilityReviewed'];out=base/'pilot-visual-review.json';assert not out.exists()
 for x in d['captionSamples']:assert pin(Path(x['path']))==x
 r=dict(pilotProof=pin(pilot),encodedQa=pin(qa),actualEncodedSamplesInspected=len(d['captionSamples']),displayWidth=375,captionSamples=d['captionSamples'],findings=notes['findings'],observationNotes=pin(a.notes_file),allowedForFinalBundle=True,actualRealtimePlayback=False,actualFullListening=False,humanApproval=False)
 out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(pin(out)))
if __name__=='__main__':main()
