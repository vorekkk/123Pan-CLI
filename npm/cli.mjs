#!/usr/bin/env node
import {agents,manage} from './installer.mjs';
const args=process.argv.slice(2);
if(args.includes('--help')||args.includes('-h')||!args.length){
 console.log('pan123-skill install|status|uninstall [--agent codex|claude|cursor] [--scope user|project] [--dest FULL_SKILL_PATH] [--force] [--json]\n--agent 可重复；--force 在修改前备份；npm 包不安装 Python CLI。');
 process.exit(0);
}
try {
 const action=args.shift(),options={agents:[],scope:'user'};
 if(!['install','status','uninstall'].includes(action))throw new Error('未知操作');
 while(args.length){
  const flag=args.shift();
  if(flag==='--force')options.force=true;
  else if(flag==='--json')options.json=true;
  else if(['--agent','--scope','--dest'].includes(flag)){
   const value=args.shift();if(!value||value.startsWith('--'))throw new Error('参数缺少值');
   if(flag==='--agent'){if(!agents.includes(value))throw new Error('未知 agent');options.agents.push(value);}
   else if(flag==='--scope'){if(!['user','project'].includes(value))throw new Error('未知 scope');options.scope=value;}
   else options.dest=value;
  }else throw new Error('未知参数 '+flag);
 }
 console.log(JSON.stringify({ok:true,data:manage(action,options)},null,2));
}catch(e){console.error(JSON.stringify({ok:false,error:{message:e.message}}));process.exitCode=1;}
