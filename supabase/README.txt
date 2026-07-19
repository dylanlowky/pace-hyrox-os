Replace these files in your project:
- core/auth.py
- views/home.py
- views/activities.py

Email confirmation redirect:
- Add APP_URL to .env and Streamlit secrets using your deployed Streamlit URL.
- In Supabase Authentication > URL Configuration, use the same URL as Site URL and add it under Redirect URLs.
