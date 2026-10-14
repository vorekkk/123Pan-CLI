import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source=path.join(root,'skills','pan123-cli');
const version=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8')).version;
const name='pan123-cli', marker='.pan123-skill.json';
export const agents=['codex','claude','cursor'];
export function detectedAgents() {
 return agents.filter(a=>fs.existsSync(path.join(os.homedir(),a==='codex'?'.codex':'.'+a)) || (a==='codex'&&process.env.CODEX_HOME));
}
function destination(agent,options) {
 if(options.dest)return path.resolve(options.dest.replace(/^~(?=$|[\/\\])/,os.homedir()));
 const base=options.scope==='project'?path.join(process.cwd(),agent==='codex'?'.agents':'.'+agent):agent==='codex'?(process.env.CODEX_HOME||path.join(os.homedir(),'.codex')):path.join(os.homedir(),'.'+agent);
 return path.resolve(base,'skills',name);
}
function safePath(dest) {
 for(let p=dest;;p=path.dirname(p)) {
  if(fs.existsSync(p)&&fs.lstatSync(p).isSymbolicLink())throw new Error('Skill 路径不能包含符号链接');
  // lstat also rejects dangling links.
  try{if(fs.lstatSync(p).isSymbolicLink())throw new Error('Skill 路径不能包含符号链接');}catch(e){if(e.code!=='ENOENT')throw e;}
  if(path.dirname(p)===p)break;
 }
}
function hashes(dir) {
 const result={};
 function walk(current) {
  for(const item of fs.readdirSync(current,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))) {
   const p=path.join(current,item.name);
   if(item.isSymbolicLink())throw new Error('Skill 目录包含符号链接');
   if(item.isDirectory())walk(p);
   else if(item.isFile()&&item.name!==marker)result[path.relative(dir,p).split(path.sep).join('/')]=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  }
 }
 walk(dir);return result;
}
function equal(a,b){return Object.keys(a).length===Object.keys(b).length&&Object.entries(a).every(([k,v])=>b[k]===v);}
function status(dest) {
 safePath(dest);
 if(!fs.existsSync(dest))return 'missing';
 try {
  const record=JSON.parse(fs.readFileSync(path.join(dest,marker),'utf8'));
  if(record.name===name&&record.schema_version===1&&record.files&&equal(record.files,hashes(dest)))return 'managed';
 } catch(e) {if(e.message.includes('符号链接'))throw e;}
 return 'conflict';
}
export function manage(action,options={}) {
 const selected=options.agents?.length?options.agents:options.dest?['codex']:detectedAgents().length?detectedAgents():['codex'];
 if(options.dest&&selected.length>1)throw new Error('--dest 不能与多个 --agent 一起使用');
 return {results:[...new Set(selected)].map(agent=>{
  const dest=destination(agent,options);safePath(dest);
  if(action==='status')return {agent,path:dest,status:status(dest)};
  fs.mkdirSync(path.dirname(dest),{recursive:true});
  const lock=path.join(path.dirname(dest),'.'+path.basename(dest)+'.install-lock');
  try {fs.mkdirSync(lock);}catch(e){if(e.code==='EEXIST')throw new Error('另一个 Skill 安装正在进行；确认无安装进程后清理 '+lock);throw e;}
  let backup,temp;
  try {
   const state=status(dest);
   if(state==='conflict'&&!options.force)throw new Error('Skill 已被修改或不是托管目录；使用 --force 备份后继续');
   if(action==='install'&&state==='managed'&&equal(hashes(dest),hashes(source)))return {agent,path:dest,status:'unchanged'};
   if(action==='install') {
    temp=fs.mkdtempSync(path.join(path.dirname(dest),'.'+name+'-'));
    fs.cpSync(source,temp,{recursive:true});
    fs.writeFileSync(path.join(temp,marker),JSON.stringify({schema_version:1,name,version,files:hashes(temp)}));
   }
   if(fs.existsSync(dest)) {backup=dest+'.backup-'+crypto.randomUUID();fs.renameSync(dest,backup);}
   if(temp){fs.renameSync(temp,dest);temp=undefined;}
   if(backup&&!options.force){fs.rmSync(backup,{recursive:true});backup=undefined;}
   return {agent,path:dest,status:action==='install'?'installed':'uninstalled',...(backup?{backup}:{})};
  } catch(e) {if(backup&&!fs.existsSync(dest))fs.renameSync(backup,dest);throw e;}
  finally {if(temp)fs.rmSync(temp,{recursive:true,force:true});fs.rmdirSync(lock);}
 })};
}
