"""Build script-faithful clause SRT from the current full-source Whisper pass.

No GPU. Reuses existing align_characters word mapping; does not edit PCM or
paragraph timing. EN is a semantic translation, timed within each matched KO
paragraph rather than pretending it has spoken English word timestamps.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import align_project_subtitles as aligner
from build_translated_srt import timestamp, split_caption, wrapped_lines, weight
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location('buckshot_voice_review',PROJECT/'production/review-voice.py')
review = module_from_spec(spec)
spec.loader.exec_module(review)
aligner.normalized = review.normalized

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def clauses(text,width):
    # Keep sentence boundaries; preserve commas as useful clause boundaries.
    # Only overlong individual clauses are repartitioned by the existing helper.
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+',text.strip()) if s.strip()]
    chunks = []
    for sentence in sentences:
        parts = [s.strip() for s in re.split(r'(?<=[,;])\s+',sentence) if s.strip()]
        joined=[];i=0
        minimum_piece=10 if width==32 else 12
        while i<len(parts):
            part=parts[i];i+=1
            # Enumeration nouns and short openers belong with their phrase;
            # avoid flashes such as "체력," / "차례," or "Today," alone.
            while weight(part)<minimum_piece and i<len(parts) and len(wrapped_lines(part+' '+parts[i],width))<=2:
                part+=' '+parts[i];i+=1
            if weight(part)<minimum_piece and joined and len(wrapped_lines(joined[-1]+' '+part,width))<=2:
                joined[-1]+=' '+part
            else:
                joined.append(part)
        sentence_chunks=[]
        for part in joined:
            sentence_chunks.extend(split_caption(part,width,2))
        i=0
        while i<len(sentence_chunks)-1:
            if weight(sentence_chunks[i])<minimum_piece and len(wrapped_lines(sentence_chunks[i]+' '+sentence_chunks[i+1],width))<=2:
                sentence_chunks[i:i+2]=[sentence_chunks[i]+' '+sentence_chunks[i+1]]
            else:
                i+=1
        chunks.extend(sentence_chunks)
    assert re.sub(r'\s+','',text) == re.sub(r'\s+','',' '.join(chunks)), 'Clause splitting changed source text'
    return chunks

def display(text):
    text = text.replace('알이에이','REA').replace('지디스크립트','GDScript').replace('고도 엔진','Godot 엔진')
    for spoken,number in [('삼천오백일흔두','3,572'),('백아흔다섯','195'),('삼백일흔네','374'),('서른두','32')]:
        text = text.replace(spoken,number)
    return text

def semantic_groups(row):
    """Use reviewed sentence meaning, not the whole paragraph as an EN slot."""
    ko = [s.strip() for s in re.split(r'(?<=[.!?])\s+',row['ko'].strip()) if s.strip()]
    en = [s.strip() for s in re.split(r'(?<=[.!?])\s+',row['en'].strip()) if s.strip()]
    key = (row['scene'],row['paragraph'])
    if key == ('03',2):
        pairs = [([i],[i]) for i in range(5)] + [([5,6],[5])]
    elif key == ('05',2):
        pairs = [([0],[0]),([1,2],[1,2]),([3,4],[3]),([5],[4])]
    elif key == ('06',1):
        pairs = [([0],[0]),([1],[1,2]),([2],[3])]
    else:
        assert len(ko)==len(en), ('A new sentence mismatch needs semantic review',key)
        pairs = [([i],[i]) for i in range(len(ko))]
    assert [i for k,_ in pairs for i in k] == list(range(len(ko)))
    assert [i for _,e in pairs for i in e] == list(range(len(en)))
    groups=[];offset=0
    for k,e in pairs:
        korean=' '.join(ko[i] for i in k);english=' '.join(en[i] for i in e)
        size=len(review.normalized(korean))
        groups.append({'koSentenceIndices':k,'enSentenceIndices':e,'koText':korean,'enText':english,'koCharacterStart':offset,'koCharacterEnd':offset+size,'enClauses':clauses(english,46),'mappingReview':'Complete KO/EN text reviewed; these sentences express the same step/result'})
        offset+=size
    assert offset==len(review.normalized(row['ko']))
    return groups

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true',help='Check text segmentation without requiring audio/ASR')
    args = parser.parse_args()
    manifest = read(PROJECT/'production/tts-manifest.json')
    folder = ROOT/manifest['tts']['outputDir']
    script = read(ROOT/manifest['paths']['script'])
    english = read(ROOT/manifest['paths']['scriptEn'])
    planned = []
    for scene,en_scene in zip(script['scenes'],english['scenes']):
        assert scene['id'] == en_scene['id'] and len(scene['lines']) == len(en_scene['lines'])
        for n,(ko,en) in enumerate(zip(scene['lines'],en_scene['lines']),1):
            row={'scene':scene['id'],'paragraph':n,'ko':ko,'en':en,'koClauses':clauses(ko,32),'enClauses':clauses(en,46)}
            row['semanticGroups']=semantic_groups(row)
            planned.append(row)
    if args.preflight:
        counts = {lang:sum(len(row[lang+'Clauses']) for row in planned) for lang in ['ko','en']}
        save(PROJECT/'planning/caption-semantic-map.json',{'schemaVersion':1,'koScriptSha256':digest(ROOT/manifest['paths']['script']),'enScriptSha256':digest(ROOT/manifest['paths']['scriptEn']),'scope':'Text meaning/sentence mapping only; no actual speech/caption timing approval','groups':[{'scene':row['scene'],'paragraph':row['paragraph'],'semanticGroups':row['semanticGroups']} for row in planned],'displayConversions':{'알이에이':'REA','지디스크립트':'GDScript','고도 엔진':'Godot 엔진','삼천오백일흔두':'3,572','백아흔다섯':'195','삼백일흔네':'374','서른두':'32'}})
        print(json.dumps({'status':'text-clause-preflight-passed','paragraphs':len(planned),'semanticGroups':sum(len(row['semanticGroups']) for row in planned),'cueCounts':counts,'gpuUsed':False,'audioTimingVerified':False}))
        return
    voice = folder/'narration.wav'
    timing = read(folder/'narration.timing.json')
    asr = read(folder/'review/source-full-asr.timestamps.json')
    assert asr['audio_sha256'] == digest(voice), 'Stale whole-source ASR; inspect current PCM'
    assert asr['timestampMode'] == 'word' and asr['language'] == 'korean'
    assert len(timing['entries']) == len(planned)
    duration = float(timing['duration_seconds'])
    cues = {'ko':[],'en':[]}
    mappings = []
    quality_flags = []
    for row,entry in zip(planned,timing['entries']):
        assert entry['scene_id']==row['scene'] and entry['paragraph']==row['paragraph'] and entry['text']==row['ko']
        origin,end = float(entry['start']),float(entry['end'])
        words = []
        for word in asr['chunks']:
            begin,finish = word['timestamp']
            if begin is None or finish is None:
                continue
            if origin <= (begin+finish)/2 < end:
                words.append({'text':word['text'],'timestamp':[max(0,float(begin)-origin),min(end-origin,float(finish)-origin)]})
        starts,ends,coverage = aligner.align_characters(row['ko'],words,end-origin)
        cursor = 0
        ko_indices,en_indices = [],[]
        for chunk in row['koClauses']:
            length = len(review.normalized(chunk))
            a,b = origin+float(starts[cursor]),origin+float(ends[cursor+length-1])
            cursor += length
            cue = {'id':len(cues['ko'])+1,'start':a,'end':b,'text':'\n'.join(wrapped_lines(display(chunk),32)),'scene':row['scene'],'paragraph':row['paragraph'],'alignment':'current-whole-source-ASR-word-matched'}
            cues['ko'].append(cue);ko_indices.append(cue['id'])
        assert cursor == len(review.normalized(row['ko']))
        speech_start,speech_end = origin+float(starts[0]),origin+float(ends[-1])
        semantic_timing=[]
        for group in row['semanticGroups']:
            group_start=origin+float(starts[group['koCharacterStart']]);group_end=origin+float(ends[group['koCharacterEnd']-1])
            weights=[weight(chunk) for chunk in group['enClauses']];total=sum(weights);used=0;group_en_ids=[]
            for chunk,w in zip(group['enClauses'],weights):
                a=group_start+(group_end-group_start)*used/total;used+=w;b=group_start+(group_end-group_start)*used/total
                cue={'id':len(cues['en'])+1,'start':a,'end':b,'text':'\n'.join(wrapped_lines(chunk,46)),'scene':row['scene'],'paragraph':row['paragraph'],'alignment':'translation-within-reviewed-corresponding-KO-sentence-group; estimated-inner-clause-boundary'}
                cues['en'].append(cue);en_indices.append(cue['id']);group_en_ids.append(cue['id'])
            semantic_timing.append(dict(group,start=group_start,end=group_end,enCueIds=group_en_ids))
        mappings.append({'scene':row['scene'],'paragraph':row['paragraph'],'sourcePcmStart':origin,'sourcePcmEnd':end,'speechStart':speech_start,'speechEnd':speech_end,'matchingCharacterCoverage':coverage,'koCueIds':ko_indices,'enCueIds':en_indices,'semanticGroups':semantic_timing,'rawExpected':row['ko'],'rawRecognized':' '.join(w['text'] for w in words),'reviewStatus':'pending direct audio/caption review'})
    for lang,language_cues in cues.items():
        previous=0
        for cue in language_cues:
            assert 0<=cue['start']<cue['end']<=duration+.002 and cue['start']>=previous-.002, ('Invalid or overlapping cue',lang,cue)
            assert len(cue['text'].splitlines())<=2
            previous=cue['end']
            span=cue['end']-cue['start']
            cps=len(re.sub(r'\s+','',cue['text']))/span
            if span<.65 or cps>(18 if lang=='ko' else 23):
                quality_flags.append({'language':lang,'cue':cue['id'],'seconds':span,'charactersPerSecond':cps,'review':'Check actual readability; no automatic speech speedup or content deletion'})
        destination=folder/f'narration.{lang}.clauses.srt'
        destination.write_text('\n\n'.join(f"{cue['id']}\n{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n{cue['text']}" for cue in language_cues)+'\n',encoding='utf-8')
    review_report={'schemaVersion':1,'sourceWavSha256':digest(voice),'sourceAsrSha256':digest(folder/'review/source-full-asr.timestamps.json'),'koSha256':digest(folder/'narration.ko.clauses.srt'),'enSha256':digest(folder/'narration.en.clauses.srt'),'paragraphCount':len(mappings),'koCueCount':len(cues['ko']),'enCueCount':len(cues['en']),'allTextPreserved':True,'paragraphMapping':mappings,'readingSpeedFlags':quality_flags,'englishTimingLimit':'EN follows reviewed matching KO sentence groups instead of entire paragraphs. Inner clause boundaries are estimated; directly inspect timing and all cue mappings. No English speech was synthesized.','humanListening':False,'finalVisualReview':'pending actual1080p/captions/375px rendering','status':'caption-candidate-awaiting-direct-review'}
    save(folder/'review/caption-alignment-review.json',review_report)
    save(folder/'review/clause-cues.json',cues)
    print(json.dumps({'status':review_report['status'],'koCues':len(cues['ko']),'enCues':len(cues['en']),'readabilityFlags':len(quality_flags),'gpuUsed':False}))

if __name__=='__main__':
    main()
