"""Repair only existing readouts with unsupported math glyphs; CPU/Pillow only."""
from pathlib import Path
import argparse,importlib.util,json,hashlib
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
H=Path(__file__).parent;ROOT=H.resolve().parents[3]
CAP=ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v6/spatial-clips'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if not a.run:ap.print_help();return
    spec=importlib.util.spec_from_file_location('readout_glyphs',H/'spatial-readouts.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    plan,_=m.prepare();shots={s['id']:s for s in read(m.CATALOG)['shots']}
    chars={False:set(),True:set()};cmap={b:set(TTFont(str(m.BOLD_PATH if b else m.FONT_PATH)).getBestCmap()) for b in [False,True]}
    for shot in shots.values():
        for n in range(61):
            for panel in m.layout(shot,m.evaluated(shot,n/60)):
                for row in panel['rows']:chars[row['bold']].update(row['text'])
    missing={b:sorted(ord(c) for c in cs if not c.isspace() and ord(c) not in cmap[b]) for b,cs in chars.items()};assert not any(missing.values()),missing
    outs=CAP/'readouts/outputs.json';oldsha=sha(outs);data=read(outs);q=CAP/'review';proof=read(q/'outputs.json')
    changed=[r['id'] for r in data['outputs'] if any(g in (ROOT/r['assFile']).read_text(encoding='utf-8-sig') for g in ['\u2212','\u2016','\u2248'])]
    unchanged={r['id']:r['files'] for r in data['outputs'] if r['id'] not in changed};count=0
    for key in changed:
        row=next(r for r in data['outputs'] if r['id']==key);shot=shots[key];states=[json.loads(s) for s in (CAP/(key+'.anchors.ndjson')).read_text().splitlines()];ass=m.HEADER
        for f,s in enumerate(states):ass+=m.ass_frame(f,m.layout(shot,m.evaluated(shot,s['normalizedTime'],s)));count+=1
        (ROOT/row['assFile']).write_text(ass,encoding='utf-8-sig')
        for label,f,source in [('first',0,CAP/(key+'.first.png')),('mid',len(states)//2,q/(key+'.mid.png')),('last',len(states)-1,CAP/(key+'.last.png'))]:
            display=m.layout(shot,m.evaluated(shot,states[f]['normalizedTime'],states[f]));dest=q/(key+'.'+label+'.display.png');m.still(source,dest,display)
            if label!='mid':m.still(source,CAP/'readouts'/(key+'.'+label+'.png'),display)
        rec=next(r for r in proof['clips'] if r['id']==key)
        for d in rec['displays']:d['sha256']=sha(ROOT/d['path'])
        for f in row['files']:f['sha256']=sha(ROOT/f['path'])
    for files in unchanged.values():
        for f in files:assert sha(ROOT/f['path'])==f['sha256']
    repair={'reason':'Unsupported math glyphs in actual Malgun cmap; same supported notation in Pillow and ASS',
        'replacements':{'U+2212':'- (minus)','U+2016':'|| (norm double bars)','U+2248':'약 (approximate); p≈90° becomes p=90° 부근'},
        'affectedIds':changed,'actualFramesRevalidated':count,'unaffectedOutputCount':49-len(changed),'unaffectedFilesSHAIdentical':True,'previousOutputsSha256':oldsha,'implementationSha256':sha(H/'spatial-readouts.py')}
    data['inputs']['planSha256']=sha(H/'spatial-readout-plan.json');data.setdefault('targetedReadoutRepairs',[]).append(repair);save(outs,data)
    font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',22);pages=[]
    for pg in proof['pages']:
        if not any(k in changed for k in pg['shotIds']):continue
        group=[next(c for c in proof['clips'] if c['id']==k) for k in pg['shotIds']];w=375 if pg['mobile375'] else 640;hh=211 if pg['mobile375'] else 360
        board=Image.new('RGB',(w*3,(hh+32)*len(group)),'#080b0d');draw=ImageDraw.Draw(board)
        for r,c in enumerate(group):
            for col,d in enumerate(c['displays']):
                y=r*(hh+32);draw.text((col*w+8,y+2),c['id']+' '+['first','middle','last'][col],font=font,fill='#e8cf83')
                with Image.open(ROOT/d['path']) as im:board.paste(im.resize((w,hh),Image.Resampling.LANCZOS),(col*w,y+32))
        dest=ROOT/pg['path'];board.save(dest,quality=94);pg['sha256']=sha(dest);pages.append(pg['path'])
    proof['readoutOutputsSha256']=sha(outs);proof.setdefault('targetedRepair',[]).append(repair);save(q/'outputs.json',proof)
    audit={'schemaVersion':1,'fontFiles':[{'file':str(p),'sha256':sha(p)} for p in [m.FONT_PATH,m.BOLD_PATH]],'states':2989,'allGlyphsSupported':True,'missingCodepoints':missing,'bodyCodepoints':sorted(ord(c) for c in chars[False]),'boldCodepoints':sorted(ord(c) for c in chars[True]),'repair':repair,'changedPages':pages,'reviewNativeMobile':'pending direct image viewing','original49CaptureUnchanged':True}
    save(H/'spatial-readout-glyph-review.json',audit)
    print(json.dumps({'glyphUnionPassed':True,'affectedIds':changed,'actualFramesRevalidated':count,'unaffectedReused':49-len(changed),'changedPages':len(pages)}),flush=True)
if __name__=='__main__':main()
