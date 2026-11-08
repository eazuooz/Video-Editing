"""Bind the preserved narration sentences to exact existing caption boundaries.

This reads metadata only. It neither synthesizes speech nor edits an old master.
Every normalized character must match in order; an ambiguous partial cue is
recorded and may not be used as a splice boundary.
"""
from pathlib import Path
import json,re,hashlib

H=Path(__file__).resolve().parent
R=H.parents[3]

def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p): return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def norm(s): return ''.join(c.lower() for c in s if c.isalnum())
def seconds(s):
    h,m,z=s.replace(',','.').split(':')
    return int(h)*3600+int(m)*60+float(z)
def cues(p):
    rows=[]
    for block in re.split(r'\n\s*\n',Path(p).read_text('utf-8-sig').strip()):
        ls=block.splitlines();a,b=map(seconds,ls[1].split(' --> '))
        rows.append(dict(start=a,end=b,text='\n'.join(ls[2:])))
    return rows

def main():
    plans=read(H/'script-migration-plan.json')['records']
    bases={r['id']:r for r in read(H/'baseline-review-manifest.json')['records']}
    records=[]
    for ep in plans:
        baseline=bases[ep['id']]
        ko_path=R/next(f['path'] for f in baseline['files'] if f['kind']=='ko.srt')
        sents=read(R/ep['baselineKo'])['scenes'];cs=cues(ko_path)
        a=''.join(norm(' '.join(s['lines'])) for s in sents)
        b=''.join(norm(c['text']) for c in cs)
        assert a==b,(ep['id'],'baseline narration and cues must match exactly',len(a),len(b))
        cursor=0;cue_ranges=[]
        for i,c in enumerate(cs):
            n=len(norm(c['text']));cue_ranges.append((cursor,cursor+n,i));cursor+=n
        cursor=0;rows=[]
        for s in sents:
            end=cursor+len(norm(' '.join(s['lines'])))
            touched=[x for x in cue_ranges if x[0]<end and x[1]>cursor]
            lo,hi=touched[0][2],touched[-1][2]
            rows.append(dict(id=s['id'],text=' '.join(s['lines']),cueStartIndex=lo,cueEndIndexExclusive=hi+1,
                             startSeconds=cs[lo]['start'],endSeconds=cs[hi]['end'],
                             startsAtCueBoundary=touched[0][0]==cursor,endsAtCueBoundary=touched[-1][1]==end))
            cursor=end
        # Caption timings identify speech, not automatically a safe PCM edge.
        # Original silence/word alignment must still be checked before a splice.
        records.append(dict(id=ep['id'],slug=ep['slug'],baselineKoSha256=sha(R/ep['baselineKo']),
                            srtPath=ko_path.relative_to(R).as_posix(),srtSha256=sha(ko_path),
                            normalizedTextExact=True,sentences=rows))
    out=dict(status='exact-text-caption-mapping',fps=60,sampleRate=48000,
             audioBoundaryReview='pending for selected changed ranges',records=records)
    save(H/'baseline-sentence-timing.json',out)
    print(json.dumps({'episodes':len(records),'sentences':sum(len(e['sentences']) for e in records),
                      'partialCueBoundaries':sum(not(s['startsAtCueBoundary'] and s['endsAtCueBoundary']) for e in records for s in e['sentences'])}))

if __name__=='__main__': main()
