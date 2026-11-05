"""Prepare only sentences that say the radiometric quantities. Retain sentence and lesson boundaries."""
import json
import re
from pathlib import Path
from difflib import SequenceMatcher
from bisect import bisect_left

PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT.parents[1]
WORK = PROJECT/'production/local/render-v6'
VOICE = WORK/'voice'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare():
    tasks=[]
    voice_rows=[]; en_rows=[]
    for p in sorted((WORK.parent/'render-v4/final-mix-review/paragraphs').glob('*.json')):
        evidence=read(p); entry=evidence['entry']; words=evidence['chunks']; sid=entry['scene_id']
        text=entry['text']; duration=entry['end']-entry['start']
        if not any(w in text for w in ['복사휘도','복사조도']):continue
        # ASR anchors on both sides of each sentence, independent of changed pronunciation.
        normalized=lambda s: ''.join(re.findall('[가-힣A-Za-z0-9]',s)).lower()
        observed='';starts=[];ends=[]
        for word in words:
            word_text=normalized(word['text']); start,end=word['timestamp']
            if not word_text:continue
            end=duration if end is None else end
            for i,c in enumerate(word_text):
                observed+=c;starts.append(start+(end-start)*i/len(word_text));ends.append(start+(end-start)*(i+1)/len(word_text))
        expected=normalized(text);mapping={}
        for block in SequenceMatcher(None,expected,observed,autojunk=False).get_matching_blocks():
            for i in range(block.size):mapping[block.a+i]=block.b+i
        source_indices=sorted(mapping);cursor=0
        for sentence in re.findall(r'[^.!?]+[.!?]?',text):
            loc=normalized(sentence);end_idx=cursor+len(loc)
            if '복사휘도' in sentence or '복사조도' in sentence:
                a=source_indices[bisect_left(source_indices,cursor)]
                z=source_indices[bisect_left(source_indices,end_idx)-1]
                assert a<cursor+5 and z>end_idx-7
                name=f'{sid}s{len(tasks)+1:02}';spoken=sentence.strip().replace('복사휘도','레디언스').replace('복사조도','이레디언스')
                tasks.append(dict(id=name,scene=sid,old=sentence.strip(),spoken=spoken,start=entry['start']+starts[mapping[a]],end=entry['start']+ends[mapping[z]],paragraphStart=entry['start'],paragraphEnd=entry['end']))
                voice_rows.append(dict(id=name,title=entry['scene_title'],lines=[spoken],displayLines=[spoken]))
                en_rows.append(dict(id=name,title=entry['scene_title'],lines=[entry['text_en']]))
            cursor=end_idx
    assert len(tasks)==8
    write(VOICE/'sentences.json',tasks)
    manifest=read(PROJECT/'production/tts-manifest.json')
    for lang,rows,key in [('ko',voice_rows,'script'),('en',en_rows,'scriptEn')]:
        path=VOICE/f'script.{lang}.json';write(path,dict(slug=PROJECT.name,scenes=rows))
        manifest['paths'][key]=path.relative_to(ROOT).as_posix()
    manifest['tts']['outputDir']=VOICE.relative_to(ROOT).as_posix()
    manifest['tts'].pop('generatedPcmSha256',None);manifest['tts']['status']='targeted-term-reading'
    write(VOICE/'manifest.json',manifest)
if __name__=='__main__':prepare()
