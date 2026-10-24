#!/usr/bin/env node
'use strict';
// Signing stays separate and local. Publication is blocked by a stale Root feed.
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const policy=require('../root-edition/updater/fetch');
function verifyRootRelease(feed,build,bytes,key=fs.readFileSync(path.join(__dirname,'../updater-service/release-public.pem'))){
 if(!build.versions||typeof build.versions.root!=='string')throw Error('release-root-version-missing');
 const candidate=policy.verify(feed,key);
 if(candidate.version!==build.versions.root)throw Error('stale-root-feed: signed '+candidate.version+', release '+build.versions.root);
 if(bytes.length!==candidate.size||crypto.createHash('sha256').update(bytes).digest('hex')!==candidate.sha256)throw Error('root-package-mismatch');
 return candidate;
}
function main(args){
 const [tag,option]=args;
 if(!/^v\d{1,4}\.\d{1,4}\.\d{1,4}$/.test(tag||'')||args.length>2||(option&&option!=='--check-only'))throw Error('Usage: node scripts/publish-release.cjs vX.Y.Z [--check-only]');
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'cytv-release-'));
 const gh=argv=>execFileSync('gh',argv,{encoding:'utf8',maxBuffer:1024*1024,stdio:['ignore','pipe','pipe']});
 try{
  gh(['release','download',tag,'--pattern','root-update.json','--pattern','BUILD-INFO.json','--dir',folder]);
  const feed=JSON.parse(fs.readFileSync(path.join(folder,'root-update.json')));
  const build=JSON.parse(fs.readFileSync(path.join(folder,'BUILD-INFO.json')));
  if(build.tag!==tag)throw Error('release-tag-mismatch');
  const candidate=policy.verify(feed,fs.readFileSync(path.join(__dirname,'../updater-service/release-public.pem')));
  const filename=path.basename(new URL(candidate.url).pathname);
  gh(['release','download',candidate.release,'--pattern',filename,'--dir',folder]);
  verifyRootRelease(feed,build,fs.readFileSync(path.join(folder,filename)));
  process.stdout.write('Verified '+tag+': signed Root '+candidate.version+' and downloadable package match release metadata.\n');
  if(option!=='--check-only')process.stdout.write(gh(['release','edit',tag,'--draft=false','--latest']));
 }finally{fs.rmSync(folder,{recursive:true,force:true});}
}
module.exports={verifyRootRelease};
if(require.main===module){try{main(process.argv.slice(2));}catch(error){process.stderr.write(String(error.message)+'\n');process.exitCode=1;}}
