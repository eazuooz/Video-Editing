"""Redraw the actual Pixelbolt recipe at 56x20, without resizing old pixels."""
from pathlib import Path
H=Path(__file__).resolve().parent
source=(H/'make_ledger.py').read_text('utf8')
prefix=source[:source.index("poly([(2,13)")].replace('W,HGT=40,18','W,HGT=56,20').replace("pixelbolt-ledger'","pixelbolt-ledger-large'")
exec(prefix)
poly([(2,15),(27,18),(53,15),(54,18),(28,19),(3,18)],'s')
poly([(2,3),(22,1),(27,3),(29,3),(49,1),(53,3),(54,16),(29,18),(26,18),(1,16)],'c')
poly([(3,3),(22,2),(26,4),(26,16),(3,14)],'e');poly([(29,4),(49,2),(51,3),(52,14),(29,16)],'e')
poly([(4,3),(22,2),(25,4),(25,14),(4,13)],'p');poly([(30,4),(49,2),(50,3),(51,13),(30,14)],'p')
line(3,14,25,16,'t');line(30,16,52,14,'t');line(4,15,25,17,'b');line(30,17,52,15,'b')
line(26,4,26,16,'b');line(27,4,27,17,'d');line(28,4,28,17,'d');line(29,4,29,16,'t')
line(5,3,21,2,'h');line(31,4,48,2,'h')
for y in [5,7,9,11]:
 for a,b in [(5,9),(11,14),(16,18),(20,22)]:line(a,y,b,y,'i')
for y in [5,7,9,11,13]:
 for a,b in [(32,35),(37,41),(43,45),(47,49)]:
  if y==13 and a>41:continue
  line(a,y,b,y,'i')
dot(7,13,'a');dot(9,13,'a');dot(49,4,'a');dot(44,12,'a');dot(2,5,'a');dot(51,16,'a')
suffix=source[source.index('recipe={'):]
suffix=suffix.replace("'open-ledger'","'open-ledger-large'").replace("'open-ledger.pixel.json'","'open-ledger-large.pixel.json'").replace("'open-ledger.png'","'open-ledger-large.png'").replace("'open-ledger-execution.json'","'open-ledger-large-execution.json'")
suffix=suffix.replace("[40,18]","[56,20]").replace('original40x18','original56x20').replace('nearest20x','nearest preview').replace('left193,top130','left185,top130').replace('centre at213,139','centre at213,140')
exec(suffix)
