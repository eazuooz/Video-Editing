"""Cheap still preflight; not a delivery render or moving-output approval."""
import importlib.util,os
from pathlib import Path
p=Path(__file__).with_name('polygon-scenes.py')
spec=importlib.util.spec_from_file_location('polygon_recovery',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sid=os.environ['POLYGON_PREVIEW_SID']
limit=int(os.environ.get('POLYGON_PREVIEW_STATE_COUNT','999'))
if sid in m.STATES:m.STATES[sid]=m.STATES[sid][:limit]
parent=getattr(m,'Polish'+sid) if sid.isdigit() else m.RecoveredAddition
class Preview(parent):
 pass
Preview.sid=sid
