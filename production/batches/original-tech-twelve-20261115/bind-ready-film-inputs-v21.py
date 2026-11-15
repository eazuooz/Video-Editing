"""Bind exact accepted voice/captions; pending native paths remain pending."""
from pathlib import Path
import argparse,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);a=p.parse_args();contract=next(x for x in read(HERE/'source-ordered-film-contracts-v21.json')['projects']if x['slug']==a.project);P=ROOT/'projects'/a.project;sp=P/'production/accepted-voice-selection-v10.json';selected=read(sp);assert read(selected['technicalVoiceReview']['path'])['approvedForTechnicalDownstream'];captions=read(selected['captionTiming']['path']);plan=read(contract['plan']['path']);assert plan['semanticClauses']==captions['clauses'];out=P/'production/film-inputs-v10.json';assert not out.exists();out.write_text(json.dumps(dict(voiceSelection=pin(sp),captionTiming=selected['captionTiming'],filmPlan=contract['plan'],mixProofPath=contract['mixProofPath'],nativeFullProofPath=contract['nativeFullProofPath'],nativeVisualReviewPath=contract['nativeVisualReviewPath'],nativeFullFrames=contract['nativeFullFrames'],actualNativeFullReady=False),ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(pin(out)))
if __name__=='__main__':main()
