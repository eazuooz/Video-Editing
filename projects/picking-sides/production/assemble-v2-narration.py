"""Assemble all12existing chunks only. Never invokes TTS or replaces preserved PCM."""
import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as r
import numpy as np
import soundfile as sf
r.np=np
r.sf=sf
r.configure_project('picking-sides')
r._apply_edge_fades=lambda wav,sr: wav  # preserve source PCM; final mixer handles transitions
r.assemble_outputs(r.load_jobs())
print('All12scene chunks assembled; current-hash ASR and final mix approval are still pending.')
