/**
 * House Price Prediction System - Analytics & Metrics Dashboard Controller
 * Powered by Chart.js for interactive visualizations of model evaluation
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardMetrics();
    loadDatasetPreview();
});

let actualVsPredChart = null;
let featureImportanceChart = null;
let residualChart = null;

async function loadDashboardMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const metrics = await response.json();

        if (!metrics || !metrics.test_samples) return;

        renderActualVsPredictedChart(metrics.test_samples);
        renderFeatureImportanceChart(metrics.feature_importance);
        renderResidualDistributionChart(metrics.test_samples);

    } catch (err) {
        console.error('Error loading metrics data:', err);
    }
}

// Chart 1: Actual vs. Predicted House Prices
function renderActualVsPredictedChart(testSamples) {
    const ctx = document.getElementById('actualVsPredChart');
    if (!ctx) return;

    const labels = testSamples.map(s => `#${s.index}`);
    const actualData = testSamples.map(s => s.actual / 100000); // In Lakhs
    const predictedData = testSamples.map(s => s.predicted / 100000);

    if (actualVsPredChart) actualVsPredChart.destroy();

    actualVsPredChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Price (₹ Lakhs)',
                    data: actualData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: false
                },
                {
                    label: 'Predicted Price (₹ Lakhs)',
                    data: predictedData,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ₹${context.raw.toFixed(2)} Lakhs`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#64748b',
                        callback: function(value) { return '₹' + value + 'L'; }
                    }
                }
            }
        }
    });
}

// Chart 2: Feature Importance (Horizontal Bar Chart)
function renderFeatureImportanceChart(featureImportance) {
    const ctx = document.getElementById('featureImportanceChart');
    if (!ctx) return;

    // Take top 8 most influential features
    const entries = Object.entries(featureImportance).slice(0, 8);
    const labels = entries.map(([key]) => formatFeatureName(key));
    const values = entries.map(([, val]) => val);

    if (featureImportanceChart) featureImportanceChart.destroy();

    featureImportanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Relative Importance (%)',
                data: values,
                backgroundColor: [
                    '#6366f1', '#818cf8', '#a5b4fc', '#10b981',
                    '#34d399', '#f59e0b', '#fbbf24', '#ec4899'
                ],
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) { return `Impact: ${context.raw}%`; }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#64748b',
                        callback: function(value) { return value + '%'; }
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } }
                }
            }
        }
    });
}

// Chart 3: Residual / Prediction Error Distribution
function renderResidualDistributionChart(testSamples) {
    const ctx = document.getElementById('residualChart');
    if (!ctx) return;

    // Group errors into buckets in Lakhs
    const errors = testSamples.map(s => (s.error / 100000));
    
    // Sort errors
    const labels = testSamples.slice(0, 30).map(s => `#${s.index}`);
    const dataVals = errors.slice(0, 30);

    if (residualChart) residualChart.destroy();

    residualChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Residual Error (₹ Lakhs)',
                data: dataVals,
                backgroundColor: dataVals.map(val => val >= 0 ? 'rgba(99, 102, 241, 0.7)' : 'rgba(239, 68, 68, 0.7)'),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw;
                            return `Residual: ${val >= 0 ? '+' : ''}₹${val.toFixed(2)} Lakhs`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#64748b',
                        callback: function(value) { return '₹' + value + 'L'; }
                    }
                }
            }
        }
    });
}

// Helper to format raw feature names for readable UI
function formatFeatureName(rawName) {
    const map = {
        'bathrooms': 'Bathrooms Count',
        'area': 'Plot / Carpet Area',
        'stories': 'Building Stories',
        'airconditioning': 'Air Conditioning',
        'amenity_score': 'Total Amenity Score',
        'bath_bed_ratio': 'Bath-to-Bed Ratio',
        'bedrooms': 'Bedrooms Count',
        'furnishingstatus_code': 'Furnishing Status',
        'total_rooms': 'Total Rooms',
        'parking': 'Parking Capacity',
        'loc_Riverside Bay': 'Loc: Riverside Bay',
        'loc_Downtown Central': 'Loc: Downtown Central',
        'loc_West Greens': 'Loc: West Greens',
        'prefarea': 'Prime Locality Flag'
    };
    return map[rawName] || rawName.replace('loc_', 'Location: ').replace('_', ' ');
}

// Dataset Explorer Table
let allDatasetRecords = [];

async function loadDatasetPreview() {
    const tableBody = document.getElementById('datasetTableBody');
    if (!tableBody) return;

    try {
        const response = await fetch('/api/dataset?limit=30');
        const res = await response.json();

        if (!res.success || !res.data) return;
        allDatasetRecords = res.data;
        renderTableRows(allDatasetRecords);

        // Search input binding
        const searchInput = document.getElementById('datasetSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                const filtered = allDatasetRecords.filter(r => 
                    r.location.toLowerCase().includes(term) ||
                    r.furnishingstatus.toLowerCase().includes(term) ||
                    String(r.price).includes(term) ||
                    String(r.area).includes(term)
                );
                renderTableRows(filtered);
            });
        }

    } catch (err) {
        console.error('Failed to load dataset:', err);
    }
}

function renderTableRows(records) {
    const tableBody = document.getElementById('datasetTableBody');
    if (!tableBody) return;

    if (records.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No matching records found</td></tr>`;
        return;
    }

    tableBody.innerHTML = records.map((row, idx) => `
        <tr>
            <td><strong>#${idx + 1}</strong></td>
            <td><strong class="text-white">₹${(row.price / 100000).toFixed(2)} L</strong></td>
            <td>${Number(row.area).toLocaleString()} sq ft</td>
            <td><span class="badge-tag badge-runner">${row.location}</span></td>
            <td>${row.bedrooms} BHK / ${row.bathrooms} Bath</td>
            <td>${row.stories} Floors (${row.parking} Park)</td>
            <td><span class="text-capitalize">${row.furnishingstatus}</span></td>
        </tr>
    `).join('');
}
