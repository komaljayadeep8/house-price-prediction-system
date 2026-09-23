"""
Automated Verification & Integration Test for House Price Prediction System
Tests ML model loading, feature scaling, prediction endpoint, metrics endpoint, and HTML routes.
"""

import sys
import json
import unittest
from app import app

class TestHousePricePrediction(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_01_home_page_status(self):
        """Verify home landing page returns 200 and loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'UrbanValuate', response.data)
        print("PASS: Home page rendered successfully.")

    def test_02_predict_page_status(self):
        """Verify prediction interface page returns 200."""
        response = self.client.get('/predict')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Valuation Studio', response.data)
        print("PASS: Prediction page rendered successfully.")

    def test_03_dashboard_page_status(self):
        """Verify dashboard page returns 200 and includes Chart.js container."""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'actualVsPredChart', response.data)
        print("PASS: Dashboard page rendered successfully.")

    def test_04_docs_page_status(self):
        """Verify documentation and viva page returns 200."""
        response = self.client.get('/docs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Viva Voce', response.data)
        print("PASS: Documentation & Viva page rendered successfully.")

    def test_05_api_metrics(self):
        """Verify /api/metrics returns genuine ML metrics."""
        response = self.client.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('best_model', data)
        self.assertIn('best_r2', data)
        self.assertIn('model_comparison', data)
        self.assertGreater(data['best_r2'], 0.60)
        print(f"PASS: /api/metrics verified (Best Model: {data['best_model']}, R2: {data['best_r2']}).")

    def test_06_api_predict_success(self):
        """Test prediction API with realistic input payload."""
        sample_payload = {
            'area': 5000,
            'bedrooms': 3,
            'bathrooms': 2,
            'stories': 2,
            'parking': 2,
            'location': 'Tech Park Cyber City',
            'furnishingstatus': 'furnished',
            'mainroad': 'yes',
            'guestroom': 'yes',
            'basement': 'no',
            'hotwaterheating': 'no',
            'airconditioning': 'yes'
        }
        response = self.client.post('/api/predict', json=sample_payload)
        self.assertEqual(response.status_code, 200)
        res_json = json.loads(response.data)
        self.assertTrue(res_json.get('success'))
        self.assertIn('predicted_price_inr', res_json)
        self.assertIn('predicted_price_raw', res_json)
        self.assertGreater(res_json['predicted_price_raw'], 1500000)
        price_display = res_json['predicted_price_inr'].replace('\u20b9', 'Rs. ')
        print(f"PASS: /api/predict generated valuation: {price_display} ({res_json['predicted_price_usd']})")

    def test_07_api_dataset_preview(self):
        """Test dataset explorer preview API."""
        response = self.client.get('/api/dataset?limit=10')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertEqual(len(data['data']), 10)
        print("PASS: /api/dataset preview endpoint verified.")

    def test_08_api_predict_deep_advisory_analytics(self):
        """Verify that prediction generates Pros/Cons, Development Stage, Financials, and Memo."""
        sample_payload = {
            'area': 6500,
            'bedrooms': 4,
            'bathrooms': 3,
            'stories': 3,
            'parking': 2,
            'location': 'Tech Park Cyber City',
            'furnishingstatus': 'furnished',
            'mainroad': 'yes',
            'guestroom': 'yes',
            'basement': 'yes',
            'hotwaterheating': 'no',
            'airconditioning': 'yes'
        }
        response = self.client.post('/api/predict', json=sample_payload)
        self.assertEqual(response.status_code, 200)
        res_json = json.loads(response.data)

        # Verify Pros & Cons
        self.assertIn('pros_and_cons', res_json)
        self.assertGreater(len(res_json['pros_and_cons']['pros']), 0)
        self.assertGreater(len(res_json['pros_and_cons']['cons']), 0)

        # Verify Development Stage
        self.assertIn('development_stage', res_json)
        self.assertIn('stage', res_json['development_stage'])
        self.assertGreater(res_json['development_stage']['transit_score'], 0)

        # Verify Financials & 5-Year Projections
        self.assertIn('financials', res_json)
        fin = res_json['financials']
        self.assertIn('liquidation_value_inr', fin)
        self.assertIn('fair_market_value_inr', fin)
        self.assertIn('peak_market_value_inr', fin)
        self.assertEqual(len(fin['yearly_projections']), 5)

        # Verify Surveyor Memo
        self.assertIn('surveyor_memo', res_json)
        self.assertGreater(len(res_json['surveyor_memo']), 50)
        print("PASS: /api/predict deep advisory analytics verified (Pros/Cons, Stage, Growth, Memo).")

    def test_09_api_chat_general_advisory(self):
        """Verify Real Estate Advisor chatbot answers micro-market comparison."""
        payload = {'message': 'Compare Cyber City vs Downtown Central'}
        response = self.client.post('/api/chat', json=payload)
        self.assertEqual(response.status_code, 200)
        res_json = json.loads(response.data)
        self.assertIn('reply', res_json)
        self.assertIn('Cyber City', res_json['reply'])
        print("PASS: /api/chat micro-market advisory verified.")

    def test_10_api_chat_with_property_context(self):
        """Verify Real Estate Advisor chatbot handles contextual queries on active house."""
        payload = {
            'message': 'Is this house a good buy?',
            'context': {
                'location': 'Tech Park Cyber City',
                'area': '6,500 sq ft',
                'price_inr': 'Rs. 85.00 Lakhs',
                'rental_yield': '4.6%',
                'growth_score': '9.0/10'
            }
        }
        response = self.client.post('/api/chat', json=payload)
        self.assertEqual(response.status_code, 200)
        res_json = json.loads(response.data)
        self.assertIn('reply', res_json)
        self.assertIn('Tech Park Cyber City', res_json['reply'])
        print("PASS: /api/chat contextual property inquiry verified.")

    def test_11_contact_page_status(self):
        """Verify Customer Care & Support page returns 200."""
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer Care', response.data)
        self.assertIn(b'Advisory Hotline', response.data)
        print("PASS: /contact page rendered successfully.")

    def test_12_api_contact_submission(self):
        """Verify /api/contact registers inquiry and returns docket ID."""
        payload = {
            'name': 'Kavita Iyer',
            'email': 'kavita@example.com',
            'phone': '+91 9876543210',
            'category': 'Valuation Verification',
            'corridor': 'Tech Park Cyber City',
            'message': 'Need physical verification for villa valuation.'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 200)
        res_json = json.loads(response.data)
        self.assertTrue(res_json['success'])
        self.assertIn('docket_id', res_json)
        self.assertTrue(res_json['docket_id'].startswith('CARE-UV-'))
        print(f"PASS: /api/contact inquiry verified (Docket: {res_json['docket_id']}).")

if __name__ == '__main__':
    unittest.main()
