const fs = require('node:fs');
const path = require('node:path');
const base = path.resolve(__dirname, '..');
const draft = JSON.parse(fs.readFileSync(path.join(base, 'script/draft-bilingual.json'), 'utf8'));
const manifest = JSON.parse(fs.readFileSync(path.join(base, 'project.json'), 'utf8'));
for (const [language, index] of [['ko', 0], ['en', 1]]) {
  const scenes = draft.scenes.map(s => ({id:s.id, title:s[language === 'ko' ? 'titleKo' : 'titleEn'], lines:s.lines.map(pair => {
    if (pair.length !== 2 || pair.some(line => !line.trim())) throw Error('Missing bilingual paragraph in ' + s.id);
    return pair[index];
  })}));
  fs.writeFileSync(path.join(base, `script/narration.${language}.json`), JSON.stringify({title:manifest.titles[language], status:draft.status, scenes}, null, 2) + '\n');
}
console.log(`Prepared independent draft: ${draft.scenes.length} scenes / ${draft.scenes.reduce((n,s)=>n+s.lines.length,0)} paired paragraphs. Action/cut review required before TTS.`);
