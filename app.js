(function () {
  "use strict";

  const DATA = window.VACATION_DATA || { hotels: [], landmarks: [], timeline: [], budgetDefault: 10000000 };
  const PUBLIC_SHARE_URL = "https://lmsutools.github.io/vacaciones-familia-colombia/";

  const state = {
    activeTab: "hoteles",
    filter: "all",
    sort: "recommended",
    favorites: loadFavorites(),
    cardGalleryCat: {},   // hotelId -> cat
    cardPhotoIdx: {},     // hotelId -> idx
    cardDetailTab: {},    // hotelId -> tab ('meals'|'activities'|'reviews'|'pricing')
    sim: {
      season: "nye",
      nights: 7,
      discounts: true,
      extras: true,
      flightsPerPax: 0,
      budget: DATA.budgetDefault || 10000000,
      focusHotelId: null,
    },
    lightbox: {
      hotelId: null,
      cat: "all",
      idx: 0,
    },
    map: null,
    markersLayer: null,
    selectedMapId: null,
  };

  function loadFavorites() {
    try {
      const raw = localStorage.getItem("vacaciones_favs_v1");
      return raw ? JSON.parse(raw) : ["hotel-las-mananitas", "ecolodge-el-almejal", "sol-caribe-san-andres"];
    } catch {
      return ["hotel-las-mananitas", "ecolodge-el-almejal", "sol-caribe-san-andres"];
    }
  }

  function saveFavorites() {
    try {
      localStorage.setItem("vacaciones_favs_v1", JSON.stringify(state.favorites));
    } catch {
      // ignore storage failure in private windows
    }
  }

  function fmtCOP(n) {
    if (n === null || n === undefined || Number.isNaN(n)) return "Sin cupo web";
    return "$" + Math.round(n).toLocaleString("es-CO") + " COP";
  }

  function fmtShortM(n) {
    if (n === null || n === undefined || Number.isNaN(n)) return "Agotado";
    const m = n / 1000000;
    return "$" + (m >= 10 ? m.toFixed(1).replace(".", ",") : m.toFixed(2).replace(".", ",")) + "M";
  }

  function escHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function getPhotoSrc(photo) {
    if (!photo) return "";
    if (window.__SHAREABLE_MODE__ && photo.remoteUrl && photo.remoteUrl.startsWith("http")) {
      return photo.remoteUrl;
    }
    return photo.localPath || photo.remoteUrl || "";
  }

  function getFilteredPhotos(hotel, cat) {
    const photos = hotel.photos || [];
    if (!cat || cat === "all") return photos;
    const sub = photos.filter((p) => p.category === cat);
    return sub.length ? sub : photos;
  }

  // ---------- Simulator Pricing Engine ----------
  function simulateHotel(hotel, sim) {
    const p = hotel.pricing || {};
    const nights = sim.nights;
    const extras = sim.extras ? (p.mandatoryExtras || 0) : 0;
    const flights = (sim.flightsPerPax || 0) * 4;

    let baseLodging = null;
    let regularLodging = null;
    let available = true;
    let note = "";

    if (hotel.id === "hotel-las-mananitas") {
      const adult = p.adultNight || 440000;
      const child = sim.discounts ? (p.childNight || 275000) : adult;
      const factor = sim.season === "jan" ? 0.92 : 1;
      baseLodging = Math.round(nights * (2 * adult + 2 * child) * factor);
      regularLodging = Math.round(nights * (4 * adult) * factor);
      note = "Tarifa oficial temporada alta; confirmar cupo directo por WhatsApp.";
    } else if (hotel.id === "ecolodge-el-almejal") {
      const adult = p.adultNight || 520000;
      const child = sim.discounts ? (p.childNight || 374000) : adult;
      const factor = sim.season === "jan" ? 0.94 : 1;
      baseLodging = Math.round(nights * (2 * adult + 2 * child) * factor);
      regularLodging = Math.round(nights * (4 * adult) * factor);
      if (nights > 5 && sim.season === "nye") {
        note = "⚠️ Web permite máx. 5 noches ($8.940.000); 6–7 noches requieren extensión directa con el lodge.";
      } else {
        note = "✅ Disponible en vivo en Cloudbeds (incluye 4 excursiones y traslados aeropuerto BSC).";
      }
    } else if (hotel.id === "sol-caribe-san-andres") {
      const rates = p.nightlyRates7 || [1650150, 1650150, 1650150, 2029200, 2029200, 2029200, 2029200];
      let vipSum = 0;
      for (let i = 0; i < nights; i++) vipSum += rates[Math.min(i, rates.length - 1)];
      if (sim.season === "pre-nye") vipSum = Math.round(vipSum * 0.884);
      if (sim.season === "jan") vipSum = Math.round(vipSum * 0.78);
      regularLodging = Math.round(vipSum / 0.95);
      baseLodging = sim.discounts ? vipSum : regularLodging;
      note = nights <= 5
        ? "✅ ¡Bajando a " + nights + " noches entra debajo de $10M COP! Cancela gratis hasta 11 dic."
        : "Disponible 7 noches; cancelación gratis hasta el 11/12/2026.";
    } else if (hotel.id === "decameron-maryland") {
      let disc7 = p.nights7Total;
      let reg7 = p.regular7Total;
      if (sim.season === "pre-nye") { disc7 = p.preNye7Total; reg7 = Math.round(reg7 * 0.92); }
      if (sim.season === "jan") { disc7 = p.jan7Total; reg7 = Math.round(reg7 * 0.8); }
      regularLodging = Math.round(reg7 * (nights / 7));
      baseLodging = Math.round((sim.discounts ? disc7 : reg7) * (nights / 7));
      note = sim.discounts ? "Black Days No Reembolsable (-39,2%). Versión Flex suma +$1,43M/sem." : "Sin descuento Black Days.";
    } else if (hotel.id === "hotel-arena-blanca") {
      let disc7 = p.nights7Total;
      let reg7 = p.regular7Total;
      if (sim.season === "pre-nye") { disc7 = p.preNye7Total; reg7 = p.preNye7Total + 30000; }
      if (sim.season === "jan") { disc7 = p.jan7Total; reg7 = p.jan7Total + 30000; }
      regularLodging = Math.round(reg7 * (nights / 7));
      baseLodging = Math.round((sim.discounts ? disc7 : reg7) * (nights / 7));
      note = "Incluye piscina con tobogán infantil. Tarifa No Reembolsable.";
    } else if (hotel.id === "grand-sirenis-san-andres") {
      let nightRate = 4080000;
      if (sim.season === "pre-nye") nightRate = Math.round(24000000 / 7);
      if (sim.season === "jan") nightRate = Math.round(18500000 / 7);
      baseLodging = nightRate * nights;
      regularLodging = baseLodging;
      note = "Solo queda Junior Presidential Suite. Cancela gratis hasta 26/11/2026.";
    } else if (hotel.id === "wayira-beach") {
      if (sim.season === "nye" || sim.season === "pre-nye") {
        available = false;
        note = "❌ Verificado en onvacation.com: agotado del 23 al 31 dic para 4 personas online.";
      } else {
        const reg7 = p.regular7Total || 9100028;
        const disc7 = p.jan7Total || 4550014;
        regularLodging = Math.round(reg7 * (nights / 7));
        baseLodging = Math.round((sim.discounts ? disc7 : reg7) * (nights / 7));
        note = "✅ Disponible en enero 2027 con Promo Black Days 50% OFF.";
      }
    } else if (hotel.id === "punta-faro-mucura") {
      available = false;
      baseLodging = Math.round((p.nights7Total || 43480000) * (nights / 7));
      regularLodging = baseLodging;
      note = "⚠️ Exige 2 habitaciones en Punta Faro (máx. 3 pax/hab.); Isla Múcura 100% agotado.";
    } else {
      available = false;
      if (sim.season === "pre-nye" && p.preNye7Total) {
        note = "Agotado en Fin de Año (referencia Las Américas pre-Navidad ~$11,84M 7N Plan Full).";
      } else {
        note = "❌ 100% agotado online en estas fechas.";
      }
    }

    const total = baseLodging !== null ? baseLodging + extras + flights : null;
    const saved = baseLodging !== null && regularLodging ? Math.max(0, regularLodging - baseLodging) : 0;
    const fitsBudget = total !== null && available && total <= sim.budget;

    return {
      hotel,
      available,
      baseLodging,
      extras,
      flights,
      total,
      saved,
      fitsBudget,
      note,
    };
  }

  // ---------- Tab Navigation ----------
  function switchTab(tabId) {
    state.activeTab = tabId;
    document.querySelectorAll(".tab-panel").forEach((el) => {
      el.classList.toggle("active", el.id === "tab-" + tabId);
    });
    document.querySelectorAll(".nav-tab, .mnav-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.tab === tabId);
    });
    if (tabId === "mapa") {
      initMapIfNeeded();
      setTimeout(() => {
        if (state.map) state.map.invalidateSize();
      }, 120);
    }
    if (tabId === "simulador") {
      renderSimulator();
    }
    if (tabId === "decision") {
      renderDecisionTab();
    }
  }

  // ---------- Hotel Cards Rendering ----------
  function getFilteredHotels() {
    let list = DATA.hotels.slice();
    if (state.filter === "budget") {
      list = list.filter((h) => h.pricing.fits10M || h.pricing.fits10MShortStay);
    } else if (state.filter === "san-andres") {
      list = list.filter((h) => h.regionGroup === "san-andres");
    } else if (state.filter === "otros") {
      list = list.filter((h) => h.regionGroup === "otros");
    } else if (state.filter === "discount") {
      list = list.filter((h) => h.discount && h.discount.hasDiscount);
    } else if (state.filter === "favorites") {
      list = list.filter((h) => state.favorites.includes(h.id));
    }

    if (state.sort === "price-asc") {
      list.sort((a, b) => {
        const pa = a.pricing.nights7Total || a.pricing.jan7Total || 999999999;
        const pb = b.pricing.nights7Total || b.pricing.jan7Total || 999999999;
        return pa - pb;
      });
    } else if (state.sort === "rating-desc") {
      const parseScore = (s) => {
        const m = String(s || "").match(/[\d.]+/);
        if (!m) return 0;
        const v = parseFloat(m[0]);
        return v > 5 ? v / 2 : v;
      };
      list.sort((a, b) => parseScore(b.reviews.overall) - parseScore(a.reviews.overall));
    } else if (state.sort === "available-first") {
      list.sort((a, b) => Number(b.pricing.isAvailableNye) - Number(a.pricing.isAvailableNye) || a.rank - b.rank);
    } else {
      list.sort((a, b) => a.rank - b.rank);
    }
    return list;
  }

  function renderHotels() {
    const grid = document.getElementById("hotels-grid");
    const favChip = document.getElementById("fav-count-chip");
    if (favChip) favChip.textContent = String(state.favorites.length);

    const list = getFilteredHotels();
    if (!list.length) {
      grid.innerHTML = `<div class="card-panel"><p class="muted">No hay hoteles en este filtro. Prueba marcando ❤️ Favoritos o vuelve a "Todos".</p></div>`;
      return;
    }

    grid.innerHTML = list.map((h) => buildHotelCardHTML(h)).join("");
    bindCardEvents();
  }

  function buildHotelCardHTML(h) {
    const isFav = state.favorites.includes(h.id);
    const cat = state.cardGalleryCat[h.id] || "all";
    const photos = getFilteredPhotos(h, cat);
    const idx = Math.min(state.cardPhotoIdx[h.id] || 0, Math.max(0, photos.length - 1));
    state.cardPhotoIdx[h.id] = idx;
    const curPhoto = photos[idx] || { localPath: "", remoteUrl: "", caption: h.name };

    const allPhotos = h.photos || [];
    const roomCount = allPhotos.filter((p) => p.category === "habitaciones").length;
    const instCount = allPhotos.filter((p) => p.category === "instalaciones").length;
    const foodCount = allPhotos.filter((p) => p.category === "gastronomia").length;
    const proofCount = allPhotos.filter((p) => p.category === "captura").length;

    const p = h.pricing;
    let mainPriceHtml = "";
    let subPriceHtml = "";
    let budgetNoteHtml = "";

    if (h.id === "ecolodge-el-almejal") {
      mainPriceHtml = `<span class="price-main">${fmtCOP(p.nights5Total)}</span>`;
      subPriceHtml = `5 noches en vivo (26–31 dic) · 7 noches teórico: ${fmtCOP(p.nights7Total)} · ${escHtml(p.ivaIncludedText)}`;
      budgetNoteHtml = `<div class="budget-note ok">✅ Entra debajo de $10M en plan oficial de 5 noches</div>`;
    } else if (h.id === "wayira-beach") {
      mainPriceHtml = `<span class="price-strike">${fmtCOP(p.regular7Total)}</span> <span class="price-main">${fmtCOP(p.jan7Total)}</span>`;
      subPriceHtml = `7 noches en enero con 50% OFF · Fin de Año (23–31 dic) agotado online para 4 pax`;
      budgetNoteHtml = `<div class="budget-note over">⚠️ Ahorras $4,55M si viajan en enero</div>`;
    } else if (p.nights7Total) {
      mainPriceHtml = `${p.savingsAmount > 0 ? `<span class="price-strike">${fmtCOP(p.regular7Total)}</span> ` : ""}<span class="price-main">${fmtCOP(p.nights7Total)}</span>`;
      subPriceHtml = `7 noches totales (2 ad + 2 niños) · ${escHtml(p.ivaIncludedText)}`;
      if (p.fits10M) {
        budgetNoteHtml = `<div class="budget-note ok">✅ Prácticamente exacto en tu tope de $10M (incluye 3 tours)</div>`;
      } else if (p.fits10MShortStay) {
        budgetNoteHtml = `<div class="budget-note over">⚠️ +${fmtCOP(p.nights7Total - 10000000)} en 7N · ✅ Entra en $9.008.850 si ajustas a 5 noches</div>`;
      } else if (h.status === "sold_out") {
        budgetNoteHtml = `<div class="budget-note out">⛔ Exige 2 habitaciones ($43,48M) y lanchas aparte</div>`;
      } else {
        budgetNoteHtml = `<div class="budget-note over">⚠️ Supera el tope de $10M por +${fmtCOP(p.nights7Total - 10000000)}</div>`;
      }
    } else {
      mainPriceHtml = `<span class="price-main">Agotado online</span>`;
      subPriceHtml = escHtml(p.ivaIncludedText);
      budgetNoteHtml = `<div class="budget-note out">⛔ 0 cupos en motores web para 26 dic – 2 ene</div>`;
    }

    const dtab = state.cardDetailTab[h.id] || "meals";
    const statusBadgeClass = h.badgeTone === "green" ? "badge-green" : h.badgeTone === "amber" ? "badge-amber" : "badge-slate";

    return `
      <article class="hotel-card ${h.status === "sold_out" ? "is-soldout" : ""}" data-hotel-id="${h.id}">
        <div class="gallery-stage" data-action="open-lightbox" data-id="${h.id}">
          <img src="${escHtml(getPhotoSrc(curPhoto))}" alt="${escHtml(curPhoto.caption || h.name)}" loading="lazy" data-fallback="${escHtml(curPhoto.remoteUrl || "")}" onerror="if(this.dataset.fallback && this.src!==this.dataset.fallback){this.src=this.dataset.fallback;}" />
          <div class="gallery-overlay-top">
            <div class="badge-stack">
              <span class="badge ${statusBadgeClass}">${escHtml(h.statusLabel)}</span>
              ${h.discount && h.discount.hasDiscount ? `<span class="badge badge-promo">${escHtml(h.discount.badge)}</span>` : ""}
            </div>
            <button class="fav-btn ${isFav ? "active" : ""}" data-action="toggle-fav" data-id="${h.id}" type="button" aria-label="Marcar como favorito">
              ${isFav ? "❤️" : "🤍"}
            </button>
          </div>
          ${photos.length > 1 ? `
            <button class="car-arrow prev" data-action="prev-photo" data-id="${h.id}" type="button" aria-label="Foto anterior">‹</button>
            <button class="car-arrow next" data-action="next-photo" data-id="${h.id}" type="button" aria-label="Foto siguiente">›</button>
          ` : ""}
          <div class="gallery-overlay-bottom">
            <span class="photo-caption-text">${escHtml(curPhoto.caption || h.name)}</span>
            <span class="photo-count-pill">📷 ${idx + 1}/${photos.length}</span>
          </div>
        </div>

        <div class="gallery-cat-bar">
          <button class="gcat-btn ${cat === "all" ? "active" : ""}" data-action="set-gcat" data-id="${h.id}" data-cat="all" type="button">Todas (${allPhotos.length})</button>
          ${roomCount ? `<button class="gcat-btn ${cat === "habitaciones" ? "active" : ""}" data-action="set-gcat" data-id="${h.id}" data-cat="habitaciones" type="button">🛏️ Habitaciones (${roomCount})</button>` : ""}
          ${instCount ? `<button class="gcat-btn ${cat === "instalaciones" ? "active" : ""}" data-action="set-gcat" data-id="${h.id}" data-cat="instalaciones" type="button">🏖️ Playa y Piscina (${instCount})</button>` : ""}
          ${foodCount ? `<button class="gcat-btn ${cat === "gastronomia" ? "active" : ""}" data-action="set-gcat" data-id="${h.id}" data-cat="gastronomia" type="button">🍽️ Comida (${foodCount})</button>` : ""}
          ${proofCount ? `<button class="gcat-btn ${cat === "captura" ? "active" : ""}" data-action="set-gcat" data-id="${h.id}" data-cat="captura" type="button">🧾 Captura Oficial</button>` : ""}
        </div>

        <div class="card-body">
          <div class="card-head">
            <div>
              <div class="dest-kicker">${escHtml(h.destination)} · ${escHtml(h.chain)}</div>
              <h3 class="hotel-title">${escHtml(h.name)}</h3>
              <div class="room-subtitle">🛏️ ${escHtml(h.roomType)}</div>
            </div>
            <div class="rating-pill">
              <strong>${escHtml(h.reviews.overall)}</strong>
              <span>Reviews</span>
            </div>
          </div>

          <div class="price-box">
            <div class="price-row">${mainPriceHtml}</div>
            <div class="price-sub">${subPriceHtml}</div>
            ${p.savingsAmount > 0 ? `<div class="savings-tag">💸 Ahorras ${fmtCOP(p.savingsAmount)} (${escHtml(h.discount.badge)})</div>` : ""}
            ${budgetNoteHtml}
          </div>

          <div class="detail-tabs">
            <button class="dtab-btn ${dtab === "meals" ? "active" : ""}" data-action="set-dtab" data-id="${h.id}" data-dtab="meals" type="button">🍽️ Comida</button>
            <button class="dtab-btn ${dtab === "activities" ? "active" : ""}" data-action="set-dtab" data-id="${h.id}" data-dtab="activities" type="button">🤿 Qué hacer</button>
            <button class="dtab-btn ${dtab === "reviews" ? "active" : ""}" data-action="set-dtab" data-id="${h.id}" data-dtab="reviews" type="button">⭐ Reviews</button>
            <button class="dtab-btn ${dtab === "pricing" ? "active" : ""}" data-action="set-dtab" data-id="${h.id}" data-dtab="pricing" type="button">💰 Extras</button>
          </div>

          <div class="detail-content">
            ${buildDetailTabContent(h, dtab)}
          </div>

          <div class="card-footer-actions">
            <a class="btn-card-primary" href="${escHtml(h.bookingUrl)}" target="_blank" rel="noopener noreferrer">🌐 Ir a Reserva Oficial</a>
            <button class="btn-card-secondary" data-action="simulate-hotel" data-id="${h.id}" type="button">🧮 Simular</button>
            <button class="btn-card-secondary" data-action="open-lightbox" data-id="${h.id}" type="button">🖼️ Ver ${allPhotos.length} fotos</button>
          </div>
        </div>
      </article>
    `;
  }

  function buildDetailTabContent(h, tab) {
    if (tab === "meals") {
      return `
        <div class="mini-heading">${escHtml(h.meals.planName)}</div>
        <ul class="detail-list">
          ${h.meals.included.map((i) => `<li>✅ ${escHtml(i)}</li>`).join("")}
          ${h.meals.excluded.map((e) => `<li>❌ ${escHtml(e)}</li>`).join("")}
        </ul>
      `;
    }
    if (tab === "activities") {
      return `
        <div class="mini-heading">En el hotel y paseos incluidos</div>
        <ul class="detail-list">
          ${h.activities.includedHotel.map((a) => `<li>🏖️ ${escHtml(a)}</li>`).join("")}
        </ul>
        <div class="mini-heading">Especial para niños de 7 y 10 años</div>
        <ul class="detail-list">
          ${h.activities.kidsFriendly.map((k) => `<li>👦👧 ${escHtml(k)}</li>`).join("")}
        </ul>
      `;
    }
    if (tab === "reviews") {
      return `
        <div class="review-bars">
          ${h.reviews.sources.map((s) => `<div class="rev-source"><strong>${escHtml(s.score)}</strong><span>${escHtml(s.name)}</span></div>`).join("")}
        </div>
        <div class="mini-heading">Lo que más elogian las familias</div>
        <ul class="detail-list">
          ${h.reviews.pros.map((x) => `<li>👍 ${escHtml(x)}</li>`).join("")}
        </ul>
        <div class="mini-heading">Puntos a tener en cuenta</div>
        <ul class="detail-list">
          ${h.reviews.cons.map((x) => `<li>⚠️ ${escHtml(x)}</li>`).join("")}
        </ul>
      `;
    }
    // pricing / extras
    return `
      <div class="mini-heading">Descuentos, cancelación y extras en destino</div>
      <ul class="detail-list">
        <li><strong>Descuento / Tarifa:</strong> ${escHtml(h.discount.detail)}</li>
        <li><strong>Política de cancelación:</strong> ${escHtml(h.cancellation)}</li>
        <li><strong>Extras fuera de tarifa:</strong> ${escHtml(h.pricing.mandatoryExtrasLabel)}</li>
        <li><strong>Sitio web oficial:</strong> <a href="${escHtml(h.officialUrl)}" target="_blank" rel="noopener noreferrer">${escHtml(h.officialUrl)}</a></li>
      </ul>
      <div class="warn-box">🛡️ ${escHtml(h.antiScamNote)}</div>
    `;
  }

  function bindCardEvents() {
    document.querySelectorAll(".gallery-stage").forEach((stage) => {
      let startX = 0;
      stage.addEventListener("touchstart", (e) => {
        if (e.touches && e.touches[0]) startX = e.touches[0].clientX;
      }, { passive: true });
      stage.addEventListener("touchend", (e) => {
        if (!e.changedTouches || !e.changedTouches[0]) return;
        const dx = e.changedTouches[0].clientX - startX;
        const id = stage.dataset.id;
        if (Math.abs(dx) > 40 && id) {
          stepCardPhoto(id, dx < 0 ? 1 : -1);
        }
      }, { passive: true });
    });
  }

  function stepCardPhoto(id, delta) {
    const h = DATA.hotels.find((x) => x.id === id);
    if (!h) return;
    const photos = getFilteredPhotos(h, state.cardGalleryCat[id] || "all");
    if (!photos.length) return;
    const cur = state.cardPhotoIdx[id] || 0;
    state.cardPhotoIdx[id] = (cur + delta + photos.length) % photos.length;
    renderHotels();
  }

  // ---------- Lightbox ----------
  function openLightbox(hotelId, forcedCat) {
    const h = DATA.hotels.find((x) => x.id === hotelId);
    if (!h) return;
    state.lightbox.hotelId = hotelId;
    state.lightbox.cat = forcedCat || state.cardGalleryCat[hotelId] || "all";
    state.lightbox.idx = forcedCat ? 0 : (state.cardPhotoIdx[hotelId] || 0);
    renderLightbox();
    document.getElementById("lightbox-modal").classList.remove("hidden");
  }

  function renderLightbox() {
    const h = DATA.hotels.find((x) => x.id === state.lightbox.hotelId);
    if (!h) return;
    const allPhotos = h.photos || [];
    const photos = getFilteredPhotos(h, state.lightbox.cat);
    const idx = Math.min(state.lightbox.idx, Math.max(0, photos.length - 1));
    state.lightbox.idx = idx;
    const cur = photos[idx];

    document.getElementById("lb-hotel-title").textContent = h.name;
    document.getElementById("lb-counter").textContent = `${idx + 1} / ${photos.length}`;

    const cats = [
      { key: "all", label: `Todas (${allPhotos.length})` },
      { key: "habitaciones", label: `🛏️ Habitaciones (${allPhotos.filter((p) => p.category === "habitaciones").length})` },
      { key: "instalaciones", label: `🏖️ Playa y Piscina (${allPhotos.filter((p) => p.category === "instalaciones").length})` },
      { key: "gastronomia", label: `🍽️ Comida (${allPhotos.filter((p) => p.category === "gastronomia").length})` },
      { key: "captura", label: `🧾 Captura (${allPhotos.filter((p) => p.category === "captura").length})` },
    ].filter((c) => c.key === "all" || allPhotos.some((p) => p.category === c.key));

    document.getElementById("lb-cats").innerHTML = cats.map((c) => `
      <button class="lb-cat-btn ${state.lightbox.cat === c.key ? "active" : ""}" data-lb-cat="${c.key}" type="button">${escHtml(c.label)}</button>
    `).join("");

    const imgEl = document.getElementById("lb-img");
    imgEl.src = getPhotoSrc(cur);
    imgEl.alt = cur ? cur.caption : h.name;
    imgEl.onerror = () => {
      if (cur && cur.remoteUrl && imgEl.src !== cur.remoteUrl) imgEl.src = cur.remoteUrl;
    };
    document.getElementById("lb-caption").textContent = cur ? cur.caption : "";

    document.getElementById("lb-thumbs").innerHTML = photos.map((p, i) => `
      <img class="lb-thumb ${i === idx ? "active" : ""}" data-lb-idx="${i}" src="${escHtml(getPhotoSrc(p))}" alt="${escHtml(p.caption)}" loading="lazy" />
    `).join("");
  }

  // ---------- Interactive Map ----------
  const REGION_VIEWS = {
    "colombia": { center: [9.6, -77.6], zoom: 6 },
    "san-andres": { center: [12.578, -81.698], zoom: 14 },
    "capurgana": { center: [8.636, -77.351], zoom: 14 },
    "bahia-solano": { center: [6.112, -77.432], zoom: 13 },
    "mayapo": { center: [11.645, -72.796], zoom: 13 },
    "covenas-mucura": { center: [9.60, -75.78], zoom: 10 },
  };

  function initMapIfNeeded() {
    if (state.map || typeof L === "undefined") return;
    const map = L.map("vacation-map", { scrollWheelZoom: false }).setView([9.6, -77.6], 6);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OpenStreetMap &copy; CARTO",
      maxZoom: 19,
    }).addTo(map);

    const layer = L.layerGroup().addTo(map);
    state.map = map;
    state.markersLayer = layer;

    DATA.hotels.forEach((h) => {
      const p = h.pricing;
      let cls = "out";
      let text = "Agotado";
      if (h.id === "ecolodge-el-almejal") {
        cls = "ok";
        text = fmtShortM(p.nights5Total) + " (5N)";
      } else if (p.fits10M) {
        cls = "ok";
        text = fmtShortM(p.nights7Total);
      } else if (p.isAvailableNye && p.nights7Total) {
        cls = "over";
        text = fmtShortM(p.nights7Total);
      } else if (h.id === "wayira-beach") {
        cls = "over";
        text = "Ene " + fmtShortM(p.jan7Total);
      }

      const icon = L.divIcon({
        className: "",
        html: `<div class="price-pin ${cls}">${escHtml(text)}</div>`,
        iconSize: [null, null],
      });

      const marker = L.marker(h.coords, { icon }).addTo(layer);
      marker.on("click", () => selectMapHotel(h.id));
    });

    (DATA.landmarks || []).forEach((lm) => {
      const icon = L.divIcon({
        className: "",
        html: `<div class="price-pin poi">${escHtml(lm.name.split("(")[0].trim())}</div>`,
        iconSize: [null, null],
      });
      L.marker(lm.coords, { icon }).bindPopup(`<strong>${escHtml(lm.name)}</strong><br>${escHtml(lm.note)}`).addTo(layer);
    });
  }

  function selectMapHotel(hotelId) {
    const h = DATA.hotels.find((x) => x.id === hotelId);
    if (!h) return;
    state.selectedMapId = hotelId;
    const firstPhoto = (h.photos && h.photos[0]) || null;
    const roomPhoto = (h.photos || []).find((p) => p.category === "habitaciones") || firstPhoto;
    const priceLine = h.id === "ecolodge-el-almejal"
      ? `${fmtCOP(h.pricing.nights5Total)} (5 noches en vivo)`
      : h.id === "wayira-beach"
        ? `Agotado dic 23–31 · Enero ${fmtCOP(h.pricing.jan7Total)}`
        : h.pricing.nights7Total
          ? `${fmtCOP(h.pricing.nights7Total)} (7 noches)`
          : "Agotado online 26 dic – 2 ene";

    document.getElementById("map-preview-card").innerHTML = `
      ${roomPhoto ? `<img class="map-preview-img" src="${escHtml(getPhotoSrc(roomPhoto))}" alt="${escHtml(h.name)}" />` : ""}
      <div class="dest-kicker">${escHtml(h.destination)}</div>
      <h3>${escHtml(h.name)}</h3>
      <p class="muted">🛏️ ${escHtml(h.roomType)}</p>
      <p style="margin:8px 0;font-weight:800;font-size:1.05rem;">${escHtml(priceLine)}</p>
      <p class="muted" style="margin-bottom:12px;">🍽️ ${escHtml(h.meals.planName)}</p>
      <div class="share-modal-btns">
        <button class="btn-card-primary" data-action="open-lightbox" data-id="${h.id}" type="button">🖼️ Ver ${h.photos.length} fotos</button>
        <button class="btn-card-secondary" data-action="jump-hotel" data-id="${h.id}" type="button">Ver detalle</button>
      </div>
    `;
  }

  // ---------- Simulator ----------
  function renderSimulator() {
    const s = state.sim;
    document.getElementById("sim-nights-label").textContent = `${s.nights} noches`;
    document.getElementById("sim-flights-label").textContent = s.flightsPerPax > 0 ? `${fmtCOP(s.flightsPerPax)} / pers. (${fmtCOP(s.flightsPerPax * 4)})` : "$0 COP (Solo hotel)";
    document.getElementById("sim-budget-label").textContent = fmtCOP(s.budget);

    const seasonTxt = s.season === "nye" ? "Fin de Año" : s.season === "pre-nye" ? "Antes del 31 dic" : "Enero 2027";
    document.getElementById("sim-summary-pill").textContent = `${seasonTxt} · ${s.nights} noches · ${s.discounts ? "Con descuentos" : "Sin descuentos"} · ${s.extras ? "Con extras" : "Sin extras"}`;

    const rows = DATA.hotels.map((h) => simulateHotel(h, s));
    rows.sort((a, b) => {
      if (a.available !== b.available) return Number(b.available) - Number(a.available);
      if (a.total === null && b.total === null) return a.hotel.rank - b.hotel.rank;
      if (a.total === null) return 1;
      if (b.total === null) return -1;
      return a.total - b.total;
    });

    const underBudget = rows.filter((r) => r.fitsBudget);
    const insightBox = document.getElementById("sim-quick-insight");
    if (underBudget.length) {
      insightBox.innerHTML = `✅ <strong>${underBudget.length} opción(es) entran</strong> dentro de ${fmtCOP(s.budget)}: ${underBudget.map((r) => `<strong>${escHtml(r.hotel.name)}</strong> (${fmtCOP(r.total)})`).join(", ")}.`;
    } else {
      const best = rows.find((r) => r.available && r.total !== null);
      insightBox.innerHTML = best
        ? `⚠️ Ninguna opción de ${s.nights} noches baja de ${fmtCOP(s.budget)} con estas opciones. La más cercana es <strong>${escHtml(best.hotel.name)}</strong> por <strong>${fmtCOP(best.total)}</strong>. Prueba bajar a <strong>5 noches</strong> o mirar <strong>Enero 2027</strong>.`
        : `⚠️ Todas las opciones muestran cupo limitado para estas fechas.`;
    }

    const maxScale = Math.max(s.budget * 1.6, 18000000);
    document.getElementById("simulator-results").innerHTML = rows.map((r) => {
      const h = r.hotel;
      const pct = r.total ? Math.min(100, Math.round((r.total / maxScale) * 100)) : 100;
      const cls = !r.available ? "out" : r.fitsBudget ? "ok" : "over";
      const diff = r.total !== null ? r.total - s.budget : null;
      const diffLabel = !r.available
        ? (r.total ? `Referencia ${fmtCOP(r.total)}` : "Sin cupo online")
        : diff <= 0
          ? `✅ Te sobran ${fmtCOP(Math.abs(diff))}`
          : `⚠️ +${fmtCOP(diff)} sobre presupuesto`;

      return `
        <div class="sim-result-card">
          <div class="sim-result-top">
            <div>
              <div class="dest-kicker">${escHtml(h.destination)}</div>
              <strong>${escHtml(h.name)}</strong>
              <div class="sim-breakdown">${escHtml(r.note)}</div>
            </div>
            <div class="sim-total">
              ${r.total !== null ? fmtCOP(r.total) : "Agotado"}
              <div class="budget-note ${cls}" style="margin-top:2px;">${escHtml(diffLabel)}</div>
            </div>
          </div>
          <div class="bar-track"><div class="bar-fill ${cls}" style="width:${pct}%"></div></div>
          <div class="sim-breakdown">
            ${r.baseLodging !== null ? `Hotel: ${fmtCOP(r.baseLodging)}` : "Sin tarifa"}
            ${r.extras > 0 ? ` + Extras destino: ${fmtCOP(r.extras)}` : ""}
            ${r.flights > 0 ? ` + Vuelos (×4): ${fmtCOP(r.flights)}` : ""}
            ${r.saved > 0 ? ` · <strong style="color:#991b1b;">Ahorro aplicado: ${fmtCOP(r.saved)}</strong>` : ""}
          </div>
        </div>
      `;
    }).join("");
  }

  // ---------- Decision & Comparison Tab ----------
  function renderDecisionTab() {
    document.getElementById("urgency-timeline").innerHTML = (DATA.timeline || []).map((t) => `
      <div class="timeline-item">
        <div class="t-date ${t.urgent ? "urgent" : ""}">${escHtml(t.date)}</div>
        <div>
          <strong>${escHtml(t.title)}</strong>
          <p class="muted">${escHtml(t.detail)}</p>
        </div>
      </div>
    `).join("");

    let selected = DATA.hotels.filter((h) => state.favorites.includes(h.id));
    if (selected.length < 2) {
      selected = DATA.hotels.slice(0, 4);
      document.getElementById("compare-subtitle").textContent = "Mostrando automáticamente las 4 mejores opciones (marca ❤️ en los hoteles para personalizar esta tabla).";
    } else {
      document.getElementById("compare-subtitle").textContent = `Comparando tus ${selected.length} hoteles favoritos ❤️ lado a lado.`;
    }

    const tbl = document.getElementById("compare-table");
    tbl.innerHTML = `
      <thead>
        <tr>
          <th>Criterio</th>
          ${selected.map((h) => `<th>${escHtml(h.name)}<br><small style="color:var(--teal);">${escHtml(h.destination)}</small></th>`).join("")}
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Precio Fin de Año</strong></td>
          ${selected.map((h) => `<td><strong>${h.id === "ecolodge-el-almejal" ? fmtCOP(h.pricing.nights5Total) + " (5N)" : h.pricing.nights7Total ? fmtCOP(h.pricing.nights7Total) + " (7N)" : "Agotado dic (Ene " + fmtShortM(h.pricing.jan7Total) + ")"}</strong></td>`).join("")}
        </tr>
        <tr>
          <td><strong>Descuento</strong></td>
          ${selected.map((h) => `<td>${escHtml(h.discount.badge)}</td>`).join("")}
        </tr>
        <tr>
          <td><strong>Plan Alimentación</strong></td>
          ${selected.map((h) => `<td>${escHtml(h.meals.planName)}</td>`).join("")}
        </tr>
        <tr>
          <td><strong>Para niños 7 y 10</strong></td>
          ${selected.map((h) => `<td>${escHtml(h.activities.kidsFriendly[0] || "")}</td>`).join("")}
        </tr>
        <tr>
          <td><strong>Reviews</strong></td>
          ${selected.map((h) => `<td><strong>${escHtml(h.reviews.overall)}</strong> — ${escHtml(h.reviews.pros[0] || "")}</td>`).join("")}
        </tr>
        <tr>
          <td><strong>Extras / Cancelación</strong></td>
          ${selected.map((h) => `<td>${escHtml(h.pricing.mandatoryExtrasLabel)}<br><small>${escHtml(h.cancellation)}</small></td>`).join("")}
        </tr>
      </tbody>
    `;
  }

  // ---------- Share Modal + Pure-JS QR SVG Generator ----------
  function getShareLanUrl() {
    const loc = window.location;
    if (loc.protocol === "https:") {
      return loc.origin + loc.pathname;
    }
    return PUBLIC_SHARE_URL;
  }

  function buildWhatsAppText() {
    const favs = DATA.hotels.filter((h) => state.favorites.includes(h.id));
    const pick = favs.length ? favs : DATA.hotels.slice(0, 4);
    const lines = [
      "🌴 *Opciones Vacaciones Familia (2 adultos + 2 niños 7 y 10 años)*",
      "📅 26 dic 2026 – 2 ene 2027 · 🎯 Presupuesto ref: $10.000.000 COP",
      "",
    ];
    pick.forEach((h, i) => {
      const priceStr = h.id === "ecolodge-el-almejal"
        ? `${fmtCOP(h.pricing.nights5Total)} (5N en vivo)`
        : h.id === "wayira-beach"
          ? `Agotado Fin de Año · Ene ${fmtCOP(h.pricing.jan7Total)} (50% OFF)`
          : h.pricing.nights7Total
            ? `${fmtCOP(h.pricing.nights7Total)} (7N)`
            : "Agotado online";
      lines.push(`${i + 1}. *${h.name}* (${h.destination})`);
      lines.push(`   • Precio: ${priceStr}`);
      lines.push(`   • Incluye: ${h.meals.planName}`);
      lines.push(`   • Web oficial: ${h.officialUrl}`);
    });
    lines.push("");
    lines.push("📲 Ábrelo en tu celular o tablet (fotos de habitaciones, mapa y simulador): " + getShareLanUrl());
    return lines.join("\n");
  }

  function openShareModal() {
    const lanUrl = getShareLanUrl();
    document.getElementById("lan-url-text").textContent = lanUrl;
    const qrContainer = document.getElementById("qr-container");
    qrContainer.innerHTML = renderQrSvg(lanUrl, 168);

    const waText = buildWhatsAppText();
    document.getElementById("wa-message-preview").value = waText;
    document.getElementById("btn-wa-link").href = "https://wa.me/?text=" + encodeURIComponent(waText);
    document.getElementById("share-modal").classList.remove("hidden");
  }

  // Minimal ISO-compliant QR Code Byte-Mode Encoder (Versions 1..4, ECC-L)
  function renderQrSvg(text, sizePx) {
    try {
      const matrix = generateQrMatrix(text);
      const n = matrix.length;
      const cell = sizePx / (n + 4);
      let rects = "";
      for (let r = 0; r < n; r++) {
        for (let c = 0; c < n; c++) {
          if (matrix[r][c]) {
            rects += `<rect x="${((c + 2) * cell).toFixed(2)}" y="${((r + 2) * cell).toFixed(2)}" width="${(cell + 0.08).toFixed(2)}" height="${(cell + 0.08).toFixed(2)}" fill="#111827"/>`;
          }
        }
      }
      return `<svg xmlns="http://www.w3.org/2000/svg" width="${sizePx}" height="${sizePx}" viewBox="0 0 ${sizePx} ${sizePx}" role="img" aria-label="Código QR para abrir en móvil"><rect width="${sizePx}" height="${sizePx}" fill="#ffffff"/>${rects}</svg>`;
    } catch {
      return `<div style="padding:14px;font-size:12px;">URL: ${escHtml(text)}</div>`;
    }
  }

  function generateQrMatrix(text) {
    const bytes = Array.from(new TextEncoder().encode(text));
    // Version capacities (ECC-L byte mode): v1=17, v2=32, v3=53, v4=78
    const specs = [
      { ver: 1, totalCodewords: 26, dataCap: 19, ecc: 7, align: [] },
      { ver: 2, totalCodewords: 44, dataCap: 34, ecc: 10, align: [18] },
      { ver: 3, totalCodewords: 70, dataCap: 55, ecc: 15, align: [22] },
      { ver: 4, totalCodewords: 100, dataCap: 80, ecc: 20, align: [26] },
    ];
    const spec = specs.find((s) => bytes.length + 2 <= s.dataCap) || specs[3];
    const ver = spec.ver;
    const size = 17 + ver * 4;

    // Build data bitstream: 0100 (byte mode), length (8 bits), data, terminator, padding
    const bits = [];
    const pushBits = (val, len) => { for (let i = len - 1; i >= 0; i--) bits.push((val >> i) & 1); };
    pushBits(0b0100, 4);
    pushBits(bytes.length, 8);
    bytes.forEach((b) => pushBits(b, 8));
    for (let i = 0; i < 4 && bits.length < spec.dataCap * 8; i++) bits.push(0);
    while (bits.length % 8 !== 0) bits.push(0);
    const padBytes = [0xec, 0x11];
    let pIdx = 0;
    while (bits.length < spec.dataCap * 8) {
      pushBits(padBytes[pIdx % 2], 8);
      pIdx++;
    }

    const dataBytes = [];
    for (let i = 0; i < bits.length; i += 8) {
      let b = 0;
      for (let j = 0; j < 8; j++) b = (b << 1) | bits[i + j];
      dataBytes.push(b);
    }

    // Reed-Solomon ECC over GF(256) poly 0x11d
    const gfExp = new Array(512), gfLog = new Array(256);
    let x = 1;
    for (let i = 0; i < 255; i++) {
      gfExp[i] = x;
      gfLog[x] = i;
      x <<= 1;
      if (x & 0x100) x ^= 0x11d;
    }
    for (let i = 255; i < 512; i++) gfExp[i] = gfExp[i - 255];
    const gfMul = (a, b) => (a === 0 || b === 0 ? 0 : gfExp[gfLog[a] + gfLog[b]]);

    let gen = [1];
    for (let i = 0; i < spec.ecc; i++) {
      const next = new Array(gen.length + 1).fill(0);
      const factor = gfExp[i];
      for (let j = 0; j < gen.length; j++) {
        next[j] ^= gen[j];
        next[j + 1] ^= gfMul(gen[j], factor);
      }
      gen = next;
    }

    const msg = dataBytes.concat(new Array(spec.ecc).fill(0));
    for (let i = 0; i < dataBytes.length; i++) {
      const coef = msg[i];
      if (coef !== 0) {
        for (let j = 0; j < gen.length; j++) msg[i + j] ^= gfMul(gen[j], coef);
      }
    }
    const allBytes = dataBytes.concat(msg.slice(dataBytes.length));

    const mat = Array.from({ length: size }, () => new Array(size).fill(null));
    const reserved = Array.from({ length: size }, () => new Array(size).fill(false));

    const setMod = (r, c, val, res = true) => {
      if (r >= 0 && r < size && c >= 0 && c < size) {
        mat[r][c] = val ? 1 : 0;
        if (res) reserved[r][c] = true;
      }
    };

    const drawFinder = (r0, c0) => {
      for (let dr = -1; dr <= 7; dr++) {
        for (let dc = -1; dc <= 7; dc++) {
          const r = r0 + dr, c = c0 + dc;
          if (r < 0 || r >= size || c < 0 || c >= size) continue;
          const inBox = dr >= 0 && dr <= 6 && dc >= 0 && dc <= 6;
          const dark = inBox && (dr === 0 || dr === 6 || dc === 0 || dc === 6 || (dr >= 2 && dr <= 4 && dc >= 2 && dc <= 4));
          setMod(r, c, dark, true);
        }
      }
    };

    drawFinder(0, 0);
    drawFinder(0, size - 7);
    drawFinder(size - 7, 0);

    spec.align.forEach((ar) => {
      for (let dr = -2; dr <= 2; dr++) {
        for (let dc = -2; dc <= 2; dc++) {
          const dark = Math.max(Math.abs(dr), Math.abs(dc)) !== 1;
          setMod(ar + dr, ar + dc, dark, true);
        }
      }
    });

    for (let i = 8; i < size - 8; i++) {
      setMod(6, i, i % 2 === 0, true);
      setMod(i, 6, i % 2 === 0, true);
    }
    setMod(size - 8, 8, 1, true);

    // Reserve format strips
    for (let i = 0; i < 9; i++) {
      if (!reserved[8][i]) reserved[8][i] = true;
      if (!reserved[i][8]) reserved[i][8] = true;
    }
    for (let i = size - 8; i < size; i++) {
      reserved[8][i] = true;
      reserved[i][8] = true;
    }

    // Place data bits zig-zag with mask 0 ((r + c) % 2 === 0)
    const allBits = [];
    allBytes.forEach((b) => { for (let i = 7; i >= 0; i--) allBits.push((b >> i) & 1); });
    let bitIdx = 0;
    let dirUp = true;
    for (let col = size - 1; col > 0; col -= 2) {
      if (col === 6) col--;
      for (let step = 0; step < size; step++) {
        const r = dirUp ? size - 1 - step : step;
        for (let dc = 0; dc < 2; dc++) {
          const c = col - dc;
          if (!reserved[r][c]) {
            const rawBit = bitIdx < allBits.length ? allBits[bitIdx++] : 0;
            const masked = rawBit ^ (((r + c) % 2 === 0) ? 1 : 0);
            mat[r][c] = masked;
          }
        }
      }
      dirUp = !dirUp;
    }

    // Format info for ECC-L (01) + Mask 0 (000) -> 0x77C4 (111011111000100)
    const fmt = 0b111011111000100;
    const fmtBits = [];
    for (let i = 14; i >= 0; i--) fmtBits.push((fmt >> i) & 1);
    const coords1 = [[8,0],[8,1],[8,2],[8,3],[8,4],[8,5],[8,7],[8,8],[7,8],[5,8],[4,8],[3,8],[2,8],[1,8],[0,8]];
    const coords2 = [[size-1,8],[size-2,8],[size-3,8],[size-4,8],[size-5,8],[size-6,8],[size-7,8],[8,size-8],[8,size-7],[8,size-6],[8,size-5],[8,size-4],[8,size-3],[8,size-2],[8,size-1]];
    for (let i = 0; i < 15; i++) {
      mat[coords1[i][0]][coords1[i][1]] = fmtBits[i];
      mat[coords2[i][0]][coords2[i][1]] = fmtBits[i];
    }
    return mat;
  }

  // ---------- Event Wiring ----------
  function bindEvents() {
    document.addEventListener("click", (e) => {
      const tabBtn = e.target.closest("[data-tab]");
      if (tabBtn) {
        switchTab(tabBtn.dataset.tab);
        return;
      }

      const chip = e.target.closest("#filter-chips .chip");
      if (chip) {
        state.filter = chip.dataset.filter;
        document.querySelectorAll("#filter-chips .chip").forEach((c) => c.classList.toggle("active", c === chip));
        renderHotels();
        return;
      }

      const zoomBtn = e.target.closest(".zoom-btn");
      if (zoomBtn && state.map) {
        const reg = REGION_VIEWS[zoomBtn.dataset.region];
        if (reg) {
          document.querySelectorAll(".zoom-btn").forEach((b) => b.classList.toggle("active", b === zoomBtn));
          state.map.setView(reg.center, reg.zoom, { animate: true });
        }
        return;
      }

      const actEl = e.target.closest("[data-action]");
      if (actEl) {
        const action = actEl.dataset.action;
        const id = actEl.dataset.id;
        if (action === "toggle-fav") {
          e.stopPropagation();
          if (state.favorites.includes(id)) {
            state.favorites = state.favorites.filter((x) => x !== id);
          } else {
            state.favorites.push(id);
          }
          saveFavorites();
          renderHotels();
          return;
        }
        if (action === "prev-photo") {
          e.stopPropagation();
          stepCardPhoto(id, -1);
          return;
        }
        if (action === "next-photo") {
          e.stopPropagation();
          stepCardPhoto(id, 1);
          return;
        }
        if (action === "set-gcat") {
          state.cardGalleryCat[id] = actEl.dataset.cat;
          state.cardPhotoIdx[id] = 0;
          renderHotels();
          return;
        }
        if (action === "set-dtab") {
          state.cardDetailTab[id] = actEl.dataset.dtab;
          renderHotels();
          return;
        }
        if (action === "open-lightbox") {
          openLightbox(id);
          return;
        }
        if (action === "simulate-hotel") {
          state.sim.focusHotelId = id;
          switchTab("simulador");
          window.scrollTo({ top: 0, behavior: "smooth" });
          return;
        }
        if (action === "jump-hotel") {
          switchTab("hoteles");
          state.filter = "all";
          document.querySelectorAll("#filter-chips .chip").forEach((c) => c.classList.toggle("active", c.dataset.filter === "all"));
          renderHotels();
          const card = document.querySelector(`.hotel-card[data-hotel-id="${id}"]`);
          if (card) card.scrollIntoView({ behavior: "smooth", block: "start" });
          return;
        }
      }

      const lbCat = e.target.closest("[data-lb-cat]");
      if (lbCat) {
        state.lightbox.cat = lbCat.dataset.lbCat;
        state.lightbox.idx = 0;
        renderLightbox();
        return;
      }

      const lbThumb = e.target.closest("[data-lb-idx]");
      if (lbThumb) {
        state.lightbox.idx = parseInt(lbThumb.dataset.lbIdx, 10) || 0;
        renderLightbox();
        return;
      }

      const seasonBtn = e.target.closest("#sim-season .seg-btn");
      if (seasonBtn) {
        state.sim.season = seasonBtn.dataset.season;
        document.querySelectorAll("#sim-season .seg-btn").forEach((b) => b.classList.toggle("active", b === seasonBtn));
        renderSimulator();
        return;
      }

      const nightBtn = e.target.closest("#sim-nights .seg-btn");
      if (nightBtn) {
        state.sim.nights = parseInt(nightBtn.dataset.nights, 10) || 7;
        document.querySelectorAll("#sim-nights .seg-btn").forEach((b) => b.classList.toggle("active", b === nightBtn));
        renderSimulator();
      }
    });

    document.getElementById("sort-select").addEventListener("change", (e) => {
      state.sort = e.target.value;
      renderHotels();
    });

    document.getElementById("sim-discounts").addEventListener("change", (e) => {
      state.sim.discounts = e.target.checked;
      renderSimulator();
    });
    document.getElementById("sim-extras").addEventListener("change", (e) => {
      state.sim.extras = e.target.checked;
      renderSimulator();
    });
    document.getElementById("sim-flights").addEventListener("input", (e) => {
      state.sim.flightsPerPax = parseInt(e.target.value, 10) || 0;
      renderSimulator();
    });
    document.getElementById("sim-budget").addEventListener("input", (e) => {
      state.sim.budget = parseInt(e.target.value, 10) || 10000000;
      renderSimulator();
    });

    // Lightbox controls + touch swipe
    const closeLb = () => document.getElementById("lightbox-modal").classList.add("hidden");
    document.getElementById("lb-close").addEventListener("click", closeLb);
    document.getElementById("lb-close-backdrop").addEventListener("click", closeLb);
    document.getElementById("lb-prev").addEventListener("click", () => {
      const h = DATA.hotels.find((x) => x.id === state.lightbox.hotelId);
      if (!h) return;
      const len = getFilteredPhotos(h, state.lightbox.cat).length;
      if (len) { state.lightbox.idx = (state.lightbox.idx - 1 + len) % len; renderLightbox(); }
    });
    document.getElementById("lb-next").addEventListener("click", () => {
      const h = DATA.hotels.find((x) => x.id === state.lightbox.hotelId);
      if (!h) return;
      const len = getFilteredPhotos(h, state.lightbox.cat).length;
      if (len) { state.lightbox.idx = (state.lightbox.idx + 1) % len; renderLightbox(); }
    });

    let lbStartX = 0;
    const lbStage = document.getElementById("lb-stage");
    lbStage.addEventListener("touchstart", (e) => { if (e.touches[0]) lbStartX = e.touches[0].clientX; }, { passive: true });
    lbStage.addEventListener("touchend", (e) => {
      if (!e.changedTouches[0]) return;
      const dx = e.changedTouches[0].clientX - lbStartX;
      if (Math.abs(dx) > 40) {
        document.getElementById(dx < 0 ? "lb-next" : "lb-prev").click();
      }
    }, { passive: true });

    // Share modal controls
    document.getElementById("btn-open-share").addEventListener("click", openShareModal);
    document.getElementById("btn-share-inline").addEventListener("click", openShareModal);
    document.getElementById("btn-wa-inline").addEventListener("click", () => {
      window.open("https://wa.me/?text=" + encodeURIComponent(buildWhatsAppText()), "_blank", "noopener,noreferrer");
    });
    document.getElementById("btn-jump-discounts").addEventListener("click", () => switchTab("decision"));
    document.getElementById("btn-clear-favs").addEventListener("click", () => {
      state.favorites = [];
      saveFavorites();
      renderHotels();
      renderDecisionTab();
    });

    const closeShare = () => document.getElementById("share-modal").classList.add("hidden");
    document.getElementById("share-close").addEventListener("click", closeShare);
    document.getElementById("share-close-backdrop").addEventListener("click", closeShare);
    document.getElementById("btn-copy-url").addEventListener("click", () => {
      navigator.clipboard?.writeText(getShareLanUrl()).catch(() => {});
      const btn = document.getElementById("btn-copy-url");
      btn.textContent = "¡Copiado!";
      setTimeout(() => { btn.textContent = "Copiar"; }, 1600);
    });
    document.getElementById("btn-copy-wa").addEventListener("click", () => {
      navigator.clipboard?.writeText(document.getElementById("wa-message-preview").value).catch(() => {});
      const btn = document.getElementById("btn-copy-wa");
      btn.textContent = "✅ Texto copiado";
      setTimeout(() => { btn.textContent = "📋 Copiar texto"; }, 1600);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeLb();
        closeShare();
      }
    });
  }

  // Init
  renderHotels();
  renderSimulator();
  renderDecisionTab();
  bindEvents();
})();
