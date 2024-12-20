from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import pyrebase
import jwt
from datetime import datetime, timezone, timedelta
from . import cfg

firebase = pyrebase.initialize_app(cfg.cfg)
auth = firebase.auth()
db = firebase.database()

def main(request):
    return render(request, 'welcome.html')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            # Get email and password from form-encoded data
            email = request.POST.get('email')
            password = request.POST.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            # Authenticate user with Firebase
            user = auth.sign_in_with_email_and_password(email, password)

            # Generate JWT token
            payload = {
                "email": email,
                "password": password,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Token expires in 1 hour
                "iat": datetime.now(timezone.utc),  # Issued at time
            }
            token = jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

            # Redirect to the microservice with the JWT token
            redirect_url = f"https://lessonixapp.pythonanywhere.com/authenticate?token={token}"
            return HttpResponseRedirect(redirect_url)

        except Exception as e:
            return JsonResponse({'error': f'Authentication failed. Error: {str(e)}'}, status=401)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            # Get register_code, email and password from form-encoded data
            register_code = request.POST.get('register_code')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            # Not written data
            if not register_code or not email or not password:
                messages.error(request, "All data required")
                return
            
            # Check if passwrods match
            if password!=confirm_password:
                messages.error(request, "Passwords do not match")
                return

            # Validate the registration code in Firebase
            register_code_data = db.child('personalregistercodes').child(register_code).get().val()
            if not register_code_data:
                messages.error(request, "Invalid registration code")
                return redirect('register')
            
            # Get data from registercode
            full_name = register_code_data.get('full_name')
            school_id = register_code_data.get('school_id')
            role = register_code_data.get('role')
                
            # Register new user
            user = auth.create_user_with_email_and_password(email, password)

            # Add info to DB
            db.child("users").child(user['localId']).set({
                "full_name": full_name,
                "school_id": school_id,
                "email": email,
                "role": role,
                "schoolStatus": 'nolesson',
            })

            # Generate JWT token
            payload = {
                "email": email,
                "password": password,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Token expires in 1 hour
                "iat": datetime.now(timezone.utc),  # Issued at time
            }

            token = jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

            # Redirect to the microservice with the JWT token
            redirect_url = f"https://lessonixapp.pythonanywhere.com/authenticate?token={token}"
            return HttpResponseRedirect(redirect_url)

        except Exception as e:
            return JsonResponse({'error': f'Authentication failed. Error: {str(e)}'}, status=401)

    return JsonResponse({'error': 'Invalid request method'}, status=405)