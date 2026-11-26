// Usage: node render_overlay.js config.json outDir [fps] [duration] [t1,t2,...]
// Renders the transparent caption/price/end-card layer as PNG frames (0000.png...).
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const [,,cfgPath,out,fpsA,durA,only]=process.argv;const cfg=JSON.parse(fs.readFileSync(cfgPath,'utf8'));
const fps=+(fpsA||30),dur=+(durA||cfg.duration);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();const p=await b.newPage({viewport:{width:720,height:1280}});
await p.addInitScript(c=>{window.CFG=c},cfg);
await p.goto('file://'+path.join(__dirname,'overlay.html'));await p.waitForFunction(()=>window.READY);await p.waitForTimeout(300);
const list=only?only.split(',').map(Number):[...Array(Math.round(dur*fps)).keys()];
for(const i of list){const t=only?i:i/fps;await p.evaluate(t=>render(t),t);
 await p.screenshot({path:`${out}/${only?('t'+t):String(i).padStart(4,'0')}.png`,omitBackground:true});}
await b.close()})();
