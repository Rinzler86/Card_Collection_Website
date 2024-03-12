from flask import Blueprint, render_template, request, current_app, url_for, redirect

# Initialize your Blueprint if not already done
merchant_bp = Blueprint('merchant', __name__, template_folder='templates')

@merchant_bp.route('/ebay_auth_redirect')
def ebay_auth_redirect():
    # eBay will redirect with an authorization code in the query parameters
    
    if auth_code := request.args.get('code', None):
        # Here you would exchange the code for an access token with eBay's API
        print(f"Authorization Code: {auth_code}")
        # For simplicity, just render a template showing the code
        return render_template('ebay_oauth_success.html', auth_code=auth_code)
    else:
        # Handle the error or missing authorization code
        return "Error or missing authorization code", 400
