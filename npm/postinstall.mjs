import {manage} from './installer.mjs';
if(process.env.npm_config_global==='true') {
 try {console.log('123Pan Skill: '+JSON.stringify(manage('install')));}
 catch {console.warn('123Pan Skill 自动安装未完成；请运行 pan123-skill install 选择目标并检查目录权限。');}
} else console.log('Skill 包已准备；运行 npx pan123-cli-skill install 安装到 AI 工具目录。');
