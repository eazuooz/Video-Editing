"""Bind the selected reviewed mesh outputs, preserving original source clips."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);assert e.id in ['M19','M20'];e.authorized()
render=read(e.H/'mesh-legibility-render.json');comp=read(e.H/'composition-polish.json')
assert render['timelineSha256']==comp['timelineSha256']==sha(e.P/'production/timeline.json')
assert set(render['scenes'])=={s['id'] for s in e.T['scenes'] if s['classification']=='explanation'}
for sid,entry in render['scenes'].items():
 path=R/entry['path'];assert sha(path)==entry['sha256'];e.verify(path,entry['frames'])
 comp['inputs'][sid]={k:entry[k] for k in ['path','sha256','reason']}
comp['diagramPolish']=rel(e.H/'mesh-legibility-render.json');comp['internalVisualQa']='pending'
save(e.H/'composition-polish.json',comp)
