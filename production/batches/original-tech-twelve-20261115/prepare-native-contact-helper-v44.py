from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'prepare-full-native-contacts-v44.py';assert not p.exists();s=(H/'prepare-full-native-contacts-v40.py').read_text(encoding='utf8').replace("ROOT=Path(__file__).resolve().parents[5]","ROOT=Path(__file__).resolve().parents[3]").replace('v40','v44');p.write_text(s,'utf8');assert Path(p).resolve().parents[3]==H.parents[2];print(str(p))
