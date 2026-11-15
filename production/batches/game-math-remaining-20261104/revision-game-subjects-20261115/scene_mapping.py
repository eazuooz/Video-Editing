"""Durable narration-to-game-subject correspondence beside the existing plan."""
from subject_revision import *


def main():
    result=[]
    roles={
        'mario':'Recognizable Mario body → the tracked particle position; vectors and graphs use the same unchanged analytic state.',
        'kart':'Actual Luigi kart → the accelerating vehicle position; preserve the real kart game example before its explanatory model.',
        'forza':'The actual Forza car → tracked car position/velocity or circular-motion point, with explanatory values explicitly distinguished from game telemetry.',
        'beamng':'The actual BeamNG vehicle → simplified mass/body in the existing force or spring model; draw forces from that same state.',
        'town-context':'The actual Townscaper building → the mesh object entering the vertex/triangle/pixel pipeline; preserve the computed camera/geometry/code.',
        'doom-context':'The actual Doom 3 metal wall → the adjacent surface-normal/normal-data model; do not claim the illustration recovers the original game shader.'}
    for eid,e in EPISODES.items():
        byscene={}
        for t in tracks(e):
            s=next(s for s in e['scenes'] if s['scene']==t['scene'])
            row=byscene.setdefault(t['scene'],dict(episode=eid,scene=t['scene'],speech=s['speech'],mode=t['mode'],asset=t['asset'],intervals=[],role=roles[t['asset']]))
            row['intervals'].append([t['start'],t['end']])
            if eid=='M24' and t['scene'] in ('021','023','030'):
                row.update(asset=None,role='Remove the unrelated character. The preserved pressure/utility/notation diagram itself explains this non-character quantity.')
            if t['mode']=='portrait':row['role']='Actual Mario elbow indicated on the image → the independently animated joint/skin-weight model. The right-hand model is not measured Mario rig data.'
            if eid=='M23' and t['scene']=='050':row['role']='Actual Mario character → the adjacent skinning / surface-normal / pixel-colour flow. Illustration of the existing narrated combination, not recovered original game shader or skin data.'
            if t['mode']=='pipeline-clear':row.update(asset=None,role='Remove unrelated decorative knight while retaining the complete native bright code; corresponding Townscaper object and actual game examples remain in adjacent passages.')
        result.extend(byscene.values())
        for key,sids,asset,title,meaning,viewport in CONTEXTS:
            if key==eid:
                for sid in sids:
                    s=next(s for s in e['scenes'] if s['scene']==sid)
                    result.append(dict(episode=eid,scene=sid,speech=s['speech'],asset=asset,role=meaning,viewport=viewport,representation='Actual game-recording screenshot beside its unchanged mathematical representation; not internal game-algorithm evidence.'))
    save(HERE/'scene-mapping.json',dict(scope=list(EPISODES),rows=result,
        reusedM21='Already uses sphere/sampled-surface vectors rather than an unrelated robot; keep its verified 79-scene result.',
        explicitException=dict(episode='M27',scene='010',reason='Preserved narration explicitly describes a robot, elevator and sandwich thought experiment. Keep that literal object instead of silently contradicting the unchanged voice.'),
        principles=['Show the actual game object before its mathematical representation.','Use exactly the same analytic state for image, vectors and graph.','Keep necessary joint/surface/control-point geometry.','Preserve all useful narration, native game motion, audio and length.']))


if __name__=='__main__':main()
