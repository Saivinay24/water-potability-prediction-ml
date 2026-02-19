/**
 * AgriSense AI — Chart Configurations
 * ====================================
 * Chart.js chart setup and rendering for all dashboard tabs.
 */

// ── Global Chart.js Defaults ────────────────────────────────────
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyleWidth = 8;
Chart.defaults.plugins.legend.labels.padding = 16;

const CHART_COLORS = {
    green: '#10b981',
    blue: '#3b82f6',
    amber: '#f59e0b',
    purple: '#8b5cf6',
    red: '#ef4444',
    cyan: '#06b6d4',
    pink: '#ec4899',
    indigo: '#6366f1',
    greenAlpha: 'rgba(16,185,129,0.15)',
    blueAlpha: 'rgba(59,130,246,0.15)',
    amberAlpha: 'rgba(245,158,11,0.15)',
    purpleAlpha: 'rgba(139,92,246,0.15)',
    redAlpha: 'rgba(239,68,68,0.15)',
};

const charts = {};

// ── Overview Charts ─────────────────────────────────────────────

function initZoneHealthChart() {
    const zones = AgriData.soilHealth.zones;
    const ctx = document.getElementById('chart-zone-health');
    if (!ctx) return;

    charts.zoneHealth = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: zones.map(z => z.zone_id.replace('_', ' ')),
            datasets: [{
                label: 'Health Score',
                data: zones.map(z => z.predicted_score),
                backgroundColor: zones.map(z => {
                    if (z.predicted_score >= 80) return CHART_COLORS.green;
                    if (z.predicted_score >= 60) return CHART_COLORS.blue;
                    if (z.predicted_score >= 40) return CHART_COLORS.amber;
                    return CHART_COLORS.red;
                }),
                borderRadius: 6,
                borderSkipped: false,
                barPercentage: 0.6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        afterLabel: (ctx) => {
                            const zone = zones[ctx.dataIndex];
                            return `Category: ${zone.category}\nSoil: ${zone.soil_type}\nMoisture: ${zone.moisture_pct}%`;
                        }
                    }
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { callback: v => v + '/100' },
                },
                x: {
                    grid: { display: false },
                },
            },
        },
    });
}

function initDeficiencyChart() {
    const rates = AgriData.nutrientDeficiency.overallRates;
    const ctx = document.getElementById('chart-deficiency-dist');
    if (!ctx) return;

    charts.deficiency = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Nitrogen', 'Phosphorus', 'Potassium', 'pH Imbalance'],
            datasets: [{
                data: [rates.N_deficient, rates.P_deficient, rates.K_deficient, rates.pH_imbalanced],
                backgroundColor: [CHART_COLORS.green, CHART_COLORS.blue, CHART_COLORS.purple, CHART_COLORS.amber],
                borderWidth: 0,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.label}: ${ctx.parsed}% of zones affected`
                    }
                },
            },
        },
    });
}

// ── Soil Health Charts ──────────────────────────────────────────

function initNPKZonesChart() {
    const zones = AgriData.soilHealth.zones;
    const ctx = document.getElementById('chart-npk-zones');
    if (!ctx) return;

    charts.npkZones = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: zones.map(z => z.zone_id.replace('_', ' ')),
            datasets: [
                {
                    label: 'Nitrogen (mg/kg)',
                    data: zones.map(z => z.nitrogen_mg_kg),
                    backgroundColor: CHART_COLORS.greenAlpha,
                    borderColor: CHART_COLORS.green,
                    borderWidth: 1.5,
                    borderRadius: 4,
                },
                {
                    label: 'Phosphorus (mg/kg)',
                    data: zones.map(z => z.phosphorus_mg_kg),
                    backgroundColor: CHART_COLORS.blueAlpha,
                    borderColor: CHART_COLORS.blue,
                    borderWidth: 1.5,
                    borderRadius: 4,
                },
                {
                    label: 'Potassium (mg/kg)',
                    data: zones.map(z => z.potassium_mg_kg),
                    backgroundColor: CHART_COLORS.purpleAlpha,
                    borderColor: CHART_COLORS.purple,
                    borderWidth: 1.5,
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    title: { display: true, text: 'mg/kg' },
                },
                x: { grid: { display: false } },
            },
        },
    });
}

function initHealthDistChart() {
    const dist = AgriData.soilHealth.categoryDistribution;
    const ctx = document.getElementById('chart-health-dist');
    if (!ctx) return;

    charts.healthDist = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(dist),
            datasets: [{
                data: Object.values(dist),
                backgroundColor: [CHART_COLORS.green, CHART_COLORS.blue, CHART_COLORS.amber, CHART_COLORS.red],
                borderWidth: 0,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
            },
        },
    });
}

// ── Water Quality Charts ────────────────────────────────────────

function initWaterSourcesChart() {
    const sources = AgriData.waterQuality.sources;
    const ctx = document.getElementById('chart-water-sources');
    if (!ctx) return;

    const sourceNames = Object.keys(sources);
    const grades = ['A', 'B', 'C', 'D', 'F'];
    const gradeColors = {
        A: CHART_COLORS.green, B: CHART_COLORS.blue,
        C: CHART_COLORS.amber, D: CHART_COLORS.red, F: '#dc2626',
    };

    charts.waterSources = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sourceNames,
            datasets: grades.map(grade => ({
                label: `Grade ${grade}`,
                data: sourceNames.map(s => sources[s].gradeDistribution[grade] || 0),
                backgroundColor: gradeColors[grade] + '33',
                borderColor: gradeColors[grade],
                borderWidth: 1.5,
                borderRadius: 4,
            })),
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
                x: { stacked: true, grid: { display: false } },
                y: {
                    stacked: true,
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    title: { display: true, text: 'Samples' },
                },
            },
        },
    });
}

function initWaterGradesChart() {
    const grades = AgriData.waterQuality.overallGrades;
    const ctx = document.getElementById('chart-water-grades');
    if (!ctx) return;

    charts.waterGrades = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(grades).map(g => `Grade ${g}`),
            datasets: [{
                data: Object.values(grades),
                backgroundColor: [CHART_COLORS.green, CHART_COLORS.blue, CHART_COLORS.amber, CHART_COLORS.red, '#dc2626'],
                borderWidth: 0,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: { legend: { position: 'bottom' } },
        },
    });
}

// ── Irrigation Charts ───────────────────────────────────────────

function initIrrigationWeeklyChart() {
    const forecast = AgriData.irrigation.weeklyForecast;
    const ctx = document.getElementById('chart-irrigation-weekly');
    if (!ctx) return;

    charts.irrigationWeekly = new Chart(ctx, {
        type: 'line',
        data: {
            labels: forecast.map(f => f.week),
            datasets: [{
                label: 'Avg Irrigation Need (mm/day)',
                data: forecast.map(f => f.need),
                borderColor: CHART_COLORS.blue,
                backgroundColor: CHART_COLORS.blueAlpha,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 7,
                pointBackgroundColor: CHART_COLORS.blue,
                pointBorderColor: '#1a2233',
                pointBorderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.parsed.y} mm/day`
                    }
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    title: { display: true, text: 'mm/day' },
                },
                x: { grid: { display: false } },
            },
        },
    });
}

// ── Crop Intelligence Charts ────────────────────────────────────

function initYieldEfficiencyChart() {
    const yields = AgriData.cropIntelligence.zoneYields;
    const zones = Object.keys(yields);
    const ctx = document.getElementById('chart-yield-efficiency');
    if (!ctx) return;

    charts.yieldEfficiency = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: zones.map(z => z.replace('_', ' ')),
            datasets: [{
                label: 'Yield Efficiency (%)',
                data: zones.map(z => yields[z].yield_efficiency),
                backgroundColor: zones.map(z => {
                    const eff = yields[z].yield_efficiency;
                    if (eff >= 85) return CHART_COLORS.green;
                    if (eff >= 70) return CHART_COLORS.blue;
                    if (eff >= 55) return CHART_COLORS.amber;
                    return CHART_COLORS.red;
                }),
                borderRadius: 6,
                borderSkipped: false,
                barPercentage: 0.6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        afterLabel: (ctx) => {
                            const zone = zones[ctx.dataIndex];
                            const data = yields[zone];
                            return `Crop: ${data.crop}\nPredicted: ${data.predicted_yield} t/ha\nBaseline: ${data.expected_baseline} t/ha`;
                        }
                    }
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { callback: v => v + '%' },
                },
                x: { grid: { display: false } },
            },
        },
    });
}

function initCropDistChart() {
    const crops = AgriData.cropIntelligence.topCrops;
    const ctx = document.getElementById('chart-crop-dist');
    if (!ctx) return;

    const colors = [CHART_COLORS.green, CHART_COLORS.blue, CHART_COLORS.amber, CHART_COLORS.purple,
    CHART_COLORS.cyan, CHART_COLORS.pink, CHART_COLORS.indigo, CHART_COLORS.red];

    charts.cropDist = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(crops),
            datasets: [{
                data: Object.values(crops),
                backgroundColor: colors,
                borderWidth: 0,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: { legend: { position: 'right', labels: { font: { size: 10 } } } },
        },
    });
}

// ── Initialize All Charts ───────────────────────────────────────

function initAllCharts() {
    initZoneHealthChart();
    initDeficiencyChart();
    initNPKZonesChart();
    initHealthDistChart();
    initWaterSourcesChart();
    initWaterGradesChart();
    initIrrigationWeeklyChart();
    initYieldEfficiencyChart();
    initCropDistChart();
}
