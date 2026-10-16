"use strict";
(() => {
  const games=window.PATCH_CATALOG?.games;
  if (!Array.isArray(games)||!window.PATCH_DETAILS) return;
  const $=id=>document.getElementById(id);
  const root=new URL("./",document.baseURI);
  const homeTitle="akuma815 — 우리들의 작은 게임방";
  const find=id=>games.find(game=>game.id===id);
  const gameUrl=game=>new URL("games/"+encodeURIComponent(game.id)+"/",root).href;
  let syncing=false;
  let routeClose=false;
  let selected=null;
  function requestedGame() {
    const url=new URL(window.location.href);
    if (url.searchParams.has("game")) return url.searchParams.get("game");
    if (!url.pathname.startsWith(root.pathname)) return null;
    const relative=url.pathname.slice(root.pathname.length);
    const match=relative.match(/^games\/([a-z0-9-]+)\/(?:index\.html)?$/);
    return match?match[1]:null;
  }
  window.PATCH_LINKS={
    opened(game) {
      selected=game;
      $("game-share-url").value=gameUrl(game);
      $("game-share-feedback").textContent="";
      document.title=game.title+" 한글 패치 "+(game.status==="in-progress"?"작업 중 · ":"")+game.version+" | akuma815";
      if (!syncing && requestedGame()!==game.id) {
        const url=new URL(window.location.href);
        url.searchParams.set("game",game.id);url.hash="";
        window.history.pushState(null,"",url);
      }
    },
    closed() {
      selected=null;
      document.title=homeTitle;
      if (routeClose) {routeClose=false;return;}
      if (requestedGame()!==null) window.history.replaceState(null,"",new URL("#catalog",root));
    }
  };
  function syncRoute() {
    const id=requestedGame();const game=find(id);
    const feedback=$("game-link-feedback");feedback.hidden=true;
    if (game) {
      syncing=true;
      try {window.PATCH_DETAILS.open(game.id,{instant:true});}
      finally {syncing=false;}
    } else {
      if ($("details").open) {routeClose=true;$("details").close();}
      document.title=homeTitle;
      if (id!==null) {
        feedback.textContent="그 게임 링크는 찾지 못했어. 아래 목록에서 다시 골라 줄래?";feedback.hidden=false;
        $("catalog").scrollIntoView({block:"start"});
      }
    }
  }
  $("copy-game-link").addEventListener("click",async()=>{
    if (!selected) return;
    const id=selected.id;const url=gameUrl(selected);
    try {
      await navigator.clipboard.writeText(url);
      if (selected?.id===id) $("game-share-feedback").textContent="링크를 복사했어! 친구에게 보내면 이 게임 소개가 바로 열려.";
    } catch {
      if (selected?.id!==id) return;
      $("game-share-url").focus();$("game-share-url").select();
      $("game-share-feedback").textContent="주소를 선택했어. 직접 복사해서 친구에게 보내 줘.";
    }
  });
  window.addEventListener("popstate",syncRoute);
  syncRoute();
})();
