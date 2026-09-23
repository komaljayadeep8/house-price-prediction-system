/**
 * UrbanValuate - Valuation Studio Controller
 * Handles synchronized sliders, area steppers, URL query params, presets,
 * and renders the certified valuation dossier and growth chart with 5-theme adaptability.
 */

let growthChartInstance = null;
let currentProjections = null;
let currentBasePrice = null;

document.addEventListener('DOMContentLoaded', () => {
    initAreaControls();
    initUrlParams();
    initPresetCards();
    initPredictionForm();

    // Auto-evaluate default preset on page load for immediate visual impact
    setTimeout(() => {
        submitPrediction();
    }, 150);

    // Re-render chart on theme transformation
    window.addEventListener('themeChanged', () => {
        if (currentProjections && currentBasePrice) {
            renderGrowthForecastChart(currentProjections, currentBasePrice);
        }
    });
});

// Area Steppers & Range Slider Synchronization
function initAreaControls() {
    const areaRange = document.getElementById('areaRange');
    const areaInput = document.getElementById('areaInput');
    const areaDisplay = document.getElementById('areaDisplay');
    const btnMinus = document.getElementById('btnMinusArea');
    const btnPlus = document.getElementById('btnPlusArea');

    if (!areaRange || !areaInput) return;

    function setArea(val) {
        val = Math.max(500, Math.min(18000, Number(val)));
        areaRange.value = val;
        areaInput.value = val;
        if (areaDisplay) areaDisplay.textContent = `${val.toLocaleString()} sq ft`;
    }

    areaRange.addEventListener('input', (e) => setArea(e.target.value));
    areaInput.addEventListener('change', (e) => setArea(e.target.value));

    if (btnMinus) {
        btnMinus.addEventListener('click', () => setArea(Number(areaInput.value) - 500));
    }
    if (btnPlus) {
        btnPlus.addEventListener('click', () => setArea(Number(areaInput.value) + 500));
    }
}

// Read URL Parameters from Home Quick Bar (e.g. ?location=...&area=...)
function initUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const locParam = urlParams.get('location');
    const areaParam = urlParams.get('area');

    if (locParam) {
        const select = document.getElementById('locationSelect');
        if (select) select.value = locParam;
    }
    if (areaParam) {
        const areaInput = document.getElementById('areaInput');
        const areaRange = document.getElementById('areaRange');
        const areaDisplay = document.getElementById('areaDisplay');
        const val = Number(areaParam);
        if (areaInput) areaInput.value = val;
        if (areaRange) areaRange.value = val;
        if (areaDisplay) areaDisplay.textContent = `${val.toLocaleString()} sq ft`;
    }
}

// Preset Property Cards
function initPresetCards() {
    const cards = document.querySelectorAll('.preset-card');
    if (!cards.length) return;

    const sampleData = {
        'luxury': {
            area: 7420,
            bedrooms: 4,
            bathrooms: 3,
            stories: 3,
            parking: 2,
            location: 'Tech Park Cyber City',
            furnishing: 'furnished',
            mainroad: true,
            guestroom: true,
            basement: false,
            hotwaterheating: false,
            airconditioning: true
        },
        'suburban': {
            area: 3600,
            bedrooms: 3,
            bathrooms: 1,
            stories: 2,
            parking: 1,
            location: 'Suburban North',
            furnishing: 'semi-furnished',
            mainroad: true,
            guestroom: false,
            basement: true,
            hotwaterheating: false,
            airconditioning: false
        },
        'penthouse': {
            area: 8960,
            bedrooms: 4,
            bathrooms: 4,
            stories: 4,
            parking: 3,
            location: 'Downtown Central',
            furnishing: 'furnished',
            mainroad: true,
            guestroom: true,
            basement: true,
            hotwaterheating: true,
            airconditioning: true
        }
    };

    cards.forEach(card => {
        card.addEventListener('click', () => {
            cards.forEach(c => {
                c.classList.remove('active');
                const check = c.querySelector('.bi-check-circle-fill');
                if (check) check.style.color = 'var(--text-dim)';
            });
            card.classList.add('active');
            const check = card.querySelector('.bi-check-circle-fill');
            if (check) check.style.color = 'var(--gold)';

            const key = card.getAttribute('data-preset');
            const data = sampleData[key];
            if (!data) return;

            // Update inputs
            const areaInput = document.getElementById('areaInput');
            const areaRange = document.getElementById('areaRange');
            const areaDisplay = document.getElementById('areaDisplay');

            if (areaInput) areaInput.value = data.area;
            if (areaRange) areaRange.value = data.area;
            if (areaDisplay) areaDisplay.textContent = `${data.area.toLocaleString()} sq ft`;

            const locSelect = document.getElementById('locationSelect');
            if (locSelect) locSelect.value = data.location;

            setRadioValue('bedrooms', data.bedrooms);
            setRadioValue('bathrooms', data.bathrooms);
            setRadioValue('stories', data.stories);
            setRadioValue('parking', data.parking);
            setRadioValue('furnishingstatus', data.furnishing);

            document.getElementById('mainroadCheck').checked = data.mainroad;
            document.getElementById('guestroomCheck').checked = data.guestroom;
            document.getElementById('basementCheck').checked = data.basement;
            document.getElementById('hotwaterheatingCheck').checked = data.hotwaterheating;
            document.getElementById('airconditioningCheck').checked = data.airconditioning;

            showToast(`Loaded ${card.querySelector('.preset-name')?.textContent || 'Preset'}!`, 'gold');
            submitPrediction();
        });
    });
}

function setRadioValue(name, value) {
    const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
    if (radio) radio.checked = true;
}

function getCheckedRadioValue(name, defaultValue) {
    const checked = document.querySelector(`input[name="${name}"]:checked`);
    return checked ? checked.value : defaultValue;
}

// Form Submission
function initPredictionForm() {
    const form = document.getElementById('predictionForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        submitPrediction();
    });
}

async function submitPrediction() {
    const submitBtn = document.getElementById('predictSubmitBtn');
    const originalBtnHtml = submitBtn ? submitBtn.innerHTML : 'Calculate Market Valuation →';

    const payload = {
        area: Number(document.getElementById('areaInput').value),
        location: document.getElementById('locationSelect').value,
        bedrooms: Number(getCheckedRadioValue('bedrooms', 4)),
        bathrooms: Number(getCheckedRadioValue('bathrooms', 3)),
        stories: Number(getCheckedRadioValue('stories', 3)),
        parking: Number(getCheckedRadioValue('parking', 2)),
        furnishingstatus: getCheckedRadioValue('furnishingstatus', 'furnished'),
        mainroad: document.getElementById('mainroadCheck').checked ? 'yes' : 'no',
        guestroom: document.getElementById('guestroomCheck').checked ? 'yes' : 'no',
        basement: document.getElementById('basementCheck').checked ? 'yes' : 'no',
        hotwaterheating: document.getElementById('hotwaterheatingCheck').checked ? 'yes' : 'no',
        airconditioning: document.getElementById('airconditioningCheck').checked ? 'yes' : 'no'
    };

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner"></span> Synthesizing Comps & Appraising...`;
    }

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            renderValuationCertificate(data);
        } else {
            showToast(data.error || 'Valuation failed', 'error');
        }
    } catch (err) {
        console.error('API Error:', err);
        showToast('Unable to connect to the valuation server.', 'error');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnHtml;
        }
    }
}

// Render the Luxury Valuation Certificate & Dossier
function renderValuationCertificate(data) {
    const placeholder = document.getElementById('resultPlaceholder');
    const details = document.getElementById('resultDetails');
    const expandedDossier = document.getElementById('expandedAdvisoryDossier');

    if (placeholder) placeholder.style.display = 'none';
    if (details) details.style.display = 'block';
    if (expandedDossier) expandedDossier.style.display = 'block';

    // Pricing
    document.getElementById('resPriceInr').textContent = data.predicted_price_inr;
    document.getElementById('resPriceUsd').textContent = `~ ${data.predicted_price_usd} USD`;
    document.getElementById('resPriceSqft').textContent = `${data.price_per_sqft} / sq ft`;
    document.getElementById('resModelUsed').textContent = data.model_used;

    // 3-Tier Valuation
    if (data.financials) {
        document.getElementById('resTierLiquidation').textContent = data.financials.liquidation_value_inr;
        document.getElementById('resTierFair').textContent = data.financials.fair_market_value_inr;
        document.getElementById('resTierPeak').textContent = data.financials.peak_market_value_inr;
        document.getElementById('resMonthlyRental').textContent = data.financials.monthly_rental_inr;
        document.getElementById('resRentalYieldPct').textContent = `${data.financials.rental_yield_pct}% Gross Return`;
    }

    // Update Global Chatbot Context
    window.latestValuationContext = {
        location: data.input_summary.location,
        area: data.input_summary.area,
        price_inr: data.predicted_price_inr,
        rental_yield: data.financials ? `${data.financials.rental_yield_pct}%` : '4.6%',
        growth_score: data.financials ? `${data.financials.growth_score}/10` : '9.0/10'
    };
    if (typeof updateContextBanner === 'function') {
        updateContextBanner();
    }

    // 1. Executive Surveyor Memo
    if (data.surveyor_memo) {
        document.getElementById('resSurveyorMemo').textContent = `"${data.surveyor_memo}"`;
    }

    // 2. Neighborhood Development Stage
    if (data.development_stage) {
        const dev = data.development_stage;
        document.getElementById('resStageBadge').textContent = dev.stage_badge || dev.stage;
        document.getElementById('resStageTitle').textContent = `${data.input_summary.location} • ${dev.stage}`;
        document.getElementById('resStageProgressPct').textContent = `${dev.stage_progress}%`;
        document.getElementById('resStageProgressBar').style.width = `${dev.stage_progress}%`;
        document.getElementById('resTransitScore').textContent = `${dev.transit_score}/10`;
        document.getElementById('resInfraScore').textContent = `${dev.infra_score}/10`;
        document.getElementById('resAvgLocRate').textContent = `₹${dev.avg_market_rate.toLocaleString()}`;
        document.getElementById('resTenantProfile').textContent = dev.tenant_profile.split(',')[0];
        document.getElementById('resLocHighlights').textContent = `${dev.highlights} ${dev.development_outlook}`;
    }

    // 3. Pros & Cons Matrix
    if (data.pros_and_cons) {
        const prosBox = document.getElementById('resProsList');
        const consBox = document.getElementById('resConsList');

        if (prosBox) {
            prosBox.innerHTML = data.pros_and_cons.pros.map(item => `
                <div class="point-row">
                    <div class="bullet-icon"><i class="bi bi-check-lg"></i></div>
                    <div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: var(--text-main); margin-bottom: 2px;">
                            ${item.title} <span class="badge-tag badge-runner" style="font-size: 0.68rem; margin-left: 6px;">${item.category}</span>
                        </div>
                        <div style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.5;">${item.desc}</div>
                    </div>
                </div>
            `).join('');
        }

        if (consBox) {
            consBox.innerHTML = data.pros_and_cons.cons.map(item => `
                <div class="point-row">
                    <div class="bullet-icon"><i class="bi bi-exclamation"></i></div>
                    <div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: var(--text-main); margin-bottom: 2px;">
                            ${item.title} <span class="badge-tag" style="background: rgba(245, 158, 11, 0.15); color: var(--gold); font-size: 0.68rem; margin-left: 6px;">${item.category}</span>
                        </div>
                        <div style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.5;">${item.desc}</div>
                    </div>
                </div>
            `).join('');
        }
    }

    // 4. 5-Year Capital Growth Statistics & Chart
    if (data.financials) {
        const fin = data.financials;
        document.getElementById('resGrowthScore').textContent = `Growth Rating: ${fin.growth_score} / 10`;
        document.getElementById('resHistoricalCagr').textContent = `${fin.cagr}%`;

        if (fin.yearly_projections && fin.yearly_projections.length >= 5) {
            document.getElementById('resYear1Val').textContent = fin.yearly_projections[0].baseline_inr;
            document.getElementById('resYear3Val').textContent = fin.yearly_projections[2].baseline_inr;
            document.getElementById('resYear5Val').textContent = fin.yearly_projections[4].baseline_inr;

            currentProjections = fin.yearly_projections;
            currentBasePrice = data.predicted_price_raw;
            renderGrowthForecastChart(currentProjections, currentBasePrice);
        }
    }
}

// Render or Re-render Growth Forecast Chart
function renderGrowthForecastChart(projections, basePrice) {
    const canvas = document.getElementById('growthForecastChart');
    if (!canvas) return;

    const labels = ['Current Value', ...projections.map(p => p.year)];
    const baselineData = [basePrice / 100000, ...projections.map(p => p.baseline / 100000)];
    const conservativeData = [basePrice / 100000, ...projections.map(p => p.conservative / 100000)];
    const optimisticData = [basePrice / 100000, ...projections.map(p => p.optimistic / 100000)];

    const currentTheme = document.documentElement.getAttribute('data-theme') || 'obsidian-gold';
    const isLight = currentTheme === 'champagne-light';

    const tickColor = isLight ? '#475569' : '#94a3b8';
    const gridColor = isLight ? 'rgba(0, 0, 0, 0.08)' : 'rgba(255, 255, 255, 0.06)';
    const textColor = isLight ? '#0f172a' : '#f8fafc';

    if (growthChartInstance) {
        growthChartInstance.destroy();
    }

    growthChartInstance = new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Optimistic Growth Target (₹ Lakhs)',
                    data: optimisticData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.05)',
                    borderWidth: 2,
                    borderDash: [4, 4],
                    pointRadius: 4,
                    fill: false,
                    tension: 0.3
                },
                {
                    label: 'Expected Baseline Equity (₹ Lakhs)',
                    data: baselineData,
                    borderColor: isLight ? '#4338ca' : '#6366f1',
                    backgroundColor: isLight ? 'rgba(67, 56, 202, 0.1)' : 'rgba(99, 102, 241, 0.15)',
                    borderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    fill: '-1',
                    tension: 0.3
                },
                {
                    label: 'Conservative Floor (₹ Lakhs)',
                    data: conservativeData,
                    borderColor: '#f59e0b',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 4,
                    fill: false,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    labels: { color: tickColor, font: { family: 'Plus Jakarta Sans', size: 12 } }
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
                    grid: { color: gridColor },
                    ticks: { color: tickColor }
                },
                y: {
                    grid: { color: gridColor },
                    ticks: {
                        color: tickColor,
                        callback: function(value) { return '₹' + value + 'L'; }
                    }
                }
            }
        }
    });
}
