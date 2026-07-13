import os
import unittest
import json
import sqlite3
from app import app, get_db_connection

class SchemeAITests(unittest.TestCase):
    
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing forms
        # Use our seeded database for testing routes
        self.client = app.test_client()

    def test_static_routes(self):
        # Verify that all core static/guest routes load successfully (status code 200)
        routes = ['/', '/about', '/schemes', '/recommend', '/eligibility', '/compare', '/calculator', '/documents', '/faq', '/contact']
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} failed to load.")

    def test_scheme_details_fail(self):
        # Invalid scheme ID should return 404
        response = self.client.get('/scheme/999')
        self.assertEqual(response.status_code, 404)

    def test_database_connection(self):
        # Test active connection to sqlite database
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        
        # Test schemes table entries count
        count = conn.execute("SELECT COUNT(*) FROM schemes").fetchone()[0]
        self.assertGreater(count, 0, "No schemes seeded in test database!")
        conn.close()

    def test_chatbot_endpoint(self):
        # Test chatbot API response
        response = self.client.post('/api/chatbot', 
                                    data=json.dumps({"query": "apply"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("reply", data)
        self.assertTrue(len(data['reply']) > 0)

    def test_recommendation_ml_model(self):
        # Test recommendation API inference pipeline
        payload = {
            "age": 25,
            "gender": "Male",
            "state": "Maharashtra",
            "occupation": "Student",
            "income": 150000.0,
            "education": "Graduate",
            "category": "SC",
            "disability_status": "No",
            "bpl_status": "No",
            "employment_status": "Student",
            "family_size": 4
        }
        response = self.client.post('/api/recommend',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("recommendations", data)
        # Should have returned matches for student (e.g. Post Matric Scholarship, etc.)
        self.assertGreater(len(data['recommendations']), 0)
        
        # Verify schema elements in return payload
        first_rec = data['recommendations'][0]
        self.assertIn("name", first_rec)
        self.assertIn("confidence", first_rec)
        self.assertIn("benefits", first_rec)
        self.assertIn("reason", first_rec)

if __name__ == "__main__":
    unittest.main()
