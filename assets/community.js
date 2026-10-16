"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const labels = {guestbook: "site-guestbook", bugs: "site-bug"};
  const templates = {guestbook: "site-guestbook.md", bugs: "site-bug-report.md"};
  const fields = {guestbook: ["title", "message"], bugs: ["title", "version", "environment", "message", "steps", "expected"]};
  const cache = new Map();
  const drafts = new Map();
  let game = null;
  let active = "intro";
  let controller = null;
  let requestNumber = 0;
  const safeGame = g => g && /^[a-z0-9-]+$/.test(g.id) && g.repository === `https://github.com/akuma815/${g.id}`;
  const text = (tag, value, className) => {
    const node = document.createElement(tag);
    node.textContent = String(value || "");
    if (className) node.className = className;
    return node;
  };
  const listUrl = kind => `${game.repository}/issues?q=${encodeURIComponent("is:issue label:" + labels[kind] + " sort:created-desc")}`;
  const baseDraftUrl = kind => `${game.repository}/issues/new?template=${templates[kind]}`;
  function values(kind) {
    return Object.fromEntries(fields[kind].map(key => [key, $(kind + "-" + key).value.trim()]));
  }
  function remember() {
    if (!game) return;
    for (const kind of Object.keys(fields)) drafts.set(game.id + ":" + kind, values(kind));
  }
  function body(kind) {
    const v = values(kind);
    if (kind === "guestbook") return `<!-- managed-by:akuma815-site-community -->\n### 낙서\n\n${v.message}\n`;
    return `<!-- managed-by:akuma815-site-community -->\n### 패치 버전\n\n${v.version}\n\n### 실행 환경\n\n${v.environment}\n\n### 어떤 일이 있었어?\n\n${v.message}\n\n### 이렇게 하면 다시 생겨\n\n${v.steps || "아직 확인하지 못했어."}\n\n### 원래는 어떻게 되어야 해?\n\n${v.expected || "아직 확인하지 못했어."}\n`;
  }
  function draftUrl(kind) {
    const v = values(kind);
    const title = kind === "guestbook" ? `[방명록] ${v.title || game.title + "에 다녀갔어!"}` : `[버그] ${v.title}`;
    // Labels come from the repository template, not a query parameter requiring triage rights.
    const query = new URLSearchParams({template: templates[kind], title, body: body(kind)});
    return `${game.repository}/issues/new?${query}`;
  }
  function date(value) {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? "" : parsed.toLocaleDateString("ko-KR");
  }
  function renderPosts(kind, entry) {
    const host = $(kind + "-posts");
    host.replaceChildren();
    for (const issue of entry.issues) {
      const note = document.createElement("article");
      note.className = kind === "guestbook" ? `graffiti-note ink-${issue.number % 4}` : "chalk-note";
      const title = String(issue.title || "").replace(/^\[(방명록|버그)\]\s*/, "");
      const heading = text("h4", title);
      const link = document.createElement("a");
      link.href = `${game.repository}/issues/${issue.number}`;
      link.target = "_blank"; link.rel = "noopener noreferrer";
      link.append(heading); note.append(link);
      if (kind === "bugs") note.append(text("span", issue.state === "closed" ? "닫힌 신고" : "열린 신고", "chalk-state"));
      let content = String(issue.body || "").replace(/<!--[^]*?-->/g, "").trim();
      if (kind === "guestbook") content = content.replace(/^### 낙서\s*/, "");
      else content = content.replace(/^###\s+/gm, "");
      // Treat GitHub text as text: no HTML, Markdown embeds, or remote images execute here.
      const excerpt = content.slice(0, 12000);
      const details = document.createElement("details");
      if (kind === "bugs") {
        details.append(text("summary", "무슨 일이 있었는지 읽어 보기"));
        details.append(text("p", excerpt, "board-message")); note.append(details);
      } else note.append(text("p", excerpt, "board-message"));
      if (content.length > excerpt.length) note.append(text("p", "긴 글은 GitHub에서 이어서 읽어 줘.", "board-overflow"));
      const author = String(issue.user?.login || "이름 없는 친구").slice(0, 80);
      note.append(text("p", `${author} · ${date(issue.created_at)} · #${issue.number}`, "board-author"));
      const replies = document.createElement("a");
      replies.href = `${game.repository}/issues/${issue.number}`;
      replies.target = "_blank"; replies.rel = "noopener noreferrer";
      replies.textContent = `답글 ${Number.isSafeInteger(issue.comments) ? issue.comments : 0}개 · GitHub에서 보기 ↗`;
      replies.className = "board-replies"; note.append(replies);
      host.append(note);
    }
    $(kind + "-more").hidden = !entry.nextPage;
    $(kind + "-status").textContent = entry.issues.length ? `${entry.issues.length}개의 ${kind === "guestbook" ? "낙서를 읽고 있어." : "신고를 보고 있어."}` : kind === "guestbook" ? "아직 깨끗한 벽이네. 첫 낙서는 네 차례야!" : "아직 칠판에 적힌 버그가 없어. 발견하면 알려 줘!";
  }
  async function load(kind, {more = false, force = false} = {}) {
    if (!safeGame(game)) return;
    controller?.abort();
    const request = ++requestNumber;
    const selected = game;
    const key = selected.id + ":" + kind;
    const previous = cache.get(key);
    if (previous && !more && !force && Date.now() - previous.updated < 300000) {renderPosts(kind, previous); return;}
    const page = more && previous?.nextPage ? previous.nextPage : 1;
    controller = new AbortController();
    const status = $(kind + "-status");
    status.textContent = kind === "guestbook" ? "친구들이 남긴 낙서를 읽어 오는 중…" : "칠판에 적힌 버그를 살펴보는 중…";
    const refresh = document.querySelector(`[data-board-refresh="${kind}"]`);
    refresh.disabled = true; $(kind + "-more").disabled = true;
    try {
      const query = new URLSearchParams({state:"all", labels:labels[kind], sort:"created", direction:"desc", per_page:"12", page:String(page)});
      const response = await fetch(`https://api.github.com/repos/akuma815/${selected.id}/issues?${query}`, {headers:{Accept:"application/vnd.github+json"}, signal:controller.signal, credentials:"omit", referrerPolicy:"no-referrer", cache:force ? "no-store" : "default"});
      if (!response.ok) throw new Error(response.status === 403 || response.status === 429 ? "rate" : "network");
      const data = await response.json();
      if (!Array.isArray(data)) throw new Error("format");
      if (request !== requestNumber || game?.id !== selected.id || active !== kind) return;
      const issues = data.filter(issue => issue && Number.isSafeInteger(issue.number) && issue.number > 0 && !issue.pull_request && issue.html_url === `${selected.repository}/issues/${issue.number}` && Array.isArray(issue.labels) && issue.labels.some(label => (typeof label === "string" ? label : label?.name) === labels[kind]));
      const combined = page > 1 && previous ? [...previous.issues, ...issues] : issues;
      const entry = {issues:[...new Map(combined.map(issue => [issue.number, issue])).values()], nextPage:/rel="next"/.test(response.headers.get("Link") || "") ? page + 1 : null, updated:Date.now()};
      cache.set(key, entry); renderPosts(kind, entry);
    } catch (error) {
      if (error.name === "AbortError" || request !== requestNumber) return;
      status.textContent = error.message === "rate" ? "잠깐, GitHub가 조금 쉬어 달래. 위의 ‘GitHub에서 모두 보기’로 바로 읽을 수 있어." : "글을 불러오지 못했어. 새로 보기를 누르거나 GitHub에서 바로 읽어 줘.";
    } finally {
      if (request === requestNumber) {refresh.disabled = false; $(kind + "-more").disabled = false;}
    }
  }
  function setTab(kind) {
    if (!["intro", "guestbook", "bugs"].includes(kind)) return;
    controller?.abort(); ++requestNumber;
    document.querySelectorAll("[data-board-refresh], [data-board-more]").forEach(button => button.disabled = false);
    active = kind;
    for (const key of ["intro", "guestbook", "bugs"]) {
      $("tab-" + key).setAttribute("aria-selected", String(key === kind));
      $("tab-" + key).tabIndex = key === kind ? 0 : -1;
      $("panel-" + key).hidden = key !== kind;
    }
    $("details").dataset.board = kind;
    $("details").scrollTop = 0;
    if (kind !== "intro") load(kind);
  }
  document.querySelector(".community-tabs").addEventListener("click", event => {
    const button = event.target.closest("[data-community-tab]");
    if (button && !button.disabled) setTab(button.dataset.communityTab);
  });
  document.querySelector(".community-tabs").addEventListener("keydown", event => {
    const keys = ["intro", "guestbook", "bugs"];
    const current = keys.indexOf(event.target.dataset.communityTab);
    if (current < 0) return;
    const next = event.key === "ArrowRight" ? (current + 1) % 3 : event.key === "ArrowLeft" ? (current + 2) % 3 : event.key === "Home" ? 0 : event.key === "End" ? 2 : null;
    if (next === null) return;
    event.preventDefault();
    if (!$("tab-" + keys[next]).disabled) {$("tab-" + keys[next]).focus(); setTab(keys[next]);}
  });
  for (const kind of Object.keys(fields)) {
    document.querySelector(`[data-board-write="${kind}"]`).addEventListener("click", () => {
      $(kind + "-form").scrollIntoView({block:"start"});
      $(kind + (kind === "guestbook" ? "-message" : "-title")).focus({preventScroll:true});
    });
    document.querySelector(`[data-board-refresh="${kind}"]`).addEventListener("click", () => load(kind, {force:true}));
    $(kind + "-more").addEventListener("click", () => load(kind, {more:true}));
    $(kind + "-form").addEventListener("input", event => {event.target.setCustomValidity?.(""); remember();});
    $(kind + "-form").addEventListener("submit", event => {
      event.preventDefault();
      if (!safeGame(game)) return;
      for (const field of kind === "guestbook" ? ["message"] : ["title", "version", "environment", "message"]) {
        const input = $(kind + "-" + field);
        input.setCustomValidity(input.value.trim() ? "" : "이 칸을 먼저 적어 줘.");
        if (!input.reportValidity()) return;
      }
      const url = draftUrl(kind);
      const feedback = $(kind + "-feedback");
      if (url.length > 7000) {
        feedback.replaceChildren(text("span", "글이 길어졌네! ‘내용 복사’를 누르고 GitHub에서 붙여 넣어 줘. "));
        const link = document.createElement("a");link.href = baseDraftUrl(kind);link.target = "_blank";link.rel = "noopener noreferrer";link.textContent = "GitHub에서 이어 쓰기 ↗";feedback.append(link);return;
      }
      remember();
      window.open(url, "_blank", "noopener,noreferrer");
      feedback.textContent = "GitHub에서 글을 확인하고 최종 등록 버튼을 눌러 줘. 돌아온 뒤 ‘새로 보기’를 누르면 돼!";
    });
    $(kind + "-message").addEventListener("input", () => $(kind + "-message").setCustomValidity(""));
    document.querySelector(`[data-board-copy="${kind}"]`).addEventListener("click", async () => {
      if (!safeGame(game)) return;
      try {await navigator.clipboard.writeText(body(kind)); $(kind + "-feedback").textContent = "내용을 복사했어. GitHub에 붙여 넣고 등록해 줘!";}
      catch {$(kind + "-feedback").textContent = "복사하지 못했어. 입력한 글을 직접 선택해서 복사해 줘.";}
    });
  }
  window.PATCH_COMMUNITY = {
    openGame(selected) {
      remember(); controller?.abort(); ++requestNumber;
      game = safeGame(selected) ? selected : null;
      for (const kind of Object.keys(fields)) {
        $("tab-" + kind).disabled = !game;
        const saved = game ? drafts.get(game.id + ":" + kind) : null;
        for (const field of fields[kind]) $(kind + "-" + field).value = saved?.[field] || (kind === "bugs" && field === "version" ? selected.version : "");
        $(kind + "-message").setCustomValidity("");
        $(kind + "-feedback").textContent = "";
        $(kind + "-posts").replaceChildren(); $(kind + "-status").textContent = "";
        $(kind + "-more").hidden = true;
        if (game) $(kind + "-all").href = listUrl(kind); else $(kind + "-all").removeAttribute("href");
      }
      document.querySelectorAll("[data-community-game]").forEach(node => node.textContent = selected.title);
      setTab("intro");
    },
    close() {remember(); controller?.abort(); ++requestNumber; game = null;}
  };
})();
