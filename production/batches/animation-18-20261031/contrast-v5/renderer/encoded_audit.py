"""Sample each completed episode's current silent plates; no full-watch claim."""
from sources import *
from PIL import Image,ImageDraw
PREFERRED={'A01':'walk','A02':'combat','A04':'anticipation','A05':'impact','A06':'control','A07':'far','A08':'overview','A09':'fist','A10':'height','A11':'kick','A12':'mouth','A13':'tool','A14':'blend','A15':'keys','A16':'active','A17':'hint','A18':'curves'}

def run(episodes=None):
    selected=H/'integration-manifest.json'
    p=read(selected if selected.exists()else H/'replacement-plan.json');out=B/'local/contrast-v5/encoded-qa';out.mkdir(exist_ok=True,parents=True)
    evidence=[];report=out/'encoded-audit.json'
    previous={e['episode']:e for e in read(report).get('samples',[])}if report.exists()else{}
    for e in p['episodes']:
        ep=e['id']
        if episodes and ep not in episodes:continue
        choices=[r for r in e['rows']if r['mode']=='analysis'and r['key']==PREFERRED[ep]and (R/r['output']).with_suffix('.json').exists()]
        if not choices:continue
        r=max(choices,key=lambda x:(x.get('phaseModeAtTail',False),x['frames']))
        f=R/r['output'];receipt=read(f.with_suffix('.json'));assert sha(f)==receipt['sha256']
        cached=previous.get(ep)
        if cached and cached['rowId']==r['id']and cached['plateSHA256']==receipt['sha256']and all((R/s['path']).exists()for s in cached['samples']):
            evidence.append(cached);print(ep,'unchanged encoded QA reused',flush=True);continue
        # Only one selected current plate is fully decoded; parent decodes final masters.
        subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(f),'-f','null','-'],check=True)
        samples=[]
        for label,ratio in [('analysis',.48),('tail',.9)]:
            frame=min(r['frames']-1,round(r['frames']*ratio));t=frame/60;dest=out/f'{ep}-{label}.png'
            subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-ss',str(t),'-i',str(f),'-frames:v','1',str(dest)],check=True)
            with Image.open(dest)as im:im.resize((375,211),Image.Resampling.LANCZOS).save(dest.with_name(dest.stem+'-375.png'))
            samples.append({'name':label,'frame':frame,'path':str(dest.relative_to(R)).replace('\\','/')})
        evidence.append({'episode':ep,'rowId':r['id'],'plateSHA256':receipt['sha256'],'decodedFrames':r['frames'],'samples':samples,'audio':False,'visualReview':'pending-model-image-inspection','fullVideoWatch':False})
        print(ep,'encoded samples ready',flush=True)
    for page in range((len(evidence)+7)//8):
        sheet=Image.new('RGB',(1500,844),'#080c0a')
        for j,e in enumerate(evidence[page*8:page*8+8]):
            for k,s in enumerate(e['samples']):
                with Image.open(R/s['path'])as im:sheet.paste(im.resize((375,211)),((j%4)*375,(j//4)*422+k*211))
        sheet.save(out/f'encoded-contact-{page+1}.png')
    (out/'encoded-audit.json').write_text(json.dumps({'scope':'Selected silent-plate decode and static encoded samples only. No audio/full-master or final changed-caption approval.','samples':evidence},ensure_ascii=False,indent=2),'utf8')
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--episodes',nargs='*');a=ap.parse_args();run(a.episodes)
