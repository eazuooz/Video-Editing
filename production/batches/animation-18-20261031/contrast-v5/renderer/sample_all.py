from compose import *
SAMPLES={'A01':('walk',50),'A02':('combat',96),'A04':('anticipation',13),'A05':('impact',76),'A06':('control',60),
         'A07':('far',86),'A08':('overview',171),'A09':('fist',81),'A10':('height',70),'A11':('kick',18),'A12':('mouth',35),
         'A13':('tool',70),'A14':('blend',49),'A15':('keys',64),'A16':('active',32),'A17':('hint',34),'A18':('curves',28)}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--episodes',nargs='*');a=ap.parse_args();rows=[];out=B/'local/contrast-v5/renderer-previews'
    for ep,(key,n)in SAMPLES.items():
        if a.episodes and ep not in a.episodes:continue
        try:
            preview(ep,key,n,out);rows.append((ep,key));print(ep,'sampled',flush=True)
        except (AssertionError,FileNotFoundError)as e:print(ep,'not ready',str(e),flush=True)
    for page in range((len(rows)+7)//8):
        sheet=Image.new('RGB',(1500,844),BG)
        for j,(ep,key)in enumerate(rows[page*8:page*8+8]):
            with Image.open(out/f'{ep}-{key}-compare.png')as im:sheet.paste(im.resize((375,211)),((j%4)*375,(j//4)*422))
            with Image.open(out/f'{ep}-{key}-stages.png')as im:sheet.paste(im.resize((375,211)),((j%4)*375,(j//4)*422+211))
        sheet.save(out/f'contact-{page+1}.png')
