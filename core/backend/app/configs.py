import os

class Settings:
  GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
  GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
  GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
  REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")

settings = Settings()