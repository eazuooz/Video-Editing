// The same audited, manifest-bound local HTTP player; keep the old review URL available.
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module');
const revision=path.basename(__dirname);
const text=fs.readFileSync(path.resolve(__dirname,'../fighters-v3/serve-review.cjs'),'utf8')
  .replaceAll('fighters-v3', revision).replaceAll('9238','9253');
const instance=new Module(__filename, module);
instance.filename=__filename;instance.paths=module.paths;instance._compile(text, __filename);
