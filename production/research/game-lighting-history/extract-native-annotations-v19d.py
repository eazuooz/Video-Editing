"""Only the corrected camera-cut/inset pilot; preserve the reviewed DLSS pixels."""
from pathlib import Path
source = Path(__file__).with_name('extract-native-annotations-v19c.py').read_text('utf-8')
source = source.replace('v19c', 'v19d').replace("cuts=plan['cuts'];", "cuts=plan['cuts'][:1];")
source = source.replace('277,278,279,320,321', '277,278,279,298,299,300,301,320,321')
exec(compile(source, str(Path(__file__)), 'exec'))
