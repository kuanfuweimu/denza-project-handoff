const fs=require('fs'),vm=require('vm'),path=require('path');
const root='D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/strings-space';
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const source=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).find(s=>s.includes('FS_SIM'));
const prefix=source.slice(0,source.indexOf('function sh('));
const build=source.slice(source.indexOf('function buildStruct('),source.indexOf('const STRUCT='));
const look=source.slice(source.indexOf('function lookAt('),source.indexOf('// ---------- state ----------'));
const ctx=vm.createContext({location:{search:''},URLSearchParams,Float32Array,ParameterLag:require(path.join(root,'parameter-lag.js')),
  StringsMaterials:require(path.join(root,'materials.js')),document:{getElementById:()=>({getContext:()=>({getExtension:()=>true})})}});
vm.runInContext(prefix+build+look+`;globalThis.result={VS_FULL,VS_LINE,VS_DOT,FS_SIM,FS_LINE,FS_DOT,FS_FLOOR,FS_GAUSS,FS_COMP,G,SCENES,ROWS,SEG,NP,FLOOR,STRUCT:buildStruct(7)};`,ctx);
const r=ctx.result;r.STRUCT.data=Array.from(r.STRUCT.data);
r.FS_TRACK=require(path.join(root,'growth-tracker.js')).shader(r.ROWS,r.SEG);
fs.writeFileSync(path.join(__dirname,'scene.json'),JSON.stringify(r));
console.log('Extracted original GLSL source and scene data');
