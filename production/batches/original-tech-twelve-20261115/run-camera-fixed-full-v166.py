from pathlib import Path
import importlib.util
p=Path(__file__).with_name('camera-fixed-capture-runtime-v166.py');s=importlib.util.spec_from_file_location('fixed166_runtime',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
if __name__=='__main__':m.main('full',__file__)
