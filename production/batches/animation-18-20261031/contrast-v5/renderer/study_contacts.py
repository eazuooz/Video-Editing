"""All used study variants, for bounded static visual audit before full assembly."""
from compose import *

def main():
    plan=read(H/'replacement-plan.json');out=B/'local/contrast-v5/study-audit';out.mkdir(parents=True,exist_ok=True);rows=[]
    for ep in plan['episodes']:
        for key in ep['sourceInputs']:
            eid=ep['id'];c=contract(eid,key);n=c['samples'][1]
            if (eid,key)in {('A08','overview'),('A05','impact'),('A02','combat')}:n=c['samples'][-1]
            p=out/f'{eid}-{key}.png'
            frame(eid,key,n,legend=True).resize((375,211),Image.Resampling.LANCZOS).save(p)
            rows.append({'episode':eid,'key':key,'frame':n,'file':str(p.relative_to(R)).replace('\\','/')});print(eid,key,flush=True)
    for page in range((len(rows)+7)//8):
        sheet=Image.new('RGB',(1500,480),BG);d=ImageDraw.Draw(sheet)
        for j,row in enumerate(rows[page*8:page*8+8]):
            x=(j%4)*375;y=(j//4)*240
            d.text((x+5,y+2),row['episode']+' / '+row['key'],font=font(18),fill=WHITE)
            with Image.open(R/row['file'])as im:sheet.paste(im,(x,y+28))
        sheet.save(out/f'studies-{page+1}.png')
    (out/'samples.json').write_text(json.dumps({'scope':'Every used study, one static source-composite sample each; not encoded or final-caption/full-motion review.','samples':rows},ensure_ascii=False,indent=2),'utf8')
if __name__=='__main__':main()
