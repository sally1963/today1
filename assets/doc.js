/* 소개·개인정보처리방침·해설 페이지 공용: 언어 전환, 운영자 정보 채우기, 광고 넣기 */
(function () {
  var S = window.SITE || {};
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };

  /* ---- 언어 ---- */
  var LANGS = { ko: "한국어", en: "English", zh: "中文", ja: "日本語", es: "Español", fr: "Français", ru: "Русский" };
  var GT = { zh: "zh-CN", ja: "ja", es: "es", fr: "fr", ru: "ru" };
  var L = {
    ko: { logo: "오늘의 <span>1위</span>", nav_rank: "순위", nav_post: "오늘의 해설", nav_about: "소개", nav_privacy: "개인정보처리방침", back: "← 지난 해설 모두 보기", post_lede: "순위표 뒤에 숨은 이야기를 매일 짧게 정리합니다.", ad: "광고", op: "운영:", ct: "문의:", fill: "(site.config.js에 입력 필요)", site: "오늘의 1위" },
    en: { logo: "Today's <span>No.1</span>", nav_rank: "Rankings", nav_post: "Today's Insight", nav_about: "About", nav_privacy: "Privacy Policy", back: "← See all past insights", post_lede: "A short daily take on the stories behind the charts.", ad: "Ad", op: "Operated by:", ct: "Contact:", fill: "(to be set in site.config.js)", site: "Today's No.1" },
    zh: { logo: "今日<span>第一</span>", nav_rank: "排行榜", nav_post: "今日解读", nav_about: "关于", nav_privacy: "隐私政策", back: "← 查看全部往期解读", post_lede: "每天简短解读排行榜背后的故事。", ad: "广告", op: "运营：", ct: "联系：", note: "本页提供韩文和英文版本，以下显示英文版。", tr: "用机器翻译查看中文 ↗", site: "今日第一" },
    ja: { logo: "今日の<span>1位</span>", nav_rank: "ランキング", nav_post: "今日の解説", nav_about: "サイトについて", nav_privacy: "プライバシーポリシー", back: "← 過去の解説をすべて見る", post_lede: "ランキングの裏にあるストーリーを毎日短くまとめます。", ad: "広告", op: "運営：", ct: "お問い合わせ：", note: "このページは韓国語と英語で提供しています。以下は英語版です。", tr: "機械翻訳で日本語を表示 ↗", site: "今日の1位" },
    es: { logo: "El <span>N.º 1</span> de hoy", nav_rank: "Rankings", nav_post: "Análisis del día", nav_about: "Acerca de", nav_privacy: "Política de privacidad", back: "← Ver todos los análisis anteriores", post_lede: "Un breve análisis diario de las historias detrás de los rankings.", ad: "Anuncio", op: "Gestionado por:", ct: "Contacto:", note: "Esta página está disponible en coreano e inglés. A continuación, la versión en inglés.", tr: "Ver en español con traducción automática ↗", site: "El N.º 1 de hoy" },
    fr: { logo: "Le <span>n° 1</span> du jour", nav_rank: "Classements", nav_post: "Le décryptage du jour", nav_about: "À propos", nav_privacy: "Politique de confidentialité", back: "← Voir tous les décryptages", post_lede: "Chaque jour, un court décryptage des histoires derrière les classements.", ad: "Publicité", op: "Édité par :", ct: "Contact :", note: "Cette page existe en coréen et en anglais. Voici la version anglaise.", tr: "Lire en français (traduction automatique) ↗", site: "Le n° 1 du jour" },
    ru: { logo: "<span>№ 1</span> сегодня", nav_rank: "Рейтинги", nav_post: "Разбор дня", nav_about: "О сайте", nav_privacy: "Политика конфиденциальности", back: "← Все прошлые разборы", post_lede: "Каждый день — короткий разбор того, что стоит за рейтингами.", ad: "Реклама", op: "Автор сайта:", ct: "Контакты:", note: "Эта страница доступна на корейском и английском. Ниже — английская версия.", tr: "Открыть на русском (машинный перевод) ↗", site: "№ 1 сегодня" }
  };
  var lang = (function () {
    var q = new URLSearchParams(location.search).get("lang"); if (q && LANGS[q]) return q;
    try { var s = localStorage.getItem("lang"); if (s && LANGS[s]) return s; } catch (e) {}
    var n = (navigator.language || "en").slice(0, 2).toLowerCase(); return LANGS[n] ? n : "en";
  })();
  window.DOCLANG = lang;
  var t = function (k) { return (L[lang] && L[lang][k]) || L.en[k] || L.ko[k] || ""; };
  var FONTS = { zh: "Noto+Sans+SC:wght@400;700;900", ja: "Noto+Sans+JP:wght@400;700;900", en: "Noto+Sans:wght@400;700;900", es: "Noto+Sans:wght@400;700;900", fr: "Noto+Sans:wght@400;700;900", ru: "Noto+Sans:wght@400;700;900" };

  function apply() {
    document.documentElement.lang = lang === "zh" ? "zh-CN" : lang;
    if (FONTS[lang] && !document.getElementById("font-" + lang)) { var k = document.createElement("link"); k.id = "font-" + lang; k.rel = "stylesheet"; k.href = "https://fonts.googleapis.com/css2?family=" + FONTS[lang] + "&display=swap"; document.head.appendChild(k); }
    document.querySelectorAll("[data-t]").forEach(function (el) { el.innerHTML = t(el.dataset.t); });
    var show = lang === "ko" ? "ko" : "en";
    document.querySelectorAll("[data-lang]").forEach(function (el) { el.hidden = el.dataset.lang !== show; });
    if (!document.body.dataset.titleKo) document.body.dataset.titleKo = document.title;
    document.title = lang === "ko" ? document.body.dataset.titleKo : (document.body.dataset.titleEn || document.title);
    var note = document.getElementById("tnote");
    if (note) {
      if (GT[lang] && document.querySelector("[data-lang=en]")) {
        var u = location.href.split("?")[0].split("#")[0] + "?lang=en";
        note.innerHTML = esc(t("note")) + ' <a href="https://translate.google.com/translate?sl=en&tl=' + GT[lang] + "&u=" + encodeURIComponent(u) + '" target="_blank" rel="noopener">' + esc(t("tr")) + "</a>";
        note.hidden = false;
      } else note.hidden = true;
    }
    document.querySelectorAll("a[href]").forEach(function (a) {
      var h = a.getAttribute("href"); if (/^(https?:|mailto:|#)/.test(h) || a.closest("#tnote")) return;
      var parts = h.split("#"), base = parts[0].split("?")[0], hash = parts[1] ? "#" + parts[1] : "";
      a.setAttribute("href", base + (lang !== "ko" ? "?lang=" + lang : "") + hash);
    });
    document.querySelectorAll("[data-site]").forEach(function (el) {
      var v = S[el.dataset.site];
      if (v) { el.textContent = v; el.classList.remove("fill"); } else { el.textContent = t("fill"); el.classList.add("fill"); }
    });
    var f = document.getElementById("fop");
    if (f) f.textContent = "© " + new Date().getFullYear() + " " + (lang === "ko" ? (S.name || t("site")) : t("site")) + (S.operator ? " · " + t("op") + " " + S.operator : "") + (S.email ? " · " + t("ct") + " " + S.email : "");
    document.querySelectorAll(".adlabel").forEach(function (el) { el.textContent = t("ad"); });
    document.querySelectorAll(".langsel").forEach(function (s) { s.value = lang; });
  }
  document.querySelectorAll(".langsel").forEach(function (s) {
    s.innerHTML = Object.keys(LANGS).map(function (k) { return '<option value="' + k + '">' + LANGS[k] + "</option>"; }).join("");
    s.addEventListener("change", function () {
      lang = s.value; window.DOCLANG = lang; try { localStorage.setItem("lang", lang); } catch (e) {}
      var u = new URL(location.href); if (lang === "ko") u.searchParams.delete("lang"); else u.searchParams.set("lang", lang);
      location.replace(u.pathname + u.search + u.hash);
    });
  });
  apply();

  /* ---- 광고 ---- */
  var AF = S.adfit || {}, mob = window.matchMedia("(max-width: 760px)").matches, need = false;
  document.querySelectorAll(".adslot").forEach(function (el) {
    var u = AF[el.dataset.slot]; if (!u) return; var unit = mob ? u.mobile : u.pc; if (!unit || !unit.id) return;
    el.innerHTML = '<span class="adlabel">' + esc(t("ad")) + '</span><ins class="kakao_ad_area" style="display:none;width:100%;" data-ad-unit="' + esc(unit.id) + '" data-ad-width="' + (+unit.w) + '" data-ad-height="' + (+unit.h) + '"></ins>';
    need = true;
  });
  if (need) { var sc = document.createElement("script"); sc.async = true; sc.charset = "utf-8"; sc.src = "https://t1.daumcdn.net/kas/static/ba.min.js"; document.body.appendChild(sc); }
  if (S.adsenseClient && /^ca-pub-\d+$/.test(S.adsenseClient)) { var g = document.createElement("script"); g.async = true; g.crossOrigin = "anonymous"; g.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + S.adsenseClient; document.head.appendChild(g); }
})();
