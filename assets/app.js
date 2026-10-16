"use strict";
(() => {
  const catalog = window.PATCH_CATALOG;
  const $ = (id) => document.getElementById(id);
  if (!catalog || !Array.isArray(catalog.games)) {
    $("catalog-summary").textContent = "목록을 불러오지 못했습니다. 새로고침하거나 GitHub 저장소를 확인해 주세요.";
    return;
  }
  const games = catalog.games;
  const platformNames = {NES:"패미컴 / NES",PS1:"PlayStation",PSP:"PSP",GBA:"Game Boy Advance",NDS:"Nintendo DS",ARCADE:"아케이드",PC:"Windows",SWITCH:"Nintendo Switch",PCE:"PC Engine"};
  const state = {platform:"ALL",query:"",available:false,sort:"available"};
  const esc = (s) => String(s).replace(/[&<>"']/g,(c)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const normalize = (s) => String(s).normalize("NFKC").toLocaleLowerCase("ko").replace(/[\s_~:·—-]+/g,"");
  const validUrl = (url) => typeof url === "string" && /^https:\/\/github\.com\/akuma815\/[a-zA-Z0-9._/-]+$/.test(url);
  const safeLink = (url,label,className="") => validUrl(url) ? `<a class="${esc(className)}" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${label}</a>` : "";
  const availableCount = games.filter(g=>g.available).length;
  $("total-count").textContent = String(games.length).padStart(2,"0");
  $("catalog-summary").textContent = `배포 중 ${availableCount}개 · 등록 준비 ${games.length-availableCount}개`;
  $("updated-at").textContent = `목록 확인 ${catalog.checkedAt} · KST`;
  const platforms = ["ALL",...Object.keys(platformNames).filter(p=>games.some(g=>g.platform===p))];
  $("filters").innerHTML = platforms.map(p=>`<button type="button" class="filter" data-platform="${p}" aria-pressed="${p==="ALL"}">${p==="ALL"?"전체":platformNames[p]}<span>${p==="ALL"?games.length:games.filter(g=>g.platform===p).length}</span></button>`).join("");
  function render() {
    const q=normalize(state.query);
    const filtered=games.filter(g=>(state.platform==="ALL"||g.platform===state.platform)&&(!state.available||g.available)&&(!q||normalize([g.title,g.english,g.platform,platformNames[g.platform],g.description].join(" ")).includes(q)));
    filtered.sort((a,b)=>state.sort==="platform"?a.platform.localeCompare(b.platform)||a.title.localeCompare(b.title,"ko"):state.sort==="title"?a.title.localeCompare(b.title,"ko"):Number(b.available)-Number(a.available)||a.title.localeCompare(b.title,"ko"));
    $("result-count").textContent = `${filtered.length}개의 패치${state.platform!=="ALL"?" · "+platformNames[state.platform]:""}`;
    $("reset").hidden = !(state.query||state.platform!=="ALL"||state.available||state.sort!=="available");
    $("empty").hidden=filtered.length>0;
    $("games").innerHTML=filtered.map(g=>`<article class="game-card" data-game="${esc(g.id)}"><div class="card-top"><span class="platform"><span class="platform-mark" aria-hidden="true"></span>${esc(g.platform)}</span><span class="availability${g.available?"":" is-pending"}"><span class="status-dot${g.available?"":" pending"}"></span>${g.available?"배포 중":"등록 준비"}</span></div><h3>${esc(g.title)}</h3><p class="english">${esc(g.english)}</p><p class="card-about">${esc(g.description)}</p><div class="card-footer"><span class="version">${esc(g.version)}</span><div class="card-links"><button class="detail-button" type="button" data-details="${esc(g.id)}" aria-label="${esc(g.title)} 상세 정보">자세히</button>${g.available?safeLink(g.repository,"소스 ↗"):""}${g.available?safeLink(g.release,"패치 받기 ↗","download"):'<span class="pending-label">공개 등록 예정</span>'}</div></div></article>`).join("");
    document.querySelectorAll("[data-platform]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.platform===state.platform)));
  }
  function reset() {state.platform="ALL";state.query="";state.available=false;state.sort="available";$("search").value="";$("available-only").checked=false;$("sort").value="available";render();}
  $("search").addEventListener("input",e=>{state.query=e.target.value;render();});
  $("available-only").addEventListener("change",e=>{state.available=e.target.checked;render();});
  $("sort").addEventListener("change",e=>{state.sort=e.target.value;render();});
  $("filters").addEventListener("click",e=>{const b=e.target.closest("[data-platform]");if(b){state.platform=b.dataset.platform;render();}});
  $("reset").addEventListener("click",reset);$("empty-reset").addEventListener("click",reset);
  let previousFocus=null;
  $("games").addEventListener("click",e=>{
    const b=e.target.closest("[data-details]");if(!b)return;
    const g=games.find(g=>g.id===b.dataset.details);if(!g)return;
    previousFocus=b;$("dialog-title").textContent=g.title;$("dialog-platform").textContent=platformNames[g.platform];$("dialog-about").textContent=g.description;
    $("dialog-version").innerHTML=`<span>${g.available?"배포 중":"공개 등록 준비"}</span> · ${esc(g.version)}`;
    $("dialog-notes").innerHTML=g.notes.map(n=>`<li>${esc(n)}</li>`).join("");
    $("dialog-actions").innerHTML=g.available?safeLink(g.release,"최종 배포 패치 받기 ↗","primary")+safeLink(g.repository,"적용 방법 · 소스 ↗"):'<p class="pending-label">공개 릴리즈 등록 후 다운로드 링크가 제공됩니다.</p>';
    $("details").showModal();
  });
  $("close-dialog").addEventListener("click",()=>$("details").close());
  $("details").addEventListener("close",()=>previousFocus?.focus());
  $("details").addEventListener("click",e=>{if(e.target===$("details")){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
  render();
})();
