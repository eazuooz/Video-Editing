"""Adapt the reviewed additive lecture pipeline; new source paths stay explicit."""
from pathlib import Path
B=Path(__file__).parent
def adapted(name):
    text=(B/name.replace('polygons','planes')).read_text(encoding='utf8')
    for before,after in [
        ('game-math-planes-barycentric','game-math-polygons-triangulation'),
        ('game-math-plane-distances-v2','game-math-polygon-centers-v2'),
        ('game-math-triangle-addresses-v2','game-math-polygon-partition-v2'),
        ('planes_additions','polygons_additions'),
        ('planes','polygons')]:text=text.replace(before,after)
    return text

text=adapted('prepare-polygons-timing.py')
# v3 overrides only two ambiguous new phrases; keep v2 evidence and93% gate.
assert "polygons-retakes-v3-tts-map.json" in text
(B/'prepare-polygons-timing.py').write_text(text,encoding='utf8')

text=adapted('plan-polygons-episodes.py')
start=text.index("                segments=[{'in':x,'maxSeconds':y-x} for x,y in scene['intervals']]")
end=text.index('                sentence_cues=slot',start)
text=text[:start]+'''                segments=copy.deepcopy(scene['sourceSegments'])
                assert len(segments)==len(scene['intervals'])
                for seg,(begin,end) in zip(segments,scene['intervals']):
                    assert seg['in']==begin and abs(seg['maxSeconds']-(end-begin))<1e-8
                    source=ROOT/seg['sourceFile']
                    assert hashlib.sha256(source.read_bytes()).hexdigest()==seg['sourceSha256']
                group_lines=scene.get('sourceGroupStartsAtLines')
                if group_lines:
                    assert len(group_lines)==len(segments)
                    for seg,line in zip(segments,group_lines):
                        if line is not None:seg['startsAtLine']=line
'''+text[end:]
start=text.index("                slot['cut']={'sourceId':scene['sourceId']")
end=text.index('\n        rows.append',start)
text=text[:start]+'''                slot['cut']={'sourceId':scene['sourceId'],'sourceFile':scene['sourceFile'],'sourceSegments':segments,'maximumSeconds':scene['maximumSeconds'],'sourceAudioUsed':False,'sourceSpeed':1,'annotationPlan':scene['annotation']}'''+text[end:]
assert 'TPkvx2W8CV8' not in text
(B/'plan-polygons-episodes.py').write_text(text,encoding='utf8')
(B/'render-polygons-explanations.py').write_text(adapted('render-polygons-explanations.py'),encoding='utf8')
text=adapted('create-polygons-overlay.py')
for before,after in [
 ("'left','right','red','blue','teal'","'left','right','red','blue','teal','yellow'"),
 ("['red','blue','teal']","['red','blue','teal','yellow']"),
 ("{'red':red_at,'blue':blue_at,'teal':teal_at}","{'red':red_at,'blue':blue_at,'teal':teal_at,'yellow':yellow_at}"),
 ("{'red':0,'blue':0,'teal':0}","{'red':0,'blue':0,'teal':0,'yellow':0}"),
 ("{'red':False,'blue':False,'teal':False}","{'red':False,'blue':False,'teal':False,'yellow':False}"),
 ("('red','#ef5350')]","('red','#ef5350'),('yellow','#ffd54f')]"),
 ("track.get('closed',True)","track.get('closed',False) or key in ['blue','yellow']"),
 ("if mapped>=reveal-.1:return mapped","if mapped>=max(reveal,fallback)-.1:return mapped"),
 ("'blue':blue_at,'teal':teal_at},'pointsSource'","'blue':blue_at,'teal':teal_at,'yellow':yellow_at},'pointsSource'")]:text=text.replace(before,after)
anchor=" track_reveals={}"
text=text.replace(anchor," yellow_at=spoken(spec.get('yellowKeyword','노란'),starts[spec.get('yellowAtLine',spec.get('revealAtLine',0))])\n"+anchor)
anchor="   if visible['teal']:text(a,z,[25,147],spec.get('tealLabel','청록: 관찰 부분의 비교 도형'),'#64ffda',15,True)"
text=text.replace(anchor,anchor+"\n   if visible['yellow']:text(a,z,[25,170],spec.get('yellowLabel','노랑: 보이는 빈 공간'),'#ffe082',15,True)")
text=text.replace("clear=i/60>=note_start", "clear=i/60>=note_start and not spec.get('omitMathNote',False)")
assert 'yellow_at' in text and 'polygons-annotation-tracks.json' in text
(B/'create-polygons-overlay.py').write_text(text,encoding='utf8')
(B/'build-polygons-episodes.py').write_text(adapted('build-polygons-episodes.py'),encoding='utf8')
print('Prepared current-hash timing, exact40:60 plan and measured Manim renderer.')
