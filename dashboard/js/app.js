/**
 * AgriSense AI — Dashboard Application Logic
 * =============================================
 * Tab navigation, dynamic content rendering, alerts, and interactivity.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDateTime();
    renderOverviewAlerts();
    renderSoilRecommendations();
    renderIrrigationSchedule();
    renderCropRecommendations();
    renderFullAlerts();
    initAllCharts();
});

// ── Navigation ──────────────────────────────────────────────────

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tab = item.dataset.tab;
            switchTab(tab);

            // Mobile: close sidebar
            sidebar.classList.remove('open');
        });
    });

    // View all links
    document.querySelectorAll('.view-all').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(link.dataset.tab);
        });
    });

    // Mobile menu toggle
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
}

function switchTab(tabName) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.tab === tabName);
    });

    // Update content
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.toggle('active', tab.id === `tab-${tabName}`);
    });

    // Update breadcrumb
    const labels = {
        overview: 'Overview',
        soil: 'Soil Health',
        water: 'Water Quality',
        irrigation: 'Irrigation',
        crops: 'Crop Advisor',
        alerts: 'Alerts & Notifications',
    };
    document.getElementById('current-page').textContent = labels[tabName] || tabName;

    // Resize charts for newly visible tab
    setTimeout(() => {
        Object.values(charts).forEach(chart => {
            if (chart && chart.resize) chart.resize();
        });
    }, 100);
}

// ── Date & Time ─────────────────────────────────────────────────

function initDateTime() {
    const dateEl = document.getElementById('date-display');
    const updateDate = () => {
        const now = new Date();
        dateEl.textContent = now.toLocaleDateString('en-US', {
            weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
        });
    };
    updateDate();
    setInterval(updateDate, 60000);

    // Weather from data
    const w = AgriData.weather.current;
    document.getElementById('weather-temp').textContent = `${w.temp}°C`;
}

// ── Alerts Rendering ────────────────────────────────────────────

function renderOverviewAlerts() {
    const container = document.getElementById('overview-alerts');
    const alerts = AgriData.alerts.slice(0, 4);

    container.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.type}">
            <span class="alert-icon">${alert.icon}</span>
            <div class="alert-text">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-desc">${alert.desc}</div>
            </div>
            <span class="alert-time">${alert.time}</span>
        </div>
    `).join('');
}

function renderFullAlerts() {
    const container = document.getElementById('alerts-full');
    renderAlertsList(container, AgriData.alerts);

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            const filtered = filter === 'all'
                ? AgriData.alerts
                : AgriData.alerts.filter(a => a.type === filter);
            renderAlertsList(container, filtered);
        });
    });
}

function renderAlertsList(container, alerts) {
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.type}">
            <span class="alert-icon">${alert.icon}</span>
            <div class="alert-text">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-desc">${alert.desc}</div>
            </div>
            <span class="alert-time">${alert.time}</span>
        </div>
    `).join('');
}

// ── Soil Recommendations ────────────────────────────────────────

function renderSoilRecommendations() {
    const container = document.getElementById('soil-recommendations');
    const recs = AgriData.nutrientDeficiency.recommendations;

    container.innerHTML = recs.map(rec => `
        <div class="rec-card ${rec.type}">
            <div class="rec-title">${rec.nutrient} — ${rec.zone}</div>
            <div class="rec-desc">${rec.message}</div>
        </div>
    `).join('');
}

// ── Irrigation Schedule ─────────────────────────────────────────

function renderIrrigationSchedule() {
    const container = document.querySelector('.schedule-grid');
    const schedule = AgriData.irrigation.zoneSchedule;

    container.innerHTML = Object.entries(schedule).map(([zone, data]) => `
        <div class="schedule-card ${data.priority.toLowerCase()}">
            <div class="schedule-zone">${zone.replace('_', ' ')}</div>
            <div class="schedule-crop">${data.crop}</div>
            <div class="schedule-need">${data.avg_need_mm}mm</div>
            <div class="schedule-freq">📅 ${data.recommended_frequency}</div>
            <div class="schedule-freq">💧 Moisture: ${data.avg_moisture}%</div>
            <span class="schedule-priority priority-${data.priority.toLowerCase()}">${data.priority} Priority</span>
        </div>
    `).join('');
}

// ── Crop Recommendations ────────────────────────────────────────

function renderCropRecommendations() {
    const container = document.getElementById('crop-recommendations');
    const recs = AgriData.cropIntelligence.zoneCropRecommendations;
    const yields = AgriData.cropIntelligence.zoneYields;

    container.innerHTML = Object.entries(recs).map(([zone, crops]) => {
        const topCrop = crops[0];
        const yieldData = yields[zone] || {};

        return `
            <div class="crop-card">
                <div class="crop-zone">${zone.replace('_', ' ')} · ${yieldData.crop || ''}</div>
                <div class="crop-name">${topCrop.crop}</div>
                <div class="crop-confidence">
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${topCrop.confidence}%"></div>
                    </div>
                    <span class="confidence-val">${topCrop.confidence}%</span>
                </div>
                <div class="crop-meta">
                    <span>Expected Yield <strong>${topCrop.yield} t/ha</strong></span>
                    <span>Efficiency <strong>${yieldData.yield_efficiency || 0}%</strong></span>
                    <span>Health Score <strong>${yieldData.health_score || 0}/100</strong></span>
                </div>
            </div>
        `;
    }).join('');
}
