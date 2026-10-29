"""Map our diagram anchors to existing word-timestamp ASR; no audio inference job."""
from __future__ import annotations
from difflib import SequenceMatcher
import math
from pathlib import Path
import re
from assemble_documentary import PROJECT,digest,load,save,now
from render_evidence_diagrams import SPECS,paragraph_texts


def normalized(value):
    value=''.join(c for c in value if c.isalnum()).lower()
    # ASR spells verified quantities as digits and names in Latin letters,
    # while the approved TTS script contains their spoken Korean forms.
    # These equivalences do not substitute or conceal an actual content error.
    for printed,spoken in [('3572','삼천오백일흔두'),('195','백아흔다섯'),
                           ('374','삼백일흔네'),('32','서른두'),
                           ('gdscript','지디스크립트'),('rea','알이에이')]:
        value=value.replace(printed,spoken)
    return value


def main():
    timing_path=PROJECT/'production/local/audio-v1/narration.timing.json'
    asr_path=PROJECT/'production/local/audio-v1/review/source-full-asr.timestamps.json'
    output=PROJECT/'production/local/evidence-diagram-timings.json'
    timing,asr=load(timing_path),load(asr_path)
    texts=paragraph_texts()
    entries=[]
    for index,paragraph in enumerate(timing['entries']):
        key=f'{paragraph["scene_id"]}-p{int(paragraph["paragraph"]):02}'
        if key not in SPECS:
            continue
        expected=normalized(texts[key])
        observed=''; word_for_character=[]
        for word_index,chunk in enumerate(asr['chunks']):
            start,end=chunk['timestamp']
            if start is None or end is None:
                continue
            if start>=paragraph['end'] or end<=paragraph['start']:
                continue
            chars=normalized(chunk['text'])
            observed+=chars
            word_for_character.extend([{'index':word_index,'text':chunk['text'],
                                        'start':start,'end':end}]*len(chars))
        mapping={}
        for match in SequenceMatcher(None,expected,observed,autojunk=False).get_matching_blocks():
            for offset in range(match.size):
                mapping[match.a+offset]=match.b+offset
        coverage=len(mapping)/len(expected)
        if coverage<.93:
            raise ValueError(f'Poor ASR matching for {key}: {coverage}; requires review')
        start_frame=round(paragraph['start']*60)
        end_frame=round(timing['entries'][index+1]['start']*60) if index+1<len(timing['entries']) else math.ceil(timing['duration_seconds']*60)
        entry={'scene':paragraph['scene_id'],'paragraph':paragraph['paragraph'],
               'durationSeconds':(end_frame-start_frame)/60,
               'speechStartSeconds':max(0,paragraph['start']-start_frame/60),
               'speechEndSeconds':paragraph['end']-start_frame/60,'timingVerified':True,
               'cueAlignmentReviewed':False,'cueTimes':{},'cueEvidence':{},
               'narrationGlobalStart':paragraph['start'],'narrationGlobalEnd':paragraph['end'],
               'timelineStartFrame':start_frame,'timelineEndFrame':end_frame,
               'timelineStartSeconds':start_frame/60,
               'existingBreathingGapSeconds':end_frame/60-paragraph['end'],
               'cueAlignmentSource':{'path':str(asr_path.relative_to(PROJECT)).replace('\\','/'),
                                     'sha256':digest(asr_path),'method':'word ASR + exact character correspondence',
                                     'paragraphCharacterCoverage':coverage,'humanListening':False}}
        for cue_index,(name,phrase) in enumerate(SPECS[key][1]):
            original_offset=texts[key].find(phrase)
            if original_offset<0:
                raise ValueError(f'Phrase absent: {key}/{name}')
            char_start=len(normalized(texts[key][:original_offset]))
            phrase_end=char_start+len(normalized(phrase))
            matched=[i for i in range(char_start,phrase_end) if i in mapping]
            if not matched or matched[0]-char_start>2:
                raise ValueError(f'Anchor beginning not reliably aligned: {key}/{name}')
            observed_offset=mapping[matched[0]]
            word=word_for_character[observed_offset]
            local=max(0,word['start']-start_frame/60)
            entry['cueTimes'][name]=round(local*60)/60
            entry['cueEvidence'][name]={'method':'asr-word-aligned','phrase':phrase,
                'spokenCharacterOffset':char_start,'firstMatchedCharacterOffset':matched[0],
                'asrWordIndex':word['index'],'asrWordText':word['text'],
                'asrWordStartGlobal':word['start'],'asrWordEndGlobal':word['end'],
                'localSecondsUnrounded':local,'note':'Automatic timestamp evidence; not human speech/visual review'}
        entries.append(entry)
    result={'schemaVersion':1,'updatedAtUtc':now(),'sourceTiming':str(timing_path.relative_to(PROJECT)).replace('\\','/'),
            'sourceTimingSha256':digest(timing_path),'sourceAsrSha256':digest(asr_path),
            'sourceAudioSha256':asr['audio_sha256'],
            'durationPolicy':'Frame-rounded continuous boundaries through next paragraph start; only existing breathing gaps',
            'cueStatus':'ASR word aligned, pending final moving speech/visual review','paragraphs':entries}
    save(output,result)
    print(f'Aligned {sum(len(e["cueTimes"]) for e in entries)} anchors across {len(entries)} measured paragraphs')
    for e in entries:
        print(f'{e["scene"]}-p{e["paragraph"]:02}: {e["cueAlignmentSource"]["paragraphCharacterCoverage"]:.3f} character match')


if __name__=='__main__':
    main()
