/**
 * app.js — TaxisDrive frontend logic
 * Handles navigation, API calls, map simulation, and UI rendering.
 * Variables/labels are in Spanish; code/logic remains in English.
 */

'use strict';

/* ═══════════════════════════════════════════════════
   CONSTANTS & STATE
═══════════════════════════════════════════════════ */

const API_BASE = '';  // same-origin Flask server

// Approximate map bounds for Pasto city (normalized to SVG 800x520)
const MAP_BOUNDS = {
  latMin: 1.190,  latMax: 1.250,
  lonMin: -77.310, lonMax: -77.260,
};

// Sector positions on SVG for labels
const SECTOR_POSITIONS = {
  'Centro':              { x: 49, y: 50 },
  'Lorenzo':             { x: 62, y: 30 },
  'Torobajo':            { x: 25, y: 65 },
  'Chambú':              { x: 73, y: 22 },
  'Corazón de Jesús':    { x: 30, y: 78 },
  'San Ignacio':         { x: 44, y: 38 },
  'Aranda':              { x: 80, y: 42 },
  'La Minga':            { x: 20, y: 85 },
  'Jamondino':           { x: 18, y: 58 },
  'Riveras de Mijitayo': { x: 85, y: 30 },
};

let currentFilter = 'all';
let fleetData = [];
let ordersData = [];
let pollingInterval = null;

/* ═══════════════════════════════════════════════════
   NAVIGATION
═══════════════════════════════════════════════════ */

function initNavigation() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const viewId = btn.dataset.view;
      activateView(viewId);
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
}

function activateView(viewId) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  const target = document.getElementById(`view-${viewId}`);
  if (target) {
    target.classList.add('active');
    if (viewId === 'mapa')     loadMapView();
    if (viewId === 'pedidos')  loadOrdersView();
    if (viewId === 'flota')    loadFleetView();
    if (viewId === 'solicitar') loadSolicitar();
  }
}

/* ═══════════════════════════════════════════════════
   API HELPERS
═══════════════════════════════════════════════════ */

async function fetchJSON(url, options = {}) {
  try {
    const response = await fetch(API_BASE + url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    return await response.json();
  } catch (err) {
    console.error('API error:', url, err);
    return null;
  }
}

async function loadFleetData() {
  const data = await fetchJSON('/api/fleet');
  if (data) {
    fleetData = data.vehicles;
    updateHeaderStats(data.stats);
  }
}

async function loadOrdersData() {
  const data = await fetchJSON('/api/orders');
  if (data) ordersData = data.orders;
}

/* ═══════════════════════════════════════════════════
   HEADER STATS
═══════════════════════════════════════════════════ */

function updateHeaderStats(stats) {
  document.getElementById('count-disponibles').textContent = stats.available || 0;
  document.getElementById('count-en-camino').textContent   = stats.en_route  || 0;
}

/* ═══════════════════════════════════════════════════
   MAP VIEW
═══════════════════════════════════════════════════ */

function latLonToPercent(lat, lon) {
  const xPct = ((lon - MAP_BOUNDS.lonMin) / (MAP_BOUNDS.lonMax - MAP_BOUNDS.lonMin)) * 100;
  const yPct = (1 - (lat - MAP_BOUNDS.latMin) / (MAP_BOUNDS.latMax - MAP_BOUNDS.latMin)) * 100;
  return {
    x: Math.min(Math.max(xPct, 2), 98),
    y: Math.min(Math.max(yPct, 2), 98),
  };
}

function renderSectorLabels() {
  const container = document.getElementById('sector-labels');
  if (!container) return;
  container.innerHTML = '';
  Object.entries(SECTOR_POSITIONS).forEach(([sector, pos]) => {
    const el = document.createElement('div');
    el.className = 'sector-label';
    el.textContent = sector;
    el.style.left = pos.x + '%';
    el.style.top  = pos.y + '%';
    container.appendChild(el);
  });
}

function renderVehicles() {
  const container = document.getElementById('vehicles-overlay');
  if (!container) return;
  container.innerHTML = '';

  fleetData.forEach(v => {
    const pos = latLonToPercent(v.latitude, v.longitude);
    const dot = document.createElement('div');
    dot.className = `vehicle-dot ${v.status}`;
    dot.style.left = pos.x + '%';
    dot.style.top  = pos.y + '%';

    const statusLabel = {
      disponible: 'Disponible',
      en_camino:  'En camino',
      ocupado:    'Ocupado',
    }[v.status] || v.status;

    dot.innerHTML = `
      <div class="vehicle-dot__inner">🚖</div>
      <div class="vehicle-tooltip">
        <strong>${v.driver_name}</strong>
        Placa: ${v.plate}<br/>
        Sector: ${v.sector}<br/>
        Estado: ${statusLabel}
      </div>
    `;
    container.appendChild(dot);
  });
}

async function loadMapView() {
  await loadFleetData();
  renderSectorLabels();
  renderVehicles();
}

/* ═══════════════════════════════════════════════════
   SOLICITAR VIEW
═══════════════════════════════════════════════════ */

async function loadSolicitar() {
  const data = await fetchJSON('/api/sectors');
  if (!data) return;

  const select = document.getElementById('inp-barrio');
  select.innerHTML = '<option value="">-- Selecciona tu barrio --</option>';

  Object.entries(data.neighborhoods).forEach(([sector, neighborhoods]) => {
    const group = document.createElement('optgroup');
    group.label = `📍 ${sector}`;
    neighborhoods.forEach(nb => {
      const opt = document.createElement('option');
      opt.value = nb;
      opt.textContent = nb;
      group.appendChild(opt);
    });
    select.appendChild(group);
  });
}

function bindSolicitarForm() {
  const btn = document.getElementById('btn-solicitar');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const nombre     = document.getElementById('inp-nombre').value.trim();
    const barrio     = document.getElementById('inp-barrio').value.trim();
    const direccion  = document.getElementById('inp-direccion').value.trim();
    const destino    = document.getElementById('inp-destino').value.trim();

    if (!nombre || !barrio || !direccion || !destino) {
      showToast('⚠️ Por favor completa todos los campos.');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="btn-icon">⏳</span> Buscando...';

    const result = await fetchJSON('/api/orders', {
      method: 'POST',
      body: JSON.stringify({
        user_name: nombre,
        neighborhood: barrio,
        address: direccion,
        destination: destino,
      }),
    });

    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">🔍</span> Buscar vehículo cercano';

    if (!result || result.error) {
      showToast('❌ ' + (result?.error || 'Error al procesar la solicitud'));
      return;
    }

    showOrderResult(result);
    showToast('✅ Solicitud creada exitosamente');
  });
}

function showOrderResult(result) {
  const card = document.getElementById('result-card');
  const title = document.getElementById('result-title');
  const msg   = document.getElementById('result-msg');
  const details = document.getElementById('result-details');

  card.classList.remove('hidden', 'error');

  if (result.vehicle) {
    title.textContent = '🚖 Vehículo asignado';
    msg.textContent   = result.message;
    card.style.borderColor = 'var(--green)';
    details.innerHTML = `
      <div class="detail-item"><label>Conductor</label><span>${result.vehicle.driver_name}</span></div>
      <div class="detail-item"><label>Placa</label><span>${result.vehicle.plate}</span></div>
      <div class="detail-item"><label>Sector</label><span>${result.vehicle.sector}</span></div>
      <div class="detail-item"><label>Llegada estimada</label><span>${result.estimated_time} min</span></div>
      <div class="detail-item"><label>N° Pedido</label><span>#${result.order_id}</span></div>
      <div class="detail-item"><label>Barrio</label><span>${result.neighborhood}</span></div>
    `;
  } else {
    card.classList.add('error');
    title.textContent = '⚠️ Sin vehículos disponibles';
    msg.textContent   = result.message;
    card.style.borderColor = 'var(--red)';
    details.innerHTML = `<div class="detail-item"><label>N° Pedido</label><span>#${result.order_id}</span></div>`;
  }
}

/* ═══════════════════════════════════════════════════
   ORDERS VIEW
═══════════════════════════════════════════════════ */

async function loadOrdersView() {
  await loadOrdersData();
  renderOrders();
}

function renderOrders() {
  const container = document.getElementById('orders-list');
  if (!container) return;

  let filtered = ordersData;
  if (currentFilter !== 'all') {
    filtered = ordersData.filter(o => o.status === currentFilter);
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <span>📋</span>
        <p>No hay pedidos${currentFilter !== 'all' ? ' con este estado' : ' aún'}.<br/>
           ${currentFilter === 'all' ? 'Crea una solicitud para comenzar.' : ''}</p>
      </div>`;
    return;
  }

  container.innerHTML = filtered.map(order => buildOrderCard(order)).join('');

  // Bind action buttons
  container.querySelectorAll('.btn-complete').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = parseInt(btn.dataset.id);
      await fetchJSON(`/api/orders/${id}/complete`, { method: 'PUT' });
      showToast('✅ Pedido completado');
      await loadOrdersView();
      await loadFleetData();
    });
  });

  container.querySelectorAll('.btn-cancel').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = parseInt(btn.dataset.id);
      await fetchJSON(`/api/orders/${id}/cancel`, { method: 'PUT' });
      showToast('🚫 Pedido cancelado');
      await loadOrdersView();
      await loadFleetData();
    });
  });
}

function buildOrderCard(order) {
  const badgeClass = `badge-${order.status}`;
  const statusLabel = {
    pendiente:  'Pendiente',
    asignado:   'Asignado',
    completado: 'Completado',
    cancelado:  'Cancelado',
  }[order.status] || order.status;

  const isActive = order.status === 'asignado' || order.status === 'pendiente';
  const actions = isActive ? `
    <div class="order-actions">
      <button class="btn-action btn-complete" data-id="${order.order_id}">✓</button>
      <button class="btn-action btn-cancel"   data-id="${order.order_id}">✕</button>
    </div>` : '';

  const vehicleInfo = order.assigned_vehicle_id
    ? `Vehículo #${order.assigned_vehicle_id} · ${order.estimated_time || '?'} min`
    : 'Sin vehículo asignado';

  return `
    <div class="order-card">
      <div class="order-num">#${order.order_id}</div>
      <div class="order-info">
        <h4>${order.user_name} → ${order.destination}</h4>
        <p>${order.neighborhood} · ${order.address} · ${vehicleInfo} · ${order.created_at}</p>
      </div>
      <span class="order-badge ${badgeClass}">${statusLabel}</span>
      ${actions}
    </div>`;
}

function bindOrderFilters() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      currentFilter = btn.dataset.filter;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderOrders();
    });
  });

  const refreshBtn = document.getElementById('btn-refresh-orders');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => loadOrdersView());
  }
}

/* ═══════════════════════════════════════════════════
   FLEET VIEW
═══════════════════════════════════════════════════ */

async function loadFleetView() {
  await loadFleetData();
  renderFleet();
}

function renderFleet() {
  const grid  = document.getElementById('fleet-grid');
  const stats = document.getElementById('fleet-stats-bar');
  if (!grid) return;

  // Stats
  const s = { total: 0, available: 0, en_route: 0, busy: 0 };
  fleetData.forEach(v => {
    s.total++;
    if (v.status === 'disponible') s.available++;
    else if (v.status === 'en_camino') s.en_route++;
    else if (v.status === 'ocupado') s.busy++;
  });
  document.getElementById('fs-total').textContent  = s.total;
  document.getElementById('fs-avail').textContent  = s.available;
  document.getElementById('fs-route').textContent  = s.en_route;
  document.getElementById('fs-busy').textContent   = s.busy;

  // Cards
  grid.innerHTML = fleetData.map(v => {
    const statusLabel = {
      disponible: 'Disponible',
      en_camino:  'En camino',
      ocupado:    'Ocupado',
    }[v.status] || v.status;

    return `
      <div class="vehicle-card status-${v.status}">
        <div class="vc-header">
          <span class="vc-icon">🚖</span>
          <span class="vc-status ${v.status}">${statusLabel}</span>
        </div>
        <div class="vc-name">${v.driver_name}</div>
        <div class="vc-plate">${v.plate}</div>
        <div class="vc-sector">📍 ${v.sector}</div>
      </div>`;
  }).join('');
}

/* ═══════════════════════════════════════════════════
   TOAST NOTIFICATION
═══════════════════════════════════════════════════ */

let toastTimeout = null;

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.remove('hidden');
  if (toastTimeout) clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.add('hidden'), 3500);
}

/* ═══════════════════════════════════════════════════
   POLLING — keep map live
═══════════════════════════════════════════════════ */

function startPolling() {
  pollingInterval = setInterval(async () => {
    await loadFleetData();
    const activeView = document.querySelector('.view.active');
    if (activeView?.id === 'view-mapa') renderVehicles();
  }, 4000);
}

/* ═══════════════════════════════════════════════════
   BOOTSTRAP
═══════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', async () => {
  initNavigation();
  bindSolicitarForm();
  bindOrderFilters();

  // Load initial view
  await loadMapView();
  startPolling();
});
