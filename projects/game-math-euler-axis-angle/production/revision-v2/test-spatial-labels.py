"""Bounded CPU-only semantic checks: projected overlap is not3Daxis equality."""
from pathlib import Path
import importlib.util,json,sys

sys.dont_write_bytecode=True
SOURCE=Path(__file__).with_name('render-spatial.py')
spec=importlib.util.spec_from_file_location('m04_spatial_compositor',SOURCE)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def point(name,pixel,math_world):
    return dict(name=name,inFrame=True,pixelTopLeft=dict(zip(('x','y','z'),(*pixel,5))),
        mathWorld=dict(zip(('x','y','z'),math_world)))

def state(body_direction,world_direction,pixel=(700,500),pair=False):
    world='worldA' if pair else 'world'
    return dict(anchors=[point('a.center',(500,500),(0,0,0)),point(world+'.origin',(500,500),(0,0,0)),
        point('a.bodyX',pixel,body_direction),point(world+'.x',pixel,world_direction)])

def main():
    cases=[]
    separate=module.label_candidates(state((0,1,0),(1,0,0)),False)
    assert len(separate)==2 and all(x['text']!='world/body x' for x in separate),separate
    cases.append('Same projected tip, different perpendicular3Ddirections: separate')
    same=module.label_candidates(state((1,0,0),(2,0,0)),False)
    assert len(same)==1 and same[0]['text']=='world/body x',same
    cases.append('Same positive3Ddirection despite different arrow lengths: merged')
    opposite=module.label_candidates(state((-1,0,0),(1,0,0)),False)
    assert len(opposite)==2,opposite
    cases.append('Opposite parallel directions: separate')
    bottom=module.label_candidates(state((0,1,0),(1,0,0),(500,710),True),True)
    assert len(bottom)==2 and abs(bottom[0]['y']-bottom[1]['y'])>=52,bottom
    assert max(x['y'] for x in bottom)<=710,bottom
    cases.append('Pair labels already at bottom clearance: second shifts upward52px')
    unknown=state((1,0,0),(1,0,0))
    unknown['anchors'][-1].pop('mathWorld')
    missing=module.label_candidates(unknown,False)
    assert len(missing)==2,missing
    cases.append('Missing mathematical direction: do not infer equality')
    long_label=module.label_candidates(state((1,0,0),(2,0,0),(1600,500)),False)
    assert len(long_label)==1 and long_label[0]['text']=='world/body x',long_label
    label=long_label[0]
    width=module.measured_axis_label_width(label['text'])
    assert label['x']+width*.5<=1015.000001,(label,width)
    assert label['x']-width*.5>=59.999999,(label,width)
    assert label['target']==(1600,500) and label['clampedToGeometryPane'],label
    cases.append('Measured actual bold40px merged label plus6px clearance stays atx≤1015; actual anchor retained for leader')
    print(json.dumps(dict(status='passed',cases=cases,gpuOrMediaJobsStarted=False),ensure_ascii=False))

if __name__=='__main__':main()
