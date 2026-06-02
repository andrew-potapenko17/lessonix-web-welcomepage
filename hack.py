import jwt
from datetime import timezone, timedelta, datetime

JWT_SECRET = "XxCMcNQg6ngg0WRgJQl5eJcmMw1R6XZT4Wg65Tmxci6tQmxfx4Jj9dsNDdMGjxzl"
JWT_ALGORITHM = "HS256"
email = "112324@gmail.com"
password = "1234"

# Generate JWT token
payload = {
    "email": email,
    "password": password,
    "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Token expires in 1 hour
    "iat": datetime.now(timezone.utc),  # Issued at time
}
token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Redirect to the microservice with the JWT token
redirect_url = f"https://web-lessonixapp.onrender.com/authenticate?token={token}"
print(redirect_url)