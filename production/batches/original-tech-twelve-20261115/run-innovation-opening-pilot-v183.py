from pathlib import Path
import importlib.util
p=Path(__file__).with_name('innovation-opening-render-v183.py');s=importlib.util.spec_from_file_location('innovation183_pilot',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
if __name__=='__main__':m.entry(__file__,True)
