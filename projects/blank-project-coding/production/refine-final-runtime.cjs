const fs=require('fs'),path=require('path');const file=path.join(__dirname,'../examples/app.js');let s=fs.readFileSync(file,'utf8');
s=s.replace('model.board=game.board;model.cells=game.cells;', 'if(model.board!==game.board){model.board.splice(0,model.board.length,...game.board.map(r=>[...r]));game.board=model.board;}if(model.cells!==game.cells){model.cells.splice(0,model.cells.length,...game.cells.map(c=>[...c]));game.cells=model.cells;}');
s=s.replace('<div>current = ${e.current}</div><table>', '<div>current = ${e.current}</div>${e.selected?`<div>current.value = ${e.selected.value} / next = ${e.selected.next}</div>`:""}<table>');
fs.writeFileSync(file,s);
