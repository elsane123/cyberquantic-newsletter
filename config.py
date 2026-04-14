"""
CyberQuantic Weekly — Configuration centralisée
"""
import os, pathlib
from dotenv import load_dotenv

load_dotenv()

# ─── CyberQuantic API ────────────────────────────────────────────────────────
CQ_BASE        = 'https://api.cyberquantic.com'
CQ_EMAIL       = 'admin@test.fr'
CQ_PASSWORD    = 'AdminCyberQuantic!!!2025'
CQ_MATCHER_URL = 'https://cyberquantic-matcher.netlify.app'
CQ_SITE_URL    = 'https://www.cyberquantic.com'

# Knowledge Base IDs
KB_COMPANIES   = '667564204c93fdc8d68a19d8'
KB_APIS        = '667564204c93fdc8d68a19d9'
KB_PROMPTS     = '667564204c93fdc8d68a19da'
KB_AGENTS      = '66756420b5190c688a19817d'
# Note: use cases fetched via /usecases endpoint

# ─── LLM (OpenRouter) ────────────────────────────────────────────────────────
OPENROUTER_API_KEY  = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
LLM_MODEL           = 'anthropic/claude-sonnet-4-5'
LLM_TEMPERATURE     = 0.5
LLM_MAX_TOKENS      = 4096

# ─── Resend ──────────────────────────────────────────────────────────────────
RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
RESEND_FROM    = os.getenv('RESEND_FROM', 'CyberQuantic Weekly <contact@cyberquantic.com>')

# ─── Netlify ─────────────────────────────────────────────────────────────────
NETLIFY_AUTH_TOKEN = os.getenv('NETLIFY_AUTH_TOKEN', '')
NETLIFY_SITE_ID    = os.getenv('NETLIFY_SITE_ID_NEWSLETTER', '')
NETLIFY_SITE_URL   = 'https://cyberquantic-newsletter.netlify.app'

# ─── Scheduler ───────────────────────────────────────────────────────────────
# Newsletter : chaque lundi à 8h UTC
NEWSLETTER_DAY_OF_WEEK = 'mon'
NEWSLETTER_HOUR_UTC    = 8
NEWSLETTER_MINUTE_UTC  = 0

# Blog posts : mardi + jeudi à 9h UTC
BLOG_DAYS_OF_WEEK = 'tue,thu'
BLOG_HOUR_UTC     = 9
BLOG_MINUTE_UTC   = 0

# ─── Chemins locaux ──────────────────────────────────────────────────────────
BASE_DIR     = pathlib.Path(__file__).parent
OUTPUT_DIR   = BASE_DIR / 'output'
PUBLIC_DIR   = BASE_DIR / 'public'
BLOG_DIR     = PUBLIC_DIR / 'blog'
STATE_FILE   = BASE_DIR / 'state.json'
SUBS_FILE    = BASE_DIR / 'subscribers.json'

for d in [OUTPUT_DIR, PUBLIC_DIR, BLOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)
