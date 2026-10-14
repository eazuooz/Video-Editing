"""Prepare one encoded-sample worker; execution requires actual render closure."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
p=B/'extract-orientation-07b-tracked-pixels-v1.py';assert not p.exists()
s=(B/'extract-orientation-03b-tracked-pixels-v1.py').read_text('utf-8').replace('03b','07b')
s=s.replace('[3.06,6.84,11.06,12.66,13.56,14.28,15.2,16.04,21.42,25.14,25.5,26.1]','[4.125,7.555,8.76,9.72,10.62,10.94,12.08,12.37,13.1,14.2,14.82,15.72,16.7166666667,21.105,27.1383333333,29.4533333333,31.5133333333,33.1]')
compile(s,str(p),'exec');p.write_text(s,'utf-8');print('07b encoded pixel worker prepared; not executed.')
