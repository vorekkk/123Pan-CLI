import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const cli = path.resolve('npm/cli.mjs');
const post = path.resolve('npm/postinstall.mjs');
for (const agent of ['codex','claude','cursor']) test(`install, conflict, force backup, uninstall: ${agent}`, () => {
 const dir=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'pan123-npm-')));
 try {
  const env={...process.env,HOME:dir,USERPROFILE:dir,CODEX_HOME:path.join(dir,'.codex')};
  const run=(...args)=>spawnSync(process.execPath,[cli,...args,'--agent',agent,'--scope','project'],{cwd:dir,env,encoding:'utf8'});
  assert.equal(run('install').status,0);
  assert.match(run('install').stdout,/unchanged/);
  const dest=path.join(dir,agent==='codex'?'.agents':'.'+agent,'skills','pan123-cli');
  fs.writeFileSync(path.join(dest,'SKILL.md'),'user edit');
  assert.notEqual(run('install').status,0);
  assert.notEqual(run('uninstall').status,0);
  assert.equal(run('install','--force').status,0);
  assert.ok(fs.readdirSync(path.dirname(dest)).some(x=>x.startsWith('pan123-cli.backup-')));
  assert.equal(run('uninstall').status,0);
  assert.equal(fs.existsSync(dest),false);
 } finally {fs.rmSync(dir,{recursive:true,force:true});}
});
test('local lifecycle does not install; global lifecycle installs into isolated home',()=>{
 const dir=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'pan123-post-')));
 try {
  const env={...process.env,HOME:dir,USERPROFILE:dir,CODEX_HOME:path.join(dir,'.codex'),npm_config_global:'false'};
  assert.equal(spawnSync(process.execPath,[post],{env}).status,0);
  assert.equal(fs.existsSync(path.join(dir,'.codex')),false);
  env.npm_config_global='true';
  assert.equal(spawnSync(process.execPath,[post],{env}).status,0);
  assert.equal(fs.existsSync(path.join(dir,'.codex/skills/pan123-cli/SKILL.md')),true);
 } finally {fs.rmSync(dir,{recursive:true,force:true});}
});
