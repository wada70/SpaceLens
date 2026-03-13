/* SpaceLens — frontend app */
(function () {
  "use strict";

  // ── DOM refs ──────────────────────────────────────────────────────────────
  const form          = document.getElementById("searchForm");
  const queryInput    = document.getElementById("queryInput");
  const spaceInput    = document.getElementById("spaceInput");
  const topKSelect    = document.getElementById("topKSelect");
  const searchBtn     = document.getElementById("searchBtn");
  const btnLabel      = searchBtn.querySelector(".btn-label");
  const btnSpinner    = searchBtn.querySelector(".btn-spinner");

  const resultsSection = document.getElementById("resultsSection");
  const answerCard     = document.getElementById("answerCard");
  const answerText     = document.getElementById("answerText");
  const keywordsPill   = document.getElementById("keywordsPill");
  const durationPill   = document.getElementById("durationPill");
  const resultsTitle   = document.getElementById("resultsTitle");
  const resultsList    = document.getElementById("resultsList");
  const emptyState     = document.getElementById("emptyState");
  const errorBanner    = document.getElementById("errorBanner");
  const errorMsg       = document.getElementById("errorMsg");

  const tpl = document.getElementById("resultItemTpl");

  // ── Search ────────────────────────────────────────────────────────────────
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    setLoading(true);
    clearResults();

    const spaceKeys = spaceInput.value
      .split(",")
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);

    const payload = {
      query,
      top_k: parseInt(topKSelect.value, 10),
      ...(spaceKeys.length ? { space_keys: spaceKeys } : {}),
    };

    try {
      const resp = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const detail = await resp.json().catch(() => ({}));
        throw new Error(detail?.detail || `HTTP ${resp.status}`);
      }

      const data = await resp.json();
      renderResults(data);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  });

  // ── Render ────────────────────────────────────────────────────────────────
  function renderResults(data) {
    // Answer
    answerText.textContent = data.answer;
    keywordsPill.textContent = "Keywords: " + data.keywords.join(", ");
    durationPill.textContent = `${data.duration_ms} ms`;

    if (!data.results || data.results.length === 0) {
      emptyState.classList.remove("hidden");
      answerCard.classList.add("hidden");
      resultsSection.classList.remove("hidden");
      return;
    }

    resultsTitle.textContent = `Top ${data.results.length} result${data.results.length !== 1 ? "s" : ""}`;

    const maxScore = Math.max(...data.results.map((r) => r.score), 0.0001);

    data.results.forEach((page, idx) => {
      const node = tpl.content.cloneNode(true);
      const item = node.querySelector(".result-item");

      // Score bar height (percentage of container height)
      const pct = Math.round((page.score / maxScore) * 100);
      const fill = node.querySelector(".result-item__score-fill");
      fill.style.height = pct + "%";
      fill.style.opacity = 0.4 + (page.score / maxScore) * 0.6;

      node.querySelector(".result-item__title").href = page.url;
      node.querySelector(".result-item__title").textContent = page.title;
      node.querySelector(".result-item__space").textContent = page.space_name || page.space_key;
      node.querySelector(".result-item__date").textContent = formatDate(page.last_modified);
      node.querySelector(".result-item__excerpt").textContent = page.excerpt || "—";
      node.querySelector(".result-item__score-badge").textContent = page.score.toFixed(2);

      // Stagger animation
      item.style.animationDelay = `${idx * 60}ms`;
      item.classList.add("result-enter");

      resultsList.appendChild(node);
    });

    resultsSection.classList.remove("hidden");

    // Scroll to results smoothly
    resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  function setLoading(on) {
    searchBtn.disabled = on;
    btnLabel.classList.toggle("hidden", on);
    btnSpinner.classList.toggle("hidden", !on);
  }

  function clearResults() {
    resultsSection.classList.add("hidden");
    emptyState.classList.add("hidden");
    errorBanner.classList.add("hidden");
    answerCard.classList.remove("hidden");
    resultsList.innerHTML = "";
    answerText.textContent = "";
    keywordsPill.textContent = "";
    durationPill.textContent = "";
  }

  function showError(msg) {
    errorMsg.textContent = msg;
    errorBanner.classList.remove("hidden");
  }

  function formatDate(iso) {
    if (!iso) return "";
    try {
      return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    } catch {
      return iso;
    }
  }

  // ── Bookmarklet ───────────────────────────────────────────────────────────
  const APP_ORIGIN = window.location.origin;

  const bookmarkletCode = `(function(){
  var q = document.title;
  window.open('${APP_ORIGIN}/?q=' + encodeURIComponent(q), 'spacelens', 'width=720,height=600');
})();`;

  const bookmarkletLink = document.getElementById("bookmarkletLink");
  bookmarkletLink.href = "javascript:" + encodeURIComponent(bookmarkletCode);

  document.getElementById("copyBookmarklet").addEventListener("click", () => {
    copyText("javascript:" + encodeURIComponent(bookmarkletCode), "copyBookmarklet");
  });

  // Widget embed snippet
  const widgetSnippet = `<!-- SpaceLens floating widget -->
<script>
(function(){
  var btn = document.createElement('button');
  btn.textContent = '🔭 SpaceLens';
  btn.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;'
    + 'background:#4f7cff;color:#fff;border:none;border-radius:24px;'
    + 'padding:10px 20px;font-size:14px;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.4);';
  btn.onclick = function(){
    window.open('${APP_ORIGIN}/?q=' + encodeURIComponent(document.title),
      'spacelens','width=760,height=640');
  };
  document.body.appendChild(btn);
})();
<\/script>`;

  document.getElementById("widgetSnippet").textContent = widgetSnippet;
  document.getElementById("copyWidget").addEventListener("click", () => {
    copyText(widgetSnippet, "copyWidget");
  });

  function copyText(text, btnId) {
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.getElementById(btnId);
      const orig = btn.textContent;
      btn.textContent = "Copied!";
      setTimeout(() => (btn.textContent = orig), 1800);
    });
  }

  // Pre-fill query from URL param (used by bookmarklet)
  const urlQ = new URLSearchParams(window.location.search).get("q");
  if (urlQ) {
    queryInput.value = urlQ;
    form.dispatchEvent(new Event("submit"));
  }
})();
