from render import DIRECTORY, EDITS, SOURCES, WORK, editor
from check import check
from pathlib import Path
import sys

def verify(n):
    row=SOURCES[n]
    samples=[2.4,17.4]
    if n in (5,10):
        delivery=editor.read(Path(row['finalDirectory']).parent/DIRECTORY/'delivery.json')
        insert=EDITS[n]['insertFrame']/60
        samples=([3,18,27] if n==5 else [3,28])
        cues=editor.srtread(Path(row['finalDirectory']).parent/DIRECTORY/'captions.ko.srt')
        for a,b,line in cues:
            if insert<=a<insert+delivery['additionFrames']/60 and (not samples or a-samples[-1]>3):
                samples.append((a+b)/2)
    check(n,row,DIRECTORY,samples)

if __name__=='__main__':
    for n in map(int,sys.argv[1:]):verify(n)
