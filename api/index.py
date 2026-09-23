import os
import sys

# Ensure root directory is in Python path for Vercel Serverless environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app, home

# Route fallbacks for Vercel internal function resolution
@app.route('/api/index')
@app.route('/api/index/')
@app.route('/api/index.py')
def vercel_root_fallback():
    return home()

class VercelPathFix:
    """
    Middleware ensuring that requests routed via Vercel serverless functions
    receive their intended PATH_INFO so all Flask routes (/, /predict, /dashboard, etc.)
    and static assets match correctly.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        # Check if Vercel router provided original requested path in headers
        original = (
            environ.get('HTTP_X_MATCHED_PATH') or
            environ.get('HTTP_X_FORWARDED_URI') or
            environ.get('HTTP_X_REWRITE_URL') or
            environ.get('HTTP_X_ORIGINAL_URL')
        )
        if original and original not in ('/api/index', '/api/index.py', '/api/index/'):
            environ['PATH_INFO'] = original
        elif path in ('/api/index', '/api/index/', '/api/index.py'):
            environ['PATH_INFO'] = '/'
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFix(app.wsgi_app)
