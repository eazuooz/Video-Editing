"""Explicit root handoff starts one finite TTS/source-ASR slot, then exits."""
import argparse,importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_finite_voice_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--gpu-approved',action='store_true');x=p.parse_args()
 assert x.gpu_approved,'Explicit root serialized GPU handoff required'
 raise SystemExit(c.finite_voice_batch())
