"""Full-text ASR comparison for this selected Short. No synthesis or media jobs."""
from pathlib import Path
import json,hashlib,re,unicodedata,difflib,argparse
P=Path(__file__).resolve().parents[1];R=P.parents[1]
from audio_revision import L, VOICE, REVISION, guard as revision_guard
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(t):
 for display,speech in sorted(read(P/'script/clauses.json').get('pronunciationAliases',{}).items(),key=lambda x:-len(x[0])):t=re.sub(re.escape(display),lambda match:speech,t,flags=re.I)
 return re.sub(r'[^0-9a-z가-힣]','',unicodedata.normalize('NFC',t).lower())
def main():
 a=argparse.ArgumentParser();a.add_argument('role',choices=['voice','mix']);args=a.parse_args()
 revision_guard()
 control=read(R/'shared/publishing/video-production-control.json')
 assert control.get('selectedShortVideo')==P.name and control.get('shortsDirectSelection',{}).get('selectedRevision')==REVISION
 j=read(P/'project.json');source=VOICE if args.role=='voice' else L/'final-mix.m4a';digest=sha(source)
 report=L/f'asr-{args.role}-{digest[:12]}.json';asr=read(report)
 assert asr['sha256']==digest and asr['fullInput'] and asr['rawRecognitionUnmodified'] and not asr['expectedTextPromptUsed']
 lines=[line for scene in read(P/'script/narration.ko.json')['scenes'] for line in scene['lines']];expected=norm(''.join(lines));actual=norm(asr['text']);ops=difflib.SequenceMatcher(None,expected,actual,autojunk=False).get_opcodes()
 differences=[dict(kind=tag,expected=expected[a:b],actual=actual[c:d],expectedRange=[a,b],actualRange=[c,d],contextExpected=expected[max(0,a-12):b+12],contextActual=actual[max(0,c-12):d+12]) for tag,a,b,c,d in ops if tag!='equal']
 report=dict(schemaVersion=1,role=args.role,input=str(source.relative_to(R)).replace('\\','/'),sha256=digest,fullAsrReport=str(report.relative_to(R)).replace('\\','/'),fullAsrSha256=sha(report),expectedText=' '.join(lines),actualText=asr['text'],normalizedExact=expected==actual,characterSimilarity=asr['similarity'],allFullTextDifferences=differences,rawAsrPreserved=True,expectedPromptUsed=False,normalizationAliases=read(P/'script/clauses.json').get('pronunciationAliases',{}),leadingEndingComplete=(expected[:15]==actual[:15] and expected[-15:]==actual[-15:]),leadingEndingMethod='Actual complete recognized beginning and ending match expected15normalizedcharacters; middle differences preserved separately.',status='full-text-exact; human-listening-pending' if not differences else 'full-text-differences; targeted-context-review-required',humanListening='pending',pronunciation='pending')
 target=L/f'asr-{args.role}-comparison.json'
 if target.exists():assert read(target)==report,'Preserve previous different comparison'
 else:target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
