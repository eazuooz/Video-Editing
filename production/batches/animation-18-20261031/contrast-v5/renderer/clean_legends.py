"""Remove only the generic legend where its semantic colours do not apply.

A02's verified current/previous/path key is retained. Topic headings, actual
guides, per-picture labels, charts, subtitles and resolution/fps are untouched.
"""
from sources import *
from render_rows import ENC
from copy import deepcopy

def main():
    control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert control['renderAuthorized'] and control['fullLocalProductionAuthorized']
    plan=read(H/'replacement-plan.json');results=read(H/'observation-corrections.json');ext=read(H/'pacing-extension.json')
    assert results['status']=='rendered-current-silent-overrides' and ext['status']=='rendered-current-silent-override'
    fixed={r['id']:r for r in results['rows']};fixed.update({r['id']:r for r in ext['bodyOverrides']})
    vf='drawbox=x=480:y=106:w=1100:h=48:color=0x080c0a:t=fill'
    rows=[]
    for e in plan['episodes']:
        assert e['id'] in control['episodes'] and e['id']!='A03'
        if e['id']=='A02':continue
        for r0 in e['rows']:
            r=deepcopy(fixed.get(r0['id'],r0))
            if not r.get('showLegend'):continue
            source_file=R/r['output'];dest=source_file.parent/'topic-legends'/source_file.name;dest.parent.mkdir(exist_ok=True)
            sig=hashlib.sha256((sha(source_file)+vf+str(ENC)).encode()).hexdigest();receipt=dest.with_suffix('.json')
            old=read(receipt)if receipt.exists()else{}
            if not dest.exists()or old.get('signature')!=sig or old.get('sha256')!=sha(dest):
                subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-threads','4','-i',str(source_file),'-filter_threads','1','-vf',vf,'-an',*ENC,str(dest)],check=True)
                v=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(dest)]))['streams']
                assert len(v)==1 and(v[0]['width'],v[0]['height'],v[0]['avg_frame_rate'],int(v[0]['nb_frames']))==(1920,1080,'60/1',r['frames'])
                receipt.write_text(json.dumps({'signature':sig,'sha256':sha(dest),'frames':r['frames'],'sourceSha256':sha(source_file),'filter':vf,'audio':False},indent=2),'utf8')
            r.update(episode=e['id'],output=str(dest.relative_to(R)).replace('\\','/'),sha256=sha(dest),showLegend=False,
                overrideReason='Remove incorrect generic current/previous/path legend; keep actual topic-specific guides and labels.')
            rows.append(r);print(e['id'],r['id'],'topic legend cleaned',flush=True)
    (H/'legend-corrections.json').write_text(json.dumps({'schemaVersion':1,'status':'rendered-current-silent-overrides','scope':'Only generic top legend removal outsideA02; actual guides/topic labels retained.','filter':vf,'rows':rows},ensure_ascii=False,indent=2)+'\n','utf8')
if __name__=='__main__':main()
