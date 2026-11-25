const {chromium}=require('playwright');(async()=>{
const [,,file,out,fps,dur,only]=process.argv;const b=await chromium.launch();const p=await b.newPage({viewport:{width:720,height:1280}});
await p.goto('file://'+file);await p.waitForFunction(()=>window.READY);await p.waitForTimeout(300);
const N=Math.round(+dur*+fps);const list=only?only.split(',').map(Number):[...Array(N).keys()];
for(const i of list){const t=only?i:i/ +fps;await p.evaluate(t=>render(t),t);await p.screenshot({path:`${out}/${only?('t'+t):String(i).padStart(4,'0')}.png`,omitBackground:true});}
await b.close()})();
