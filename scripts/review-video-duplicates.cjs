// Pre-production topic review. Exact IDs and title matches flag candidates;
// an explicit content review is required before creating a batch project.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const queuePath = path.join(root, 'production/batches/sakurai-planning-game-design/queue.json');
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const args = process.argv.slice(2), slug = args[0];
const candidate = queue.items.find(item => item.slug === slug);
if (!candidate) throw Error('Expected a slug from the saved batch queue.');
const option = name => { const i = args.indexOf(name); return i < 0 ? null : args[i + 1]; };
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const normalized = value => String(value || '').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '');
const inputFiles = [], projects = [];
for (const entry of fs.readdirSync(path.join(root, 'projects'), {withFileTypes: true}).sort((a,b) => a.name.localeCompare(b.name))) {
  if (!entry.isDirectory() || entry.name === slug) continue;
  const base = `projects/${entry.name}`, manifestPath = `${base}/project.json`;
  if (!fs.existsSync(path.join(root, manifestPath))) continue;
  const manifest = JSON.parse(fs.readFileSync(path.join(root, manifestPath), 'utf8'));
  const record = {slug: entry.name, status: manifest.status, titles: manifest.titles || {}, videoId: manifest.publishing?.videoId || null, sceneTitles: [], sourceIdMatches: [], exactTitleMatch: false};
  // Additive revisions keep the old script and receipt. Review and hash the
  // active final script/receipt as well, so new chapters cannot evade review.
  const scriptPaths = new Set([`${base}/script/narration.ko.json`, manifest.paths?.script].filter(Boolean));
  const receiptPaths = new Set([`${base}/publishing/youtube-upload.json`, manifest.publishing?.receipt].filter(Boolean));
  const files = [...new Set([manifestPath, ...scriptPaths, `${base}/script/narration.en.json`, manifest.paths?.scriptEn, `${base}/planning/outline.md`, `${base}/sources/SOURCES.md`, `${base}/README.md`, ...receiptPaths].filter(Boolean))];
  for (const relative of files) {
    if (!fs.existsSync(path.join(root, relative))) continue;
    const text = fs.readFileSync(path.join(root, relative), 'utf8');
    inputFiles.push({path: relative, sha256: hash(text)});
    if (receiptPaths.has(relative)) {
      const receipt = JSON.parse(text); record.videoId ||= receipt.videoId || null;
    }
    if (scriptPaths.has(relative)) {
      const script = JSON.parse(text); record.scriptTitle = script.title;
      record.sceneTitles = [...new Set([...record.sceneTitles, ...(script.scenes || []).map(scene => scene.title)])];
    }
    // The batch reference ID, not shared game footage IDs, is compared.
    if (text.includes(candidate.sourceVideoId)) record.sourceIdMatches.push(relative);
  }
  const excluded = queue.excluded.find(item => item.slug === entry.name || item.alsoExistingProject === entry.name);
  const saved = queue.items.find(item => item.slug === entry.name);
  record.videoId ||= excluded?.youtube || saved?.videoId || null;
  if (saved?.sourceVideoId === candidate.sourceVideoId) record.sourceIdMatches.push('batch queue sourceVideoId');
  const candidateTitles = [candidate.sourceTitle, candidate.titleKo, candidate.titleEn].filter(Boolean).map(normalized);
  record.exactTitleMatch = [...Object.values(record.titles), record.scriptTitle].some(title => title && candidateTitles.includes(normalized(title)));
  record.scriptPath = manifest.paths?.script || `${base}/script/narration.ko.json`;
  record.scriptPaths = [...scriptPaths];
  projects.push(record);
}
const digest = hash(JSON.stringify({candidate: {slug, sourceVideoId: candidate.sourceVideoId, sourceTitle: candidate.sourceTitle}, inputFiles}));
const reportPath = path.join(root, `production/batches/sakurai-planning-game-design/preflight/${slug}.json`);
if (args.includes('--check')) {
  if (!fs.existsSync(reportPath)) throw Error('Run topic review and record its actual content/Studio evidence before project creation.');
  const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
  if (report.inputsDigest !== digest) throw Error('Existing project evidence changed: refresh duplicate review before creation.');
  if (report.verdict !== 'distinct' || !report.contentReview || !report.studioEvidence) throw Error('Content and current channel-upload review must establish a distinct topic before creation.');
  if (report.exactMatches.length) throw Error('Exact source/title match requires resolving or skipping the duplicate; never auto-produce it.');
  console.log(`${slug}: current pre-production content and Studio duplicate review passed.`);
  process.exit(0);
}
const exactMatches = projects.filter(project => project.sourceIdMatches.length || project.exactTitleMatch);
const decision = option('--decision'), reason = option('--reason'), studioEvidence = option('--studio-evidence');
if (decision && !['distinct', 'duplicate'].includes(decision)) throw Error('Decision must be distinct or duplicate.');
if (decision && (!reason || !studioEvidence)) throw Error('Record the actual content comparison and channel-upload evidence, not an assumed verdict.');
if (decision === 'distinct' && exactMatches.length) throw Error('Exact matches remain unresolved; inspect and skip a duplicate instead.');
const report = {schemaVersion: 1, candidate: {slug, sourceVideoId: candidate.sourceVideoId, sourceTitle: candidate.sourceTitle}, reviewedAt: new Date().toISOString(), inputsDigest: digest, inputFiles, existingProjects: projects, exactMatches, verdict: decision || 'pending-content-and-studio-review', contentReview: reason, studioEvidence, policy: 'Do not rely only on source ID, file name or first-six exclusion. Compare the viewer question, chapter claims and examples. Preserve already-created videos per user instruction.'};
fs.mkdirSync(path.dirname(reportPath), {recursive: true});
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({slug, verdict: report.verdict, existingProjects: projects.length, exactMatches: exactMatches.map(item => item.slug), report: path.relative(root, reportPath)}, null, 2));
