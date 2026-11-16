"""Reuse29 identical reviewed rasters; rebuild only3 changed game annotations."""
from pathlib import Path
import ast, bisect, importlib.util, json
from PIL import Image, ImageDraw

H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selected_reference_renderer_v77',H/'run-lockon-user-revision-v74.py')
film=importlib.util.module_from_spec(spec);spec.loader.exec_module(film)
R=film.BASE.parent;OUT=R/'preencode-reference-v77';assert not OUT.exists();OUT.mkdir()
old=film.read(R/'preencode-reference-v72/evidence.json')
assert (H/'run-lockon-user-revision-v74.py').read_text('utf8').replace('v74','v70')==(H/'run-lockon-user-revision-v70.py').read_text('utf8')
oldtree=ast.parse((H/'lockon-revision-overlays-v70.py').read_text('utf8'))
newtree=ast.parse((H/'lockon-revision-overlays-v74.py').read_text('utf8'))
oldfn=next(x for x in oldtree.body if isinstance(x,ast.FunctionDef)and x.name=='annotate')
newfn=next(x for x in newtree.body if isinstance(x,ast.FunctionDef)and x.name=='annotate')
assert len(oldfn.body)==len(newfn.body)==4
for index in [0,1,3]:assert ast.dump(oldfn.body[index])==ast.dump(newfn.body[index])
assert ast.dump(oldfn.body[2].orelse[0])==ast.dump(newfn.body[2].orelse[0])
prep,reason=film.prepare('pilot');assert prep and reason is None
composer=film.layout.Composer(film.P.name);beats=prep['identity']['beats'];cues=prep['identity']['captionCues'];records=[];readers={};rebuilt=[];reused=[]
for row in old['records']:
    seconds=row['frame']/60;b=beats[bisect.bisect_right([x['start']for x in beats],seconds)-1]
    if b.get('annotation')!='two-stalfos-waiting':
        for key in ['image','mobile']:assert film.pin(row[key]['path'])==row[key]
        records.append(row);reused.append(row['cueIndex']);continue
    assert b['kind']=='game';elapsed=seconds-b['start'];key=b['source']['path']
    if key not in readers:readers[key]=film.GameReader(key)
    source_seconds=b['sourceStartSeconds']+elapsed;pixels,pts=readers[key].frame(source_seconds)
    im=composer.base(b['label']);height=round(984*pixels.height/pixels.width)
    im.paste(pixels.resize((984,height),Image.Resampling.LANCZOS),(0,396+(984-height)//2))
    film.overlays.annotate(im,b,source_seconds)
    cue=cues[row['cueIndex']];assert cue['ko']==row['caption'];composer.captioned(im,cue['ko'])
    full=OUT/f"cue-{row['cueIndex']:03}.png";im.save(full)
    small=OUT/f"cue-{row['cueIndex']:03}-375.jpg";im.resize((375,667),Image.Resampling.LANCZOS).save(small,quality=96)
    records.append(dict(row,image=film.pin(full),mobile=film.pin(small),source=dict(kind='game',sourcePts=pts)))
    rebuilt.append(row['cueIndex'])
for reader in readers.values():reader.close()
assert rebuilt==[18,19,20]and len(reused)==29 and len(records)==32
film.save(OUT/'evidence.json',dict(fingerprint=prep['fingerprint'],records=records,
    reusedByteExactCompositions=reused,recomposedActualGameFrames=rebuilt,
    previousReferenceEvidence=film.pin(R/'preencode-reference-v72/evidence.json'),
    derivation='Renderer raster logic identical after version/path renaming. Overlay AST changes only the two-stalfos-waiting branch; all other cases are identical.',
    modelStarted=False,fullRenderStarted=False,publishingApproved=False))
for start in range(0,32,8):
    sheet=Image.new('RGB',(1500,1394),'#172420');d=ImageDraw.Draw(sheet)
    for j,row in enumerate(records[start:start+8]):
        x=j%4*375;y=j//4*697;d.text((x+5,y+5),str(row['cueIndex'])+' '+format(row['seconds'],'.2f')+'s',fill='white');sheet.paste(Image.open(row['mobile']['path']),(x,y+30))
    sheet.save(OUT/f'contact-{start//8:02}.jpg',quality=95)
print(json.dumps(dict(reused=29,rebuilt=rebuilt,fingerprint=prep['fingerprint'],evidence=film.pin(OUT/'evidence.json'))))
