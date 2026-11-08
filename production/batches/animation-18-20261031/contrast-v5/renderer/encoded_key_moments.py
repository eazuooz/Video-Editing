"""Inspect brief comparison intervals in already encoded final plates."""
from sources import *
from render_rows import state
from PIL import Image

def main():
    plan=read(H/'integration-manifest.json')
    qa=read(B/'local/contrast-v5/encoded-qa/encoded-audit.json')
    destination=B/'local/contrast-v5/encoded-qa'
    samples=[]
    for ep,target in [('A14',49),('A18',26)]:
        record=next(s for s in qa['samples']if s['episode']==ep)
        episode=next(e for e in plan['episodes']if e['id']==ep)
        row=next(r for r in episode['rows']if r['id']==record['rowId'])
        candidates=[(abs(state(ep,row,i)[0]-target),i,state(ep,row,i)[0])for i in range(row['newFrames'])if state(ep,row,i)[1]=='compare']
        _,frame,actual=min(candidates)
        path=destination/f'{ep}-key-moment.png'
        subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-ss',str(frame/60),'-i',str(R/row['output']),'-frames:v','1',str(path)],check=True)
        with Image.open(path)as im:im.resize((375,211),Image.Resampling.LANCZOS).save(path.with_name(path.stem+'-375.png'))
        samples.append({'episode':ep,'rowId':row['id'],'plateSHA256':sha(R/row['output']),'encodedFrame':frame,'actualSourceFrame':actual,'path':str(path.relative_to(R)).replace('\\','/'),'purpose':'Mid-transition rather than completed matching endpoint.','review':'pending-model-image-inspection'})
    (destination/'key-moments.json').write_text(json.dumps({'scope':'Actual encoded comparison moments only; no playback/listening claim.','samples':samples},ensure_ascii=False,indent=2)+'\n','utf8')
if __name__=='__main__':main()
