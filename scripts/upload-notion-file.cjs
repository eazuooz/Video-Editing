// Read a short-lived Notion MCP upload descriptor from stdin. Never persist or log credentials.
// Input: {upload_url, upload_headers, upload_form_field, file, content_type?}.
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  let input = '';
  for await (const chunk of process.stdin) input += chunk;
  const config = JSON.parse(input.trim().replace(/^\uFEFF/, ''));
  const url = new URL(config.upload_url);
  if (url.origin !== 'https://api.notion.com' || !/^\/v1\/mcp\/file_uploads\/[\da-f-]+\/send$/.test(url.pathname)) throw Error('Unexpected Notion upload endpoint');
  const file = fs.readFileSync(config.file);
  if (file.length > 20 * 1024 * 1024) throw Error('Single-part upload exceeds 20 MiB');
  const form = new FormData();
  form.append(config.upload_form_field || 'file', new Blob([file], {type: config.content_type || 'image/jpeg'}), path.basename(config.file));
  // Exactly one POST, with all headers returned by Notion. No automatic retry.
  const response = await fetch(url, {method: 'POST', headers: config.upload_headers, body: form, redirect: 'error'});
  const result = await response.json();
  if (!response.ok) throw Error(`Notion upload HTTP ${response.status}: ${result.code || 'failed'}`);
  console.log(JSON.stringify(result));
})().catch(error => { console.error(error.message); process.exitCode = 1; });
