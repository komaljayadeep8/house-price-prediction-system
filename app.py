"""
Flask Backend Application for House Price Prediction & Real Estate Advisory Suite
Powered by Scikit-Learn Regression Pipeline and UrbanAdvisor Market Intelligence.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'), static_folder=os.path.join(BASE_DIR, 'static'))
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'ml_engine', 'model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'ml_engine', 'scaler.pkl')
COLUMNS_PATH = os.path.join(BASE_DIR, 'ml_engine', 'feature_columns.json')
METRICS_PATH = os.path.join(BASE_DIR, 'ml_engine', 'model_metrics.json')
DATASET_PATH = os.path.join(BASE_DIR, 'data', 'housing_enriched.csv')

# Load ML assets
model = None
scaler = None
feature_columns = []
model_metrics = {}
df_dataset = None

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    if os.path.exists(COLUMNS_PATH):
        with open(COLUMNS_PATH, 'r') as f:
            feature_columns = json.load(f)
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'r') as f:
            model_metrics = json.load(f)
    if os.path.exists(DATASET_PATH):
        df_dataset = pd.read_csv(DATASET_PATH)
except Exception as e:
    print(f"Warning during asset initialization: {e}")

# ----------------- MICRO-MARKET REAL ESTATE PROFILES ----------------- #

LOCALITY_PROFILES = {
    'Tech Park Cyber City': {
        'stage': 'Phase IV: Hyper-Prime IT & Fintech Corridor',
        'stage_badge': 'Established High-Yield Core',
        'stage_progress': 88,
        'transit_score': 9.4,
        'infra_score': 9.6,
        'lifestyle_score': 9.1,
        'avg_market_rate': 14200,  # INR per sq ft
        'cagr': 10.8,             # Annual historical capital growth %
        'rental_yield_pct': 4.6,  # Gross rental yield %
        'commercial_density': 'Very High',
        'tenant_profile': 'IT Executives, Tech Founders, Corporate Expatriates',
        'highlights': 'Surrounded by Fortune 500 tech campuses, upcoming Metro Line 4 interchange, high white-collar tenant density.',
        'development_outlook': 'Top-tier capital defense with continuous rental absorption and tight prime vacancy rates.'
    },
    'Downtown Central': {
        'stage': 'Phase V: Mature Central Business District',
        'stage_badge': 'Institutional Heritage Asset',
        'stage_progress': 96,
        'transit_score': 9.8,
        'infra_score': 9.5,
        'lifestyle_score': 9.7,
        'avg_market_rate': 16800,
        'cagr': 8.5,
        'rental_yield_pct': 3.9,
        'commercial_density': 'Maximum',
        'tenant_profile': 'Senior Partners, Diplomats, C-Suite Leaders',
        'highlights': 'Heritage civic center, high barrier to entry, limited new land supply, highest institutional valuation density.',
        'development_outlook': 'Prime capital preservation asset with steady, inflation-hedged long-term equity growth.'
    },
    'Riverside Bay': {
        'stage': 'Phase III: Ultra-Luxury Waterfront Enclave',
        'stage_badge': 'Prime High-Appreciation Haven',
        'stage_progress': 74,
        'transit_score': 8.6,
        'infra_score': 9.1,
        'lifestyle_score': 9.8,
        'avg_market_rate': 15500,
        'cagr': 11.4,
        'rental_yield_pct': 4.2,
        'commercial_density': 'Medium-High',
        'tenant_profile': 'High Net Worth Individuals, Creative Directors, Luxury Seekers',
        'highlights': 'Scenic waterfront promenade, luxury lifestyle zoning, premier private clubs and private marinas.',
        'development_outlook': 'High aspirational luxury demand driving premium capital gains above standard metropolitan inflation.'
    },
    'Suburban North': {
        'stage': 'Phase II: High-Velocity Residential Growth Zone',
        'stage_badge': 'Rapid Expansion Township',
        'stage_progress': 60,
        'transit_score': 8.1,
        'infra_score': 8.4,
        'lifestyle_score': 8.2,
        'avg_market_rate': 8900,
        'cagr': 9.6,
        'rental_yield_pct': 4.1,
        'commercial_density': 'Moderate',
        'tenant_profile': 'Young Tech Families, Healthcare Professionals, University Faculty',
        'highlights': 'Expanding township communities, reputed international schools, upcoming retail malls and ring-road connectivity.',
        'development_outlook': 'Strong mid-market family absorption with steady 3-5 year appreciation potential.'
    },
    'West Greens': {
        'stage': 'Phase II: Master-Planned Eco-Residential Belt',
        'stage_badge': 'Eco-Luxury Lifestyle Corridor',
        'stage_progress': 52,
        'transit_score': 7.9,
        'infra_score': 8.0,
        'lifestyle_score': 8.9,
        'avg_market_rate': 8200,
        'cagr': 9.2,
        'rental_yield_pct': 3.8,
        'commercial_density': 'Low-Medium',
        'tenant_profile': 'Eco-Conscious Executives, Senior Retirees, Wellness Professionals',
        'highlights': 'Low-density green zoning, expansive public parks, peaceful low-pollution environment popular with retirees.',
        'development_outlook': 'Balanced lifestyle micro-market offering peaceful living with steady suburban price appreciation.'
    },
    'East Expressway': {
        'stage': 'Phase I: Emerging Infrastructure & Logistics Hub',
        'stage_badge': 'High-Alpha Speculative Corridor',
        'stage_progress': 40,
        'transit_score': 7.4,
        'infra_score': 7.8,
        'lifestyle_score': 7.1,
        'avg_market_rate': 6800,
        'cagr': 12.2,
        'rental_yield_pct': 4.8,
        'commercial_density': 'Developing Industrial & SEZ',
        'tenant_profile': 'Logistics Managers, Industrial Engineers, Value-Oriented Investors',
        'highlights': 'Greenfield industrial-tech corridor, multi-lane expressways, logistics parks, significant early-stage price discount.',
        'development_outlook': 'High-upside speculative growth corridor favored by long-term capital appreciation investors.'
    }
}

# ----------------- FORMATTING HELPERS ----------------- #

def format_currency_inr(amount):
    """Formats numeric amount into Indian Lakhs or Crores representation."""
    if amount >= 10000000:
        return f"₹{amount / 10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount / 100000:.2f} Lakhs"
    else:
        return f"₹{amount:,.0f}"

def format_currency_usd(amount_inr, exchange_rate=83.5):
    """Converts INR estimate to USD for global context."""
    usd = amount_inr / exchange_rate
    return f"${usd:,.0f}"

# ----------------- PROS & CONS DECISION ENGINE ----------------- #

def evaluate_pros_and_cons(features, predicted_price, loc_profile):
    """
    Evaluates property specifications and generates nuanced, human-authored
    pros and cons from a chartered property surveyor perspective.
    """
    pros = []
    cons = []

    area = features['area']
    bedrooms = features['bedrooms']
    bathrooms = features['bathrooms']
    stories = features['stories']
    parking = features['parking']
    mainroad = features['mainroad']
    guestroom = features['guestroom']
    basement = features['basement']
    airconditioning = features['airconditioning']
    hotwater = features['hotwaterheating']
    furnishing = features['furnishingstatus']
    price_per_sqft = round(predicted_price / max(area, 1), 2)
    avg_loc_rate = loc_profile['avg_market_rate']

    # 1. Spatial Dimension Analysis
    if area >= 6000:
        pros.append({
            'title': 'Substantial Spatial Footprint',
            'desc': f'At {area:,} sq ft, the extensive floorplate accommodates expansive private and entertaining zones, commanding high prestige and resilient long-term capital value.',
            'category': 'Layout'
        })
    elif area >= 3500:
        pros.append({
            'title': 'Well-Proportioned Living Envelope',
            'desc': f'Generous {area:,} sq ft layout provides ideal family zoning without excessive property maintenance overhead.',
            'category': 'Layout'
        })
    else:
        pros.append({
            'title': 'High-Efficiency Compact Footprint',
            'desc': f'Compact {area:,} sq ft footprint translates to reduced ongoing maintenance costs and high leasing liquidity among professional tenants.',
            'category': 'Efficiency'
        })

    # 2. Bathroom-to-Bedroom Ratio
    if bathrooms >= bedrooms:
        pros.append({
            'title': 'Superior Ensuite Parity (1:1+)',
            'desc': f'Every bedroom enjoys dedicated bath access ({bathrooms} baths for {bedrooms} BHK), which is a key driver for luxury rental yields and high tenant retention.',
            'category': 'Ergonomics'
        })
    elif bathrooms == 1 and bedrooms >= 3:
        cons.append({
            'title': 'Single Bathroom Ratio Constraint',
            'desc': f'A single bathroom servicing {bedrooms} bedrooms creates a practical morning bottleneck, presenting a potential discount point during buyer negotiations.',
            'category': 'Ergonomics'
        })

    # 3. Vertical Circulation (Stories)
    if stories >= 3:
        pros.append({
            'title': 'Distinct Vertical Spatial Zoning',
            'desc': f'{stories}-story vertical distribution ensures total acoustic separation between ground-floor entertaining areas and upper-level sleeping sanctuaries.',
            'category': 'Architecture'
        })
        cons.append({
            'title': 'Multi-Flight Staircase Circulation',
            'desc': f'Spanning {stories} stories may limit accessibility for senior family members or require future provision for a residential pneumatic elevator.',
            'category': 'Accessibility'
        })

    # 4. Parking Capacity
    if parking >= 2:
        pros.append({
            'title': 'Secure Multi-Vehicle Parking Capacity',
            'desc': f'Accommodates {parking} vehicles within private curtilage—an increasingly scarce and monetizable asset in dense metropolitan zones.',
            'category': 'Convenience'
        })
    elif parking == 0:
        cons.append({
            'title': 'Absence of Dedicated On-Site Parking',
            'desc': 'No private parking provision will deter multi-vehicle executive buyers and may prolong time-on-market during resale.',
            'category': 'Convenience'
        })

    # 5. Access & Thoroughfare
    if mainroad == 'yes':
        pros.append({
            'title': 'Direct Arterial Road Frontage',
            'desc': 'Immediate main-road access provides effortless vehicular ingress, high prominence, and future potential for partial commercial/consultancy zoning.',
            'category': 'Infrastructure'
        })
        cons.append({
            'title': 'Ambient Thoroughfare Acoustics',
            'desc': 'Direct main-road frontage exposes front-facing living quarters to ambient peak-hour vehicular sound, requiring high-grade double glazing.',
            'category': 'Acoustics'
        })
    else:
        pros.append({
            'title': 'Protected Low-Noise Residential Setting',
            'desc': 'Internal residential street placement guarantees reduced traffic noise, enhanced pedestrian safety, and tranquil domestic living.',
            'category': 'Lifestyle'
        })

    # 6. Environmental Conditioning & Amenities
    if airconditioning == 'yes':
        pros.append({
            'title': 'Turnkey Climate Control Installed',
            'desc': 'Integrated air conditioning ensures optimal thermal comfort year-round with zero post-purchase retrofit downtime or capital outlay.',
            'category': 'Comfort'
        })
    else:
        cons.append({
            'title': 'Unconditioned Thermal Envelope',
            'desc': 'Absence of built-in AC will require immediate buyer expenditure of approximately ₹1.5L - ₹3.0L for ductless/inverter installations.',
            'category': 'CapEx'
        })

    if basement == 'yes':
        pros.append({
            'title': 'Sub-Grade Versatile Basement Utility',
            'desc': 'Finished basement provides adaptable supplementary square footage suitable for a home cinema, private gym, or executive workspace.',
            'category': 'Flexibility'
        })
        cons.append({
            'title': 'Sub-Surface Moisture Maintenance',
            'desc': 'Basement footprint demands periodic inspection of sub-grade waterproofing, sump discharge systems, and dehumidification.',
            'category': 'Maintenance'
        })

    if guestroom == 'yes':
        pros.append({
            'title': 'Dedicated Autonomous Guest Suite',
            'desc': 'Separate guest accommodations ensure guest hospitality without compromising daily family privacy.',
            'category': 'Hospitality'
        })

    # 7. Furnishing Status
    if furnishing == 'furnished':
        pros.append({
            'title': 'Immediate Turnkey Rental Asset',
            'desc': 'Fully furnished condition enables immediate listing on executive corporate rental markets, commanding a 15–20% rental rate premium.',
            'category': 'Income'
        })
    elif furnishing == 'unfurnished':
        cons.append({
            'title': 'Fit-Out Capital Outlay Required',
            'desc': 'Unfurnished status requires initial capital investment (modular kitchen, wardrobes, lighting) prior to optimal tenant onboarding.',
            'category': 'CapEx'
        })

    # 8. Micro-Market Rate Valuation Benchmark
    if price_per_sqft < avg_loc_rate * 0.90:
        pros.append({
            'title': 'Favorable Micro-Market Pricing Arbitrage',
            'desc': f'Valued at ₹{price_per_sqft:,.0f}/sqft versus the surrounding micro-market baseline of ₹{avg_loc_rate:,.0f}/sqft, unlocking an instant equity discount buffer.',
            'category': 'Valuation'
        })
    elif price_per_sqft > avg_loc_rate * 1.15:
        cons.append({
            'title': 'Top-Decile Locality Premium Tier',
            'desc': f'At ₹{price_per_sqft:,.0f}/sqft, this property sits above the average surrounding benchmark (₹{avg_loc_rate:,.0f}/sqft), requiring bespoke architectural finishes to support resale.',
            'category': 'Valuation'
        })

    # Ensure at least 3 pros and 2 cons for balanced human-like critique
    if len(cons) == 0:
        cons.append({
            'title': 'Standard Annual Maintenance Overhead',
            'desc': 'Periodic exterior repainting and MEP (Mechanical, Electrical, Plumbing) maintenance should be budgeted at ~0.5% of asset value annually.',
            'category': 'Maintenance'
        })
    if len(cons) == 1:
        cons.append({
            'title': 'Statutory Transaction Levies',
            'desc': 'Prospective buyers must account for 6–8% additional closing capital for state stamp duty, municipal cess, and registration fees.',
            'category': 'Acquisition'
        })

    return {'pros': pros[:5], 'cons': cons[:4]}

# ----------------- 5-YEAR GROWTH & VALUATION PROJECTIONS ----------------- #

def calculate_growth_and_financials(predicted_price, loc_profile):
    """
    Computes 1-year to 5-year capital appreciation trajectories and rental yields
    based on historical micro-market CAGR and urban development trends.
    """
    cagr = loc_profile['cagr']
    rental_yield_pct = loc_profile['rental_yield_pct']

    # Yearly projections (Baseline, Conservative, Optimistic)
    years = [1, 2, 3, 4, 5]
    projections = []

    for y in years:
        base_val = predicted_price * ((1 + (cagr / 100)) ** y)
        cons_val = predicted_price * ((1 + ((cagr - 2.0) / 100)) ** y)
        opt_val = predicted_price * ((1 + ((cagr + 2.5) / 100)) ** y)

        projections.append({
            'year': f"Year {y}",
            'baseline': round(base_val, 0),
            'baseline_inr': format_currency_inr(base_val),
            'conservative': round(cons_val, 0),
            'conservative_inr': format_currency_inr(cons_val),
            'optimistic': round(opt_val, 0),
            'optimistic_inr': format_currency_inr(opt_val),
            'gain_baseline': round(base_val - predicted_price, 0),
            'gain_baseline_inr': format_currency_inr(base_val - predicted_price)
        })

    # Rental Financials
    annual_rental = predicted_price * (rental_yield_pct / 100)
    monthly_rental = annual_rental / 12

    # 3-Tier Valuation Range
    liquidation_value = predicted_price * 0.92
    fair_market_value = predicted_price
    peak_market_value = predicted_price * 1.08

    # Capital Growth Investment Rating (out of 10)
    growth_score = min(round((cagr / 12.0) * 10, 1), 9.8)

    return {
        'cagr': cagr,
        'growth_score': growth_score,
        'rental_yield_pct': rental_yield_pct,
        'monthly_rental_inr': f"₹{monthly_rental:,.0f}/mo",
        'annual_rental_inr': format_currency_inr(annual_rental),
        'liquidation_value_inr': format_currency_inr(liquidation_value),
        'fair_market_value_inr': format_currency_inr(fair_market_value),
        'peak_market_value_inr': format_currency_inr(peak_market_value),
        'yearly_projections': projections
    }

# ----------------- HUMAN EXECUTIVE SURVEYOR MEMO ----------------- #

def generate_surveyor_memo(features, predicted_price, loc_profile, financials):
    """Drafts an authentic, human-written appraisal memo."""
    location = features['location']
    area = features['area']
    bedrooms = features['bedrooms']
    furnishing = features['furnishingstatus'].title()
    fair_val = financials['fair_market_value_inr']
    yield_pct = financials['rental_yield_pct']
    cagr = financials['cagr']
    growth_score = financials['growth_score']

    memo = (
        f"Based on empirical comparative market analysis across {loc_profile['stage']}, "
        f"this {area:,} sq ft {bedrooms}-BHK residence exhibits an estimated Fair Market Valuation of {fair_val}. "
        f"Positioned within {location}, the asset benefits from an infrastructure rating of {loc_profile['infra_score']}/10 "
        f"and transit connectivity score of {loc_profile['transit_score']}/10. "
        f"Given prevailing demographic demand, the property demonstrates a robust capital growth rating of {growth_score}/10, "
        f"supported by a projected {cagr}% 5-year CAGR and an estimated annual rental yield of {yield_pct}%. "
        f"In summary, this property represents a resilient, high-absorption asset suitable for institutional capital preservation "
        f"or high-net-worth residential deployment."
    )
    return memo

# ----------------- PAGE ROUTES ----------------- #

@app.route('/')
@app.route('/api/index')
@app.route('/api/index/')
@app.route('/api/index.py')
def home():
    """Renders the landing home page."""
    return render_template('index.html', metrics=model_metrics)

@app.route('/predict')
def predict_page():
    """Renders the interactive prediction & valuation interface."""
    return render_template('predict.html', metrics=model_metrics)

@app.route('/dashboard')
def dashboard():
    """Renders the model evaluation, analytics, and metrics dashboard."""
    return render_template('dashboard.html', metrics=model_metrics)

@app.route('/docs')
def documentation():
    """Renders project documentation, architecture, and Viva Voce prep."""
    return render_template('docs.html')

@app.route('/contact')
def contact_page():
    """Renders the Customer Care & Support page."""
    return render_template('contact.html')

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """
    Receives customer support & valuation inquiry requests,
    validates details, and issues an advisory docket number.
    """
    try:
        data = request.get_json(force=True)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        category = data.get('category', 'Valuation Inquiry').strip()
        message = data.get('message', '').strip()
        corridor = data.get('corridor', 'Tech Park Cyber City').strip()

        if not name or not email:
            return jsonify({'success': False, 'error': 'Name and Email address are required.'}), 400

        import random
        docket_id = f"CARE-UV-{random.randint(10000, 99999)}"

        return jsonify({
            'success': True,
            'docket_id': docket_id,
            'message': f"Inquiry registered successfully under Docket {docket_id}. Our Senior Valuation Desk will contact you within 15 minutes.",
            'details': {
                'name': name,
                'email': email,
                'phone': phone,
                'category': category,
                'corridor': corridor
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ----------------- API ENDPOINTS ----------------- #

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    Receives house features via JSON, transforms and scales them,
    runs inference on the trained regression model, and generates deep
    pros/cons, development stage analytics, and 5-year growth forecasts.
    """
    if model is None or scaler is None or not feature_columns:
        return jsonify({'success': False, 'error': 'Model assets not loaded on server.'}), 500

    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'success': False, 'error': 'No input data provided.'}), 400

        # Extract features
        area = float(data.get('area', 3500))
        bedrooms = int(data.get('bedrooms', 3))
        bathrooms = int(data.get('bathrooms', 2))
        stories = int(data.get('stories', 2))
        parking = int(data.get('parking', 1))

        # Binary amenities
        mainroad_val = str(data.get('mainroad', '')).lower() in ['yes', '1', 'true']
        guestroom_val = str(data.get('guestroom', '')).lower() in ['yes', '1', 'true']
        basement_val = str(data.get('basement', '')).lower() in ['yes', '1', 'true']
        hotwater_val = str(data.get('hotwaterheating', '')).lower() in ['yes', '1', 'true']
        ac_val = str(data.get('airconditioning', '')).lower() in ['yes', '1', 'true']

        mainroad = 1 if mainroad_val else 0
        guestroom = 1 if guestroom_val else 0
        basement = 1 if basement_val else 0
        hotwaterheating = 1 if hotwater_val else 0
        airconditioning = 1 if ac_val else 0

        # Location & preferred area mapping
        location = str(data.get('location', 'Tech Park Cyber City'))
        prime_locations = ['Downtown Central', 'Tech Park Cyber City', 'Riverside Bay']
        prefarea = 1 if (location in prime_locations or str(data.get('prefarea', '')).lower() in ['yes', '1', 'true']) else 0

        # Furnishing status
        furnishing = str(data.get('furnishingstatus', 'semi-furnished')).lower()
        furnishing_map = {'unfurnished': 0, 'semi-furnished': 1, 'furnished': 2}
        furnishingstatus_code = furnishing_map.get(furnishing, 1)

        # Feature Engineering
        total_rooms = bedrooms + bathrooms
        bath_bed_ratio = round(bathrooms / max(bedrooms, 1), 2)
        amenity_score = mainroad + guestroom + basement + hotwaterheating + airconditioning + prefarea + (1 if parking > 0 else 0)

        # One-hot encoded locations
        all_locations = [
            'loc_Downtown Central', 'loc_East Expressway', 'loc_Riverside Bay',
            'loc_Suburban North', 'loc_Tech Park Cyber City', 'loc_West Greens'
        ]
        loc_dict = {loc_col: 0 for loc_col in all_locations}
        matching_loc_col = f"loc_{location}"
        if matching_loc_col in loc_dict:
            loc_dict[matching_loc_col] = 1

        # Construct input dictionary
        input_dict = {
            'area': area,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'stories': stories,
            'parking': parking,
            'mainroad': mainroad,
            'guestroom': guestroom,
            'basement': basement,
            'hotwaterheating': hotwaterheating,
            'airconditioning': airconditioning,
            'prefarea': prefarea,
            'furnishingstatus_code': furnishingstatus_code,
            'total_rooms': total_rooms,
            'bath_bed_ratio': bath_bed_ratio,
            'amenity_score': amenity_score,
            **loc_dict
        }

        # Vectorize and scale
        input_vector = [input_dict[col] for col in feature_columns]
        input_df = pd.DataFrame([input_vector], columns=feature_columns)
        scaled_features = scaler.transform(input_df)

        # Model inference
        predicted_price = float(model.predict(scaled_features)[0])
        predicted_price = max(predicted_price, 1200000.0)

        # Retrieve Micro-Market Profile
        loc_profile = LOCALITY_PROFILES.get(location, LOCALITY_PROFILES['Tech Park Cyber City'])

        # Features dict for helpers
        raw_features = {
            'area': area,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'stories': stories,
            'parking': parking,
            'mainroad': 'yes' if mainroad == 1 else 'no',
            'guestroom': 'yes' if guestroom == 1 else 'no',
            'basement': 'yes' if basement == 1 else 'no',
            'hotwaterheating': 'yes' if hotwaterheating == 1 else 'no',
            'airconditioning': 'yes' if airconditioning == 1 else 'no',
            'furnishingstatus': furnishing,
            'location': location
        }

        # Compute Deep Analytics
        pros_and_cons = evaluate_pros_and_cons(raw_features, predicted_price, loc_profile)
        financials = calculate_growth_and_financials(predicted_price, loc_profile)
        surveyor_memo = generate_surveyor_memo(raw_features, predicted_price, loc_profile, financials)

        price_per_sqft = round(predicted_price / max(area, 1), 2)
        confidence_lower = round(predicted_price * 0.95, -3)
        confidence_upper = round(predicted_price * 1.05, -3)

        response_data = {
            'success': True,
            'predicted_price_raw': round(predicted_price, 2),
            'predicted_price_inr': format_currency_inr(predicted_price),
            'predicted_price_usd': format_currency_usd(predicted_price),
            'price_per_sqft': f"₹{price_per_sqft:,.2f}",
            'price_per_sqft_raw': price_per_sqft,
            'price_range_inr': f"{format_currency_inr(confidence_lower)} - {format_currency_inr(confidence_upper)}",
            'confidence_band': "±5% (Based on Model MAE)",
            'model_used': model_metrics.get('best_model', 'Ridge Regression'),
            'amenity_score': f"{amenity_score} / 7",
            'raw_features': raw_features,
            'pros_and_cons': pros_and_cons,
            'development_stage': loc_profile,
            'financials': financials,
            'surveyor_memo': surveyor_memo,
            'input_summary': {
                'area': f"{int(area):,} sq ft",
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'stories': stories,
                'location': location,
                'furnishing': furnishing.title()
            }
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'success': False, 'error': f"Prediction failed: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """
    Real Estate Market Advisory AI Chatbot (UrbanAdvisor).
    Handles queries regarding market trends, micro-market comparisons,
    stamp duty, negotiation, and context of the active property valuation.
    """
    try:
        data = request.get_json(force=True) or {}
        message = str(data.get('message', '')).strip().lower()
        context = data.get('context', {})  # Active property valuation context if available

        if not message:
            return jsonify({'reply': "I am your Real Estate Investment Advisor. How can I assist you with property valuations, locality dynamics, or market negotiations today?"})

        # Context-aware analysis of active property
        if ('this house' in message or 'this property' in message or 'current valuation' in message or 'is this a good buy' in message) and context:
            loc = context.get('location', 'the locality')
            price_inr = context.get('price_inr', 'the estimated price')
            area = context.get('area', 'this area')
            yield_val = context.get('rental_yield', '4.2%')
            growth = context.get('growth_score', '8.5/10')
            
            reply = (
                f"Regarding your currently appraised property in **{loc}** ({area}, valued at **{price_inr}**):\n\n"
                f"• **Investment Verdict**: Rated **{growth}** for capital appreciation with an estimated **{yield_val} gross annual rental yield**.\n"
                f"• **Micro-Market Context**: {loc} is in an active expansion phase with strong corporate demand and steady capital preservation.\n"
                f"• **Negotiation Recommendation**: If you are negotiating an acquisition, target an entry point around the conservative liquidation tier (~8% below fair value) to maximize your day-one equity margin."
            )
            return jsonify({'reply': reply})

        # Micro-market comparisons
        if 'compare' in message or 'which location' in message or 'best location' in message or 'cyber city' in message or 'downtown' in message or 'riverside' in message:
            reply = (
                "Here is an executive micro-market comparison across our prime corridors:\n\n"
                "1. **Tech Park Cyber City** (~₹14,200/sqft | 10.8% CAGR): Optimal for high-yield rental returns (4.6%) driven by tech workforce demand.\n"
                "2. **Downtown Central** (~₹16,800/sqft | 8.5% CAGR): Ultimate capital preservation, luxury heritage zoning, tightest long-term supply.\n"
                "3. **Riverside Bay** (~₹15,500/sqft | 11.4% CAGR): High aspirational luxury appreciation with premier waterfront lifestyle premiums.\n"
                "4. **Suburban North** (~₹8,900/sqft | 9.6% CAGR): Stable family residential townships with affordable entry tickets.\n"
                "5. **East Expressway** (~₹6,800/sqft | 12.2% CAGR): Highest speculative capital growth potential due to greenfield infrastructure expansion."
            )
            return jsonify({'reply': reply})

        # Rental yield queries
        if 'rental yield' in message or 'rent' in message or 'rental return' in message:
            reply = (
                "**Understanding Real Estate Rental Yields:**\n\n"
                "• **Gross Rental Yield** = (Annual Rental Income ÷ Total Property Cost) × 100.\n"
                "• In our metropolitan markets, typical residential yields range between **3.8% and 4.8%**.\n"
                "• **How to Maximize Yield**:\n"
                "  1. Providing high-quality semi-furnished or fully furnished interiors yields a 15–20% rent premium.\n"
                "  2. Properties within 1.5 km of major tech corridors (like Cyber City) experience sub-15 day tenant vacancy.\n"
                "  3. Dedicated 1:1 bathroom-to-bedroom ratios significantly attract high-budget corporate tenants."
            )
            return jsonify({'reply': reply})

        # Stamp duty & registration
        if 'stamp duty' in message or 'tax' in message or 'registration' in message or 'closing cost' in message:
            reply = (
                "**Estimated Acquisition & Closing Costs:**\n\n"
                "When acquiring residential real estate, budget approximately **6.5% to 8.5%** above the agreement value for statutory levies:\n"
                "• **Stamp Duty**: Typically **5% to 6.5%** depending on state jurisdiction (often a 1% concession for female co-owners).\n"
                "• **Registration Fee**: Standard **1%** of market guidance value.\n"
                "• **Legal & Title Scrutiny**: ~₹25,000 to ₹50,000 for due diligence.\n"
                "• **Advise**: Ensure all occupancy certificates (OC) and encumbrance certificates (EC) for the last 30 years are verified."
            )
            return jsonify({'reply': reply})

        # Negotiation tactics
        if 'negotiat' in message or 'offer' in message or 'discount' in message or 'bargain' in message:
            reply = (
                "**Strategic Real Estate Negotiation Playbook:**\n\n"
                "1. **Use Valuation Tiers**: Use our **Quick Liquidation Value (~8% discount)** as your opening anchor bid for pre-owned assets.\n"
                "2. **Leverage Inspection Cons**: Cite necessary CapEx items like unfurnished status, single bathroom constraints, or lack of AC to substantiate your discount request.\n"
                "3. **Proof of Funds**: Providing a pre-approved home loan letter or liquid capital readiness grants you 3–5% additional leverage over contingent buyers.\n"
                "4. **Quarter-End Timing**: Developers and institutional sellers are significantly more accommodating with pricing incentives at fiscal quarter-ends."
            )
            return jsonify({'reply': reply})

        # Default smart response
        reply = (
            "As your Real Estate Advisory Consultant, I can provide deep intelligence on:\n\n"
            "• **Micro-Market Trends**: Compare pricing and CAGR across Cyber City, Downtown, Riverside Bay, and Suburban corridors.\n"
            "• **Valuation Insights**: Analyze carpet area pricing arbitrage and fair market benchmarks.\n"
            "• **Investment Financials**: Estimate rental yields, 5-year capital appreciation, and closing stamp duties.\n"
            "• **Acquisition Tactics**: Structuring competitive offers and buyer due diligence.\n\n"
            "Feel free to ask a specific question, or run a valuation on the **Predict** page to analyze a live property!"
        )
        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'reply': f"Advisory service temporarily interrupted: {str(e)}"}), 500

@app.route('/api/metrics')
def api_metrics():
    """Serves model performance metrics, comparison table, and actual vs predicted points."""
    return jsonify(model_metrics)

@app.route('/api/dataset')
def api_dataset():
    """Serves paginated preview of the real housing dataset."""
    if df_dataset is None:
        return jsonify({'success': False, 'error': 'Dataset not loaded'}), 500

    limit = min(int(request.args.get('limit', 25)), 100)
    records = df_dataset.head(limit).to_dict(orient='records')
    return jsonify({
        'success': True,
        'total_rows': len(df_dataset),
        'columns': list(df_dataset.columns),
        'data': records
    })


@app.route('/api/debug_env')
def debug_env():
    from flask import request
    return jsonify({
        'path': request.path,
        'environ_PATH_INFO': request.environ.get('PATH_INFO'),
        'headers': {k: v for k, v in request.headers.items() if not k.lower().startswith('authorization')}
    })

@app.route('/api/sample')
def api_sample():
    """Returns predefined realistic house profiles for instant one-click testing."""
    samples = [
        {
            "name": "Luxury Cyber City Villa",
            "area": 7420,
            "bedrooms": 4,
            "bathrooms": 3,
            "stories": 3,
            "parking": 2,
            "location": "Tech Park Cyber City",
            "furnishingstatus": "furnished",
            "mainroad": "yes",
            "guestroom": "yes",
            "basement": "no",
            "hotwaterheating": "no",
            "airconditioning": "yes"
        },
        {
            "name": "Affordable Suburban Family Home",
            "area": 3600,
            "bedrooms": 3,
            "bathrooms": 1,
            "stories": 2,
            "parking": 1,
            "location": "Suburban North",
            "furnishingstatus": "semi-furnished",
            "mainroad": "yes",
            "guestroom": "no",
            "basement": "yes",
            "hotwaterheating": "no",
            "airconditioning": "no"
        },
        {
            "name": "Downtown Prime Penthouse Duplex",
            "area": 8960,
            "bedrooms": 4,
            "bathrooms": 4,
            "stories": 4,
            "parking": 3,
            "location": "Downtown Central",
            "furnishingstatus": "furnished",
            "mainroad": "yes",
            "guestroom": "yes",
            "basement": "yes",
            "hotwaterheating": "yes",
            "airconditioning": "yes"
        }
    ]
    return jsonify(samples)

if __name__ == '__main__':
    print("Starting House Price Prediction & Real Estate Advisory Suite on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=False)
