"""Record reviewed recognition evidence and bind literal whole-word captions."""
from pathlib import Path
import hashlib,json,re,statistics
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=ROOT/'projects/shorts-oot-ninja-show-z-targeting'
BASE=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
    assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def norm(s):
    # Orthographic number forms only. No pronunciation or homophone aliases.
    for a,b in [('육십사','64'),('삼인칭','3인칭'),('삼차원','3차원')]:s=s.replace(a,b)
    return re.sub(r'[^0-9A-Za-z가-힣]','',s).lower()
def main():
    proof_path=BASE/'voice-edit-v3/voice-generation-complete-proof.json';proof=read(proof_path);narr=read(P/'planning/narration-edited-v3.json')
    old_review=Path(narr['previousAsr']['path']);old=read(old_review);old_levels=read(Path(narr['previousLevels']['path']))
    new_review=Path(read(BASE/'asr-edit-v3/status.json')['review']['path']);new=read(new_review);new_levels=read(new_review.parent/'levels.json')
    assert new_levels['flags']==[] and [x['taskKey']for x in old_levels['flags']]==['paragraph-p001']
    assert next(x for x in new['results']if x['task']['key']=='paragraph-p001')['rawRecognition']['text'].replace(' ','')== '젤다에서적을주목해보세요옆으로움직여도상대를바라봅니다교토의닌자공연이여기에어떤힌트를줬을까요?'
    timing=read(proof['unitTiming']['path'])['entries'];prior={x['task']['key']:x for x in old['results']};unit_by_id={u['id']:u for u in narr['units']};words=[]
    for entry,row in zip(timing,proof['rawChunks']):
        uid=entry['scene_id'];record=prior['unit-'+uid];assert record['task']['sha256']==row['sha256']
        for i,chunk in enumerate(record['rawRecognition']['chunks']):
            a,b=chunk['timestamp'];assert a is not None and b is not None and 0<=a<b<=row['duration']
            source=dict(review=pin(old_review),taskKey=record['task']['key'],wordIndex=i,timestamp=[a,b]);text=chunk['text']
            if uid=='u008' and text.strip()=='주의를':
                # Independently cropped context recognizes the literal source
                # word 주위를. Keep every original ASR record unchanged and
                # use that actual positive whole-word onset/offset instead.
                join=prior['join-u008-u009'];j=next((n,w)for n,w in enumerate(join['rawRecognition']['chunks'])if w['text'].strip()=='주위를');n,w=j
                offset=(join['task']['offsetSample']-record['task']['offsetSample'])/24000;a,b=[offset+x for x in w['timestamp']];assert 0<=a<b<=row['duration'];text=w['text'];source=dict(review=pin(old_review),taskKey=join['task']['key'],wordIndex=n,timestamp=w['timestamp'],unitOffsetSeconds=offset,reason='Literal 주위를 in independent joined context; raw isolated and paragraph homophone ambiguity preserved.')
            words.append(dict(unit=uid,paragraph=unit_by_id[uid]['paragraph'],recognizedText=text,start=entry['start']+a,end=entry['start']+b,source=source))
    clauses_path=P/'planning/caption-clauses-edited-v3.json';clauses=read(clauses_path);cues=[]
    for para in clauses['paragraphs']:
        inventory=[w for w in words if w['paragraph']==para['id']];text=''.join(norm(w['recognizedText'])for w in inventory);expected=''.join(norm(x[0])for x in para['clauses']);assert text==expected,(para['id'],text,expected)
        boundaries={0:0};position=0
        for i,w in enumerate(inventory):position+=len(norm(w['recognizedText']));boundaries[position]=i+1
        position=0
        for index,(ko,en)in enumerate(para['clauses']):
            start=position;position+=len(norm(ko));assert start in boundaries and position in boundaries,'Clause would split an ASR word'
            first,last=inventory[boundaries[start]],inventory[boundaries[position]-1];assert first['start']<last['end']
            cues.append(dict(paragraph=para['id'],clauseIndex=index,ko=ko,en=en,start=first['start'],spokenEnd=last['end'],startWord=first,endWord=last))
    for i,c in enumerate(cues):
        c['end']=cues[i+1]['start']if i+1<len(cues)else proof['canonical']['duration'];assert c['start']<c['spokenEnd']<=c['end']+.0001
    rows=[x for x in old_levels['paragraphs']if x['kind']=='paragraph'and x['paragraph']!='p001']+new_levels['paragraphs'];assert len(rows)==7
    med=statistics.median(x['wholeTake']['bodyDbfs']for x in rows)
    # Keep the existing paragraph-relative warning threshold as well.
    paragraph_levels=[dict(paragraph=x['paragraph'],bodyDbfs=x['wholeTake']['bodyDbfs'],relativeToMedianDb=x['wholeTake']['bodyDbfs']-med)for x in rows];assert all(x['relativeToMedianDb']>=-4 for x in paragraph_levels)
    review=dict(schemaVersion=1,voice=pin(proof_path),sourceAsr=pin(old_review),editedAsr=pin(new_review),sourceLevels=pin(narr['previousLevels']['path']),editedLevels=pin(new_review.parent/'levels.json'),rawUnitsByteExact=True,
        contentReview='Retained units and p002..p007 compared with exact script. All literal learning claims and source order preserved. Spacing/punctuation and spoken-number spelling differences are immaterial. Cropped-context 사슬/사실 and 주위/주의 variation is retained in raw evidence; caption anchor for 주위 comes from literal positive whole-word joined recognition. Removed opening term 라곤 ambiguity is excluded.',
        newJoinsReview='Both new joins preserve the complete adjacent words and positive word intervals;0.28s PCM gap preserved.',
        sustainedDeclineHolds=[],paragraphRelativeLevels=paragraph_levels,sameApprovedReferenceAndModel=True,voiceBiometricIdentityMeasured=False,approvedForTechnicalDownstream=True,actualListening=False,humanApproval=False,finalFilmComplete=False)
    target=BASE/'voice-edit-v3/technical-voice-review.json';write(target,review)
    out=P/'production/caption-timing-v3.json';write(out,dict(voice=pin(proof_path),technicalVoiceReview=pin(target),clauses=pin(clauses_path),cues=cues,audioOffsetSeconds=0,voiceSpeed=1,wordInterpolation=False,englishUsesSameMeaningClauseInterval=True,finalFilmComplete=False))
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    for lang in ['ko','en']:
        srt=P/'production'/('captions-v3.'+lang+'.srt');assert not srt.exists();srt.write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c[lang]}'for i,c in enumerate(cues))+'\n',encoding='utf8')
    print(json.dumps(dict(technicalVoiceReview=pin(target),captions=pin(out),cues=len(cues),duration=proof['canonical']['duration'],humanApproval=False)))
if __name__=='__main__':main()
