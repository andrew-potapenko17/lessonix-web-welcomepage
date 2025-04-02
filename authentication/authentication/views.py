from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from social_django.models import UserSocialAuth
from django.views.decorators.csrf import csrf_exempt
import pyrebase
import requests
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from . import cfg

from requests_oauthlib import OAuth1

firebase = pyrebase.initialize_app(cfg.cfg)
auth = firebase.auth()
db = firebase.database()

def main(request):
    return render(request, 'welcome.html')

def privacypolicy(request):
    return render(request, 'privacypolicy.html')

def get_user_id_by_email(email):
    try:
        users_ref = db.child('users')
        users = users_ref.get()

        if not users:
            return None  # No users found

        # Iterate through users to find the matching email
        for user in users.each():
            user_id = user.key()
            user_data = user.val()
            if user_data.get('email') == email:
                return user_id  # Return user ID when email matches

        return None  # Email not found

    except Exception as e:
        print(f"Error fetching user ID by email: {e}")
        return None

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            user_id = get_user_id_by_email(email)
            user_data = db.child("users").child(user_id).get().val()

            if not user_data:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)

            hashed_password = user_data.get("password")
            if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return JsonResponse({'error': 'Invalid email or password'}, status=401)

            # Generate JWT token
            payload = {
                "email": email,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "iat": datetime.now(timezone.utc),
            }
            token = jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

            redirect_url = f"https://lessonixapp.pythonanywhere.com/authenticate?token={token}"
            return HttpResponseRedirect(redirect_url)

        except Exception as e:
            return JsonResponse({'error': f'Authentication failed. Error: {str(e)}'}, status=401)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            # Get register_code, email, password, and confirm_password from form data
            register_code = request.POST.get('register_code')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            # Validate that all required fields are provided
            if not register_code or not email or not password or not confirm_password:
                return JsonResponse({'error': 'All fields are required'}, status=400)

            # Check if passwords match
            if password != confirm_password:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            # Validate the registration code in Firebase
            register_code_data = db.child('personalregistercodes').child(register_code).get().val()
            if not register_code_data:
                return JsonResponse({'error': 'Invalid registration code'}, status=400)

            # Get additional data associated with the registration code
            full_name = register_code_data.get('full_name')
            school_id = register_code_data.get('school_id')
            role = register_code_data.get('role')

            # Check if email already exists in the database
            existing_user = get_user_id_by_email(email)
            if existing_user:
                return JsonResponse({'error': 'Email is already registered'}, status=400)

            # Hash the password securely
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Register the user in Firebase Authentication
            user = auth.create_user_with_email_and_password(email, password)

            # Add user information to the database
            db.child("users").child(user['localId']).set({
                "full_name": full_name,
                "school_id": school_id,
                "email": email,
                "password": hashed_password,
                "role": role,
                "lvl": 1,
                "schoolStatus": 'nolesson',
            })

            # Remove the used registration code from Firebase
            db.child('personalregistercodes').child(register_code).remove()

            # Generate JWT token
            payload = {
                "email": email,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Token expires in 1 hour
                "iat": datetime.now(timezone.utc),  # Issued at time
            }
            token = jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

            # Redirect to the microservice with the JWT token
            redirect_url = f"https://lessonixapp.pythonanywhere.com/authenticate?token={token}"
            return HttpResponseRedirect(redirect_url)

        except Exception as e:
            return JsonResponse({'error': f'Registration failed. Error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



def get_google_email(access_token):
    url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        user_info = response.json()
        return user_info.get('email')
    return None


def google_auth_success(request):
    try:
        # Get the authenticated user's details
        social_user = UserSocialAuth.objects.get(provider='google-oauth2', user=request.user)
        google_data = social_user.extra_data
        access_token = google_data.get('access_token')
        
        if not access_token:
            return JsonResponse({'error': 'Unable to retrieve access token from Google'}, status=400)

        # Fetch the email using the access token
        email = get_google_email(access_token)
        if not email:
            return JsonResponse({'error': 'Unable to retrieve email from Google'}, status=400)

        # Check if the email exists in Firebase database
        try:
            user_id = get_user_id_by_email(email)
            user_data = db.child("users").child(user_id).get().val()

            if not user_data:
                return JsonResponse({'error': 'No user found with this email'}, status=401)

            # Generate JWT token
            payload = {
                "email": email,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Token expires in 1 hour
                "iat": datetime.now(timezone.utc),  # Issued at time
            }
            token = jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

            # Redirect to the microservice with the JWT token
            redirect_url = f"https://lessonixapp.pythonanywhere.com/authenticate?token={token}"
            return HttpResponseRedirect(redirect_url)

        except Exception as e:
            return JsonResponse({'error': f'Error checking user in database. {str(e)}'}, status=500)

    except UserSocialAuth.DoesNotExist:
        return JsonResponse({'error': 'Google account not linked to any user'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)


def facebook_auth_success(request):
        try:
            # Get the authenticated user's details
            social_user = UserSocialAuth.objects.get(provider='facebook', user=request.user)
            facebook_data = social_user.extra_data
            access_token = facebook_data.get('access_token')
            
            if not access_token:
                return JsonResponse({'error': 'Unable to retrieve access token from Facebook'}, status=400)

            # Fetch the email using the access token
            email = get_facebook_email(access_token)
            if not email:
                return JsonResponse({'error': 'Unable to retrieve email from Facebook'}, status=400)

            # Check if the email exists in Firebase database
            try:
                user_id = get_user_id_by_email(email)
                user_data = db.child("users").child(user_id).get().val()

                if not user_data:
                    return JsonResponse({'error': 'No user found with this email'}, status=401)

                # Generate JWT token
                payload = {
                    "email": email,
                    "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Token expires in 1 hour
                    "iat": datetime.now(timezone.utc),  # Issued at time
                }
                token = jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

                # Redirect to the microservice with the JWT token
                redirect_url = f"https://lessonixapp.pythonanywhere.com/authenticate?token={token}"
                return HttpResponseRedirect(redirect_url)

            except Exception as e:
                return JsonResponse({'error': f'Error checking user in database. {str(e)}'}, status=500)

        except UserSocialAuth.DoesNotExist:
            return JsonResponse({'error': 'Facebook account not linked to any user'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

def get_facebook_email(access_token):
        url = "https://graph.facebook.com/me?fields=email"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            return user_info.get('email')
        return None    

def twitter_auth_success(request):
    try:
        # Get the authenticated user's details from the UserSocialAuth table
        social_user = UserSocialAuth.objects.get(provider='twitter', user=request.user)
        twitter_data = social_user.extra_data

        # Retrieve the email from the extra_data (from the Twitter OAuth response)
        email = twitter_data.get('email')

        if not email:
            return JsonResponse({'error': 'Unable to retrieve email from Twitter'}, status=400)

        # Check if the email exists in Firebase database
        try:
            # Assuming you have a function that maps email to user_id in Firebase
            user_id = get_user_id_by_email(email)
            user_data = db.child("users").child(user_id).get().val()

            if not user_data:
                return JsonResponse({'error': 'No user found with this email'}, status=401)

            # Generate JWT token for the user
            payload = {
                "email": email,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Token expires in 1 hour
                "iat": datetime.now(timezone.utc),  # Issued at time
            }
            token = jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

            # Redirect to the microservice with the JWT token
            redirect_url = f"https://lessonixapp.pythonanywhere.com/authenticate?token={token}"
            return HttpResponseRedirect(redirect_url)

        except Exception as e:
            # Handle errors when checking the user in the Firebase database
            return JsonResponse({'error': f'Error checking user in database. {str(e)}'}, status=500)

    except UserSocialAuth.DoesNotExist:
        # Handle the case where the Twitter account is not linked to any user
        return JsonResponse({'error': 'Twitter account not linked to any user'}, status=400)

    except Exception as e:
        # Handle any other unexpected errors
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
