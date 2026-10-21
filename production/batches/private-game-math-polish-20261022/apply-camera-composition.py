"""Bind inspected camera diagram versions without replacing baseline clips."""
from polish_common import *
e=Episode('M16');e.authorized()
render=read(e.H/'camera-legibility-render.json');comp=read(e.H/'composition-polish.json')
assert render['timelineSha256']==comp['timelineSha256']==sha(e.P/'production/timeline.json')
assert set(render['scenes'])=={s['id'] for s in e.T['scenes'] if s['classification']=='explanation'}
for sid,entry in render['scenes'].items():
 path=R/entry['path'];assert sha(path)==entry['sha256'];e.verify(path,entry['frames'])
 comp['inputs'][sid]={k:entry[k] for k in ['path','sha256','reason']}
comp['diagramPolish']=rel(e.H/'camera-legibility-render.json')
comp['internalVisualQa']='pending'
save(e.H/'composition-polish.json',comp)
