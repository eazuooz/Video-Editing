"""Reuse completed A01's local-only assembly/delivery checks for this A02 revision."""
from pathlib import Path
import hashlib,json

H=Path(__file__).resolve().parent
R=H.parents[3]
SOURCE=R/'projects/animation-assigning/production/grid-v1'

def main():
    records=[]
    for name in ('finalize_video.py','render_ready_cuts.py','extract_final_review.py','build_delivery.py'):
        src=SOURCE/name; dst=H/name
        text=src.read_text(encoding='utf-8-sig')
        text=text.replace('animation-assigning','animation-exaggeration').replace('A01','A02')
        if name=='build_delivery.py':
            assert 'all17ParagraphsRead' in text and 'qa/final-audio-v1/continuity.json' in text
            text=text.replace('all17ParagraphsRead','all14ParagraphsRead')
            text=text.replace('qa/final-audio-v1/continuity.json','qa/audio-v1/continuity.json')
        if dst.exists():
            assert dst.read_text(encoding='utf-8-sig')==text, f'Preserve changed helper: {dst}'
        else:
            dst.write_text(text,encoding='utf-8')
        records.append({'name':name,'source':src.relative_to(R).as_posix(),
            'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),
            'target':dst.relative_to(R).as_posix(),
            'targetSha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
    (H/'final-helper-provenance.json').write_text(json.dumps({
        'episode':'A02','status':'prepared-no-media-job',
        'changes':'Episode/slug binding; actual14-paragraph final ASR review; current audio-v1 continuity evidence.',
        'helpers':records,'userReviewInferred':False,'platformMutation':False
    },ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('A02 local assembly, extraction and four-output collector prepared.')

if __name__=='__main__':main()
