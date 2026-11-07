"""CPU-only exact-source and measured mixed-weight caption validation for 11.05."""
from pathlib import Path
import argparse, copy, hashlib, json, re, unittest
from PIL import ImageFont

ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'projects/shorts-leveldesign-11-05'
FONT=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')
FONT_SHA='018174e8cdd366aff67c8d366c7dc806a7babbe7f2819fc23b00d59f7b8353d0'

def need(value,reason):
    if not value: raise ValueError(reason)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def fonts():
    need(sha(FONT)==FONT_SHA,'Current caption font changed')
    result={}
    for weight in (500,700):
        f=ImageFont.truetype(str(FONT),48); f.set_variation_by_axes([weight]); result[weight]=f
    return result
def widths(cue,fs):
    lines=cue['lines']; text=cue['text']; spans=cue['emphasis']
    need(isinstance(lines,list) and 1<=len(lines)<=2 and all(isinstance(s,str) and s and s==s.strip() for s in lines),'One/two nonempty authored lines required')
    need(' '.join(lines)==text,'Authored wrap must preserve exact text')
    need(isinstance(spans,list) and len(spans)<=1,'At most one emphasis span')
    found=False; values=[]; offset=0
    for line in lines:
        if spans:
            span=spans[0]; a,b=span['start'],span['end']
            need(type(a)is int and type(b)is int and 0<=a<b<=len(text) and span['role'] in ('term','result','problem'),'Invalid emphasis')
            need(span['text']==text[a:b],'Emphasis text differs')
            if offset<=a<b<=offset+len(line):
                left,right=a-offset,b-offset
                value=fs[500].getlength(line[:left])+fs[700].getlength(line[left:right])+fs[500].getlength(line[right:]); found=True
            else: value=fs[500].getlength(line)
        else: value=fs[500].getlength(line)
        values.append(float(value)); offset+=len(line)+1
    need(not spans or found,'Emphasis crosses an authored line boundary')
    need(max(values)<=800,'Caption exceeds fixed 800px at actual 48px mixed weights')
    return values

def validate(document,narration,fs):
    need(document['topicId']=='11.05' and document['schemaVersion']=='11.05-caption-clauses-v1','Wrong caption source scope')
    need(document['actualTimingAssigned'] is False and document['humanApproval'] is False,'Authored captions cannot approve timing/human review')
    st=document['style']
    need((st['fontSizePx'],st['fontWeight'],st['emphasisFontWeight'],st['maxTextWidthPx'],st['maxLines'],st['lineHeightPx'])==(48,500,700,800,2,62),'Fixed caption style changed')
    need(st['fontSHA256']==FONT_SHA,'Font identity changed')
    groups=document['groups']; ids=[]; counts={'ko':0,'en':0}; max_width=0; all_logical=[]
    for paragraph,(ko,en) in enumerate(zip(narration['narrationKo'],narration['paragraphsEn']),1):
        rows=[g for g in groups if g['paragraph']==paragraph]
        need(rows and ' '.join(g['ko'] for g in rows)==ko and ' '.join(g['en'] for g in rows)==en,'Paragraph reconstruction differs')
        logical_parts=re.split(r'(?<=[.!?])\s+',ko); logical_cursor=0
        for language,source in (('ko',ko),('en',en)):
            position=0
            for group in rows:
                a,b=group[language+'SourceCharRange']
                need([a,b]==[position,position+len(group[language])] and source[a:b]==group[language],'Group source range/reordering differs')
                position=b+1
                cues=group[language+'Cues']
                need(cues and ' '.join(c['text'] for c in cues)==group[language],'Cue reconstruction differs')
                local=0
                for cue in cues:
                    need(cue['id'] not in ids,'Duplicate cue ID'); ids.append(cue['id'])
                    need(cue['sourceCharRange']==[a+local,a+local+len(cue['text'])] and cue['groupCharRange']==[local,local+len(cue['text'])],'Cue source ranges differ')
                    need(cue['clock']==dict(startSample=None,endSample=None,startFrame=None,endFrameExclusive=None),'Authored source must not manufacture clocks')
                    measured=widths(cue,fs)
                    need(cue['measuredLineWidthsPx']==measured,'Stored font measurements differ')
                    max_width=max(max_width,*measured); counts[language]+=1; local+=len(cue['text'])+1
                    if language=='ko':
                        need(cue['spokenLiteralAnchorKo']==cue['text'],'Korean literal anchor differs')
                    else:
                        anchor=cue['spokenKoAnchor']; x,y=anchor['sourceCharRange']
                        need(group['koSourceCharRange'][0]<=x<y<=group['koSourceCharRange'][1] and ko[x:y]==anchor['text'],'English cue lacks an exact corresponding Korean source anchor')
                        need(anchor['boundaryScope']=='semantic-group' and anchor['actualWordBoundaryVerified'] is False,'English authoring cannot approve a word clock')
        for group in rows:
            mapped=group['koLogicalSentences']
            need(mapped,'Logical sentence mapping missing')
            for item in mapped:
                expected_id=f'p{paragraph:03d}-c{logical_cursor+1:02d}'
                need(item['sceneId']==expected_id and item['sentenceIndexZeroBased']==logical_cursor and item['canonicalKo']==logical_parts[logical_cursor],'Logical48 mapping differs')
                x,y=item['sourceCharRange']; need(ko[x:y]==item['canonicalKo'],'Logical source range differs')
                all_logical.append(expected_id); logical_cursor+=1
        need(logical_cursor==len(logical_parts),'Logical sentence omitted')
    need([g['paragraph'] for g in groups]==sorted(g['paragraph'] for g in groups),'Group paragraph order differs')
    need(len(narration['narrationKo'])==len(narration['paragraphsEn'])==14 and len(all_logical)==48,'Expected exact current14 paragraphs/48 logical sentences')
    need(document['counts']==dict(paragraphs=14,semanticGroups=len(groups),koLogicalSentences=48,koCues=counts['ko'],enCues=counts['en']),'Stored counts differ')
    return dict(paragraphs=14,logicalSentences=48,semanticGroups=len(groups),cueCounts=counts,maxMeasuredLineWidthPx=max_width,exactReconstruction=True,actualTimingAssigned=False,actualPixelReview=False,humanApproval=False)

def verify(path=PROJECT/'caption-clauses-v1.json'):
    document=read(path); pin=document['sourceNarration']; source=Path(pin['path'])
    need(source.resolve()==(PROJECT/'narration-final-v4.json').resolve() and sha(source)==pin['sha256'],'Current final narration path/hash differs')
    need(document['validatorSourceSHA256']==sha(__file__),'Caption validator source changed')
    return validate(document,read(source),fonts())

class FaultTests(unittest.TestCase):
    def setUp(self): self.fs=fonts()
    def current(self): return read(PROJECT/'caption-clauses-v1.json'),read(PROJECT/'narration-final-v4.json')
    def test_legal_mixed_weight(self):
        cue=dict(text='방 템플릿입니다.',lines=['방 템플릿입니다.'],emphasis=[dict(start=0,end=5,text='방 템플릿',role='term')]); self.assertLess(widths(cue,self.fs)[0],800)
    def test_omitted_wrap_word(self):
        with self.assertRaises(ValueError): widths(dict(text='같은 방 구조',lines=['같은 구조'],emphasis=[]),self.fs)
    def test_overflow(self):
        with self.assertRaises(ValueError): widths(dict(text='방'*30,lines=['방'*30],emphasis=[]),self.fs)
    def test_cross_line_emphasis(self):
        with self.assertRaises(ValueError): widths(dict(text='방 연결 유형',lines=['방 연결','유형'],emphasis=[dict(start=2,end=7,text='연결 유형',role='term')]),self.fs)
    def test_logical_scene_omission(self):
        document,narration=self.current(); document['groups'][2]['koLogicalSentences']=[]
        with self.assertRaises(ValueError): validate(document,narration,self.fs)
    def test_wrong_language_anchor(self):
        document,narration=self.current(); document['groups'][0]['enCues'][0]['spokenKoAnchor']['text']='다른 원문'
        with self.assertRaises(ValueError): validate(document,narration,self.fs)
    def test_manufactured_timestamp(self):
        document,narration=self.current(); document['groups'][0]['koCues'][0]['clock']['startSample']=0
        with self.assertRaises(ValueError): validate(document,narration,self.fs)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--selftest',action='store_true'); ap.add_argument('--path',type=Path); args=ap.parse_args()
    if args.selftest:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(FaultTests); result=unittest.TextTestRunner(verbosity=1).run(suite)
        if not result.wasSuccessful(): raise SystemExit(1)
    print(json.dumps(verify(args.path or PROJECT/'caption-clauses-v1.json'),ensure_ascii=False))
