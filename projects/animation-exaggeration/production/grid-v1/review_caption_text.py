"""Bind the completed bilingual read-through to current canonical and caption bytes."""
from pathlib import Path
from datetime import datetime,timezone
import re
import audio_pipeline as ap
from build_delivery import parse_srt

H=Path(__file__).resolve().parent
P=H.parents[1]
L=H.parent/'local/grid-v1/edit'

def main():
    tracks={lang:parse_srt(L/f'captions.{lang}.srt') for lang in ('ko','en')}
    checks={}
    files=[L/'captions.json',L/'caption-layout.json',H/'caption-timing-plan.json']
    for lang in ('ko','en'):
        src=P/f'script/grid-v1/narration.{lang}.json'
        script=ap.read(src)
        expected=' '.join(' '.join(line.split()) for scene in script['scenes'] for line in scene['lines'])
        assert len(tracks[lang])==100
        assert ' '.join(cue['text'] for cue in tracks[lang])==expected
        ass=L/f'captions.{lang}.ass'
        rows=[line for line in ass.read_text(encoding='utf-8-sig').splitlines() if line.startswith('Dialogue: 2,')]
        assert len(rows)==100
        rendered=[re.sub(r'\{[^}]*\}','',row.split(',',9)[9]).replace('\\N',' ') for row in rows]
        assert rendered==[x['text'] for x in tracks[lang]]
        assert all('\\pos(960,970)' in row for row in rows)
        checks[lang]={'paragraphs':sum(len(s['lines']) for s in script['scenes']),
            'canonicalRejoinExact':True,'assTextExact':True,'fixedCaptionCenter':True}
        files.extend([src,ass,L/f'captions.{lang}.srt'])
    assert [(x['start'],x['end']) for x in tracks['ko']]==[(x['start'],x['end']) for x in tracks['en']]
    layout=ap.read(L/'caption-layout.json')
    assert layout['geometryPassed'] and layout['fontSize']==48 and layout['fixedCenter']==[960,970]
    ap.save(H/'caption-text-review.json',{
        'schemaVersion':1,'episode':'A02','revision':'grid-v1',
        'status':'complete-bilingual-text-and-clock-review-encoded-pixels-separate',
        'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'root',
        'inputs':[ap.artifact(p) for p in files],
        'counts':{'scenes':5,'paragraphs':14,'pairedCues':100},'checks':checks,
        'directReadThrough':'All14 canonical KO/EN paragraphs and all100 bilingual SRT clauses read in order without headings; no omitted/additional claims or reference-creator framing found.',
        'retainedTechnicalMeaning':[
            'Same arm direction, not an identical hand trajectory, when torso contribution changes.',
            'Rig rotation changes orientation; translation changes the joint origin; matched hand target remains an own Unity demonstration.',
            'Observe complete normal-speed motion before inspecting a paused pose; repair geometry while retaining pose function.',
            '0cm origin and100→110→100cm are explicitly our illustrative values;10cm overshoot is retained in both languages.'
        ],
        'essentialConditionsRetained':['Small on-screen character size','Same camera and playback time for amplitude comparison','Paused posture evaluated in motion context'],
        'newLinesOmittedDuringThisReview':[], 'issues':[],
        'encodedPixelsReviewed':False,'fullAudioListening':False,'userReview':False,
        'limitations':'Text and structural timing checks do not establish actual encoded readability, pronunciation or full moving-picture review.'
    })
    print('A02: 14 paragraphs and100 paired cues; canonical/ASS equality and fixed geometry pass.')

if __name__=='__main__':main()
