const $=s=>document.querySelector(s);
const state={languages:[],categories:[],signs:[],query:"",language:"",category:"",ui:"en"};
const i18n={
 en:{nav_dictionary:"Dictionary",nav_learn:"Learn",nav_contribute:"Contribute",nav_about:"About",hero_eyebrow:"A community-led open project",hero_title:"Every sign has a story.",hero_desc:"Explore sign languages as distinct, living languages — documented with respect, consent and community review.",explore_dictionary:"Explore dictionary",msl_note:"is included as a priority research area.",directory_eyebrow:"Explore",directory_title:"Sign dictionary",principles_title:"Language first. Community always.",search_label:"Search signs"},
 my:{nav_dictionary:"အဘိဓာန်",nav_learn:"လေ့လာရန်",nav_contribute:"ပါဝင်ကူညီရန်",nav_about:"အကြောင်း",hero_eyebrow:"အသိုင်းအဝိုင်းဦးဆောင်သော ပွင့်လင်းစီမံကိန်း",hero_title:"လက်ဟန်တိုင်းတွင် အဓိပ္ပာယ်ရှိသည်။",hero_desc:"လက်ဟန်ဘာသာစကားများကို သီးခြားအသက်ဝင်သော ဘာသာစကားများအဖြစ် လေးစားမှု၊ သဘောတူညီမှုနှင့် လူမှုအသိုင်းအဝိုင်းစိစစ်မှုတို့ဖြင့် လေ့လာပါ။",explore_dictionary:"အဘိဓာန်ကြည့်ရန်",msl_note:"ကို ဦးစားပေးသုတေသနအဖြစ် ထည့်သွင်းထားသည်။",directory_eyebrow:"ရှာဖွေရန်",directory_title:"လက်ဟန်အဘိဓာန်",principles_title:"ဘာသာစကားကို ဦးစားပေး၊ အသိုင်းအဝိုင်းကို အမြဲလေးစားပါ။",search_label:"လက်ဟန်များ ရှာရန်"}
};
function translate(lang){state.ui=lang;document.documentElement.lang=lang;document.querySelectorAll("[data-i18n]").forEach(el=>{const key=el.dataset.i18n;if(i18n[lang]?.[key])el.textContent=i18n[lang][key]});}
function norm(s){return String(s??"").normalize("NFKC").toLocaleLowerCase().trim()}
function renderLanguages(){
 const box=$("#language-list");if(!box)return;box.innerHTML="";
 state.languages.forEach(l=>{const a=document.createElement("article");a.className="language-card"+(l.priority?" featured":"");a.innerHTML=`<strong></strong><span></span><small></small>`;a.querySelector("strong").textContent=l.name;a.querySelector("span").textContent=[l.region,l.family].filter(Boolean).join(" · ");a.querySelector("small").textContent=l.id==="ysm"?"Myanmar priority research":l.status||"Research directory";box.append(a)});
 const lf=$("#language-filter");state.languages.forEach(l=>{const o=document.createElement("option");o.value=l.id;o.textContent=l.name;lf.append(o)});
}
function renderFilters(){
 const cf=$("#category-filter");state.categories.forEach(c=>{const o=document.createElement("option");o.value=c.id;o.textContent=c.label;cf.append(o)});
}
function matches(s){const q=norm(state.query);const text=norm([s.id,s.gloss,s.meaning,s.notes,...(s.alternates||[])].join(" "));return(!q||text.includes(q))&&(!state.language||s.language===state.language)&&(!state.category||s.category===state.category)}
function renderSigns(){
 const results=state.signs.filter(matches);$("#sign-grid").innerHTML="";$("#result-count").textContent=`${results.length} entries`;
 $("#empty-state").hidden=results.length>0;
 results.forEach(s=>{const card=document.createElement("article");card.className="sign-card";const h=document.createElement("h3");h.textContent=s.gloss||s.id;const p=document.createElement("p");p.textContent=s.meaning||"Meaning pending community review.";const meta=document.createElement("span");meta.className="status";meta.textContent=s.reviewStatus||"needs-review";const btn=document.createElement("button");btn.className="button secondary";btn.textContent="Details";btn.addEventListener("click",()=>showDetails(s));card.append(h,p,meta,document.createElement("br"),btn);$("#sign-grid").append(card)});
}
function showDetails(s){const box=$("#dialog-content");box.innerHTML="";const h=document.createElement("h2");h.id="dialog-title";h.textContent=s.gloss||s.id;const p=document.createElement("p");p.textContent=s.meaning||"Meaning pending community review.";const d=document.createElement("p");d.textContent=`Language: ${s.language} · Category: ${s.category||"Uncategorized"} · Status: ${s.reviewStatus||"needs-review"}`;box.append(h,p,d);if(s.media?.url){const link=document.createElement("a");link.href=s.media.url;link.textContent="Open approved media";link.rel="noopener noreferrer";box.append(link)}$("#sign-dialog").showModal()}
async function init(){
 $("#year").textContent=new Date().getFullYear();
 const [l,c,a]=await Promise.all(["data/languages.json","data/categories.json","data/signs/index.json"].map(u=>fetch(u).then(r=>{if(!r.ok)throw Error(u);return r.json()})));
 state.languages=l.languages;state.categories=c.categories;state.signs=a.signs;
 renderLanguages();renderFilters();renderSigns();
 $("#search-input").addEventListener("input",e=>{state.query=e.target.value;renderSigns()});
 $("#language-filter").addEventListener("change",e=>{state.language=e.target.value;renderSigns()});
 $("#category-filter").addEventListener("change",e=>{state.category=e.target.value;renderSigns()});
 $("#language-ui").addEventListener("change",e=>translate(e.target.value));
 $("#theme-toggle").addEventListener("click",()=>{const root=document.documentElement;root.dataset.theme=root.dataset.theme==="dark"?"light":"dark"});
 const q=new URLSearchParams(location.search).get("q");if(q){$("#search-input").value=q;state.query=q;renderSigns()}
}
init().catch(err=>{console.error(err);$("#empty-state").textContent="Could not load dictionary data. Run this site through a local web server or GitHub Pages.";});
