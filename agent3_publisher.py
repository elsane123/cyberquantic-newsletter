"""
Agent 3 — Publisher
Publish newsletter via Resend + Netlify archive
"""
import json, shutil, logging
from datetime import datetime, timezone
from pathlib import Path
import requests as req
from config import *
from models import NewsletterDraft, PublicationResult

logging.basicConfig(level=logging.INFO, format='%(asctime)s [Agent3] %(levelname)s %(message)s')
log = logging.getLogger('agent3')


# ─── Subscriber management ────────────────────────────────────────────────────

def load_subscribers() -> list:
    if not SUBS_FILE.exists():
        return []
    data = json.loads(SUBS_FILE.read_text(encoding='utf-8'))
    return [s for s in data.get('subscribers', []) if s.get('actif', True)]


# ─── Resend email sender ──────────────────────────────────────────────────────

def send_email(to: str, subject: str, html: str, preheader: str = '') -> bool:
    if not RESEND_API_KEY:
        log.error('RESEND_API_KEY not configured')
        return False
    payload = {
        'from': RESEND_FROM,
        'to': [to],
        'subject': subject,
        'html': html,
        'headers': {'X-Entity-Ref-ID': subject, 'List-Unsubscribe': f'<mailto:unsubscribe@cyberquantic.com>'}
    }
    r = req.post('https://api.resend.com/emails',
                 headers={'Authorization': f'Bearer {RESEND_API_KEY}', 'Content-Type': 'application/json'},
                 json=payload)
    if r.status_code in (200, 201):
        log.info(f'  ✅ Sent to {to}')
        return True
    else:
        log.error(f'  ❌ Failed {to}: {r.status_code} {r.text[:100]}')
        return False


# ─── Netlify archive builder ──────────────────────────────────────────────────

def build_newsletter_archive(draft: NewsletterDraft):
    """Save newsletter HTML to public/newsletters/ for Netlify hosting."""
    newsletters_dir = PUBLIC_DIR / 'newsletters'
    newsletters_dir.mkdir(exist_ok=True)
    ts = draft.date_iso.replace('-', '')
    # Save current newsletter
    path = newsletters_dir / f'{ts}.html'
    path.write_text(draft.html_body, encoding='utf-8')
    # Update latest
    shutil.copy2(path, newsletters_dir / 'latest.html')
    log.info(f'  💾 Newsletter saved: {path}')


def build_blog_post(draft: NewsletterDraft):
    """Save blog article to public/blog/ for Netlify hosting."""
    if not draft.blog_html or not draft.blog_slug:
        return
    ts = draft.date_iso.replace('-', '')
    path = BLOG_DIR / f'{ts}-{draft.blog_slug}.html'
    path.write_text(draft.blog_html, encoding='utf-8')
    log.info(f'  💾 Blog post saved: {path}')
    return path


def build_archive_index():
    """Rebuild public/index.html with all newsletters and blog posts."""
    newsletters_dir = PUBLIC_DIR / 'newsletters'
    manifest_path = newsletters_dir / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else []
    blog_files = sorted(BLOG_DIR.glob('*.html'), reverse=True) if BLOG_DIR.exists() else []

    nl_items = ''
    for m in manifest[:20]:
        date_fmt = m['date_iso']
        nl_items += f"""
        <li style="padding:16px 0; border-bottom:1px solid #e2e8f0; display:flex; flex-direction:column; gap:4px;">
            <div style="font-size:0.85em; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">{date_fmt}</div>
            <a href="/newsletters/{m['id']}.html" style="font-weight:700; font-size:1.15em; color:#4F46E5; display:block; line-height:1.3; text-decoration:none;">{m.get('subject', 'Édition du ' + date_fmt)}</a>
            <p style="font-size:0.95em; color:#475569; line-height:1.5;">{m.get('preheader', '')}</p>
        </li>"""
    blog_items = '\n'.join([
        f'<li><a href="/blog/{f.name}">{f.stem[9:].replace("-", " ").title()}</a></li>'
        for f in blog_files[:20]
    ])

    html = f"""<!DOCTYPE html>
<html lang="fr"><head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>CyberQuantic Weekly — Newsletter IA B2B Europe</title>
  <meta name="description" content="L'essentiel de l'IA B2B européenne chaque semaine. Use cases, entreprises EU, APIs et prompts métier.">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f1f5f9;color:#1e293b}}
    .hero{{background:linear-gradient(135deg,#4F46E5,#7C3AED);padding:60px 24px;text-align:center;color:#fff}}
    .hero h1{{font-size:2.2em;font-weight:800;margin-bottom:12px}}
    .hero p{{font-size:1.1em;opacity:.85;max-width:520px;margin:0 auto 32px}}
    .subscribe{{background:#fff;display:inline-flex;border-radius:8px;overflow:hidden;max-width:460px;width:100%}}
    .subscribe input{{flex:1;padding:14px 16px;border:none;outline:none;font-size:15px;color:#1e293b}}
    .subscribe button{{background:#4F46E5;color:#fff;border:none;padding:14px 24px;font-weight:600;cursor:pointer;font-size:15px}}
    .container{{max-width:900px;margin:0 auto;padding:48px 24px}}
    .grid{{display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-top:16px}}
    @media(max-width:640px){{.grid{{grid-template-columns:1fr}}}}
    h2{{font-size:1.4em;font-weight:700;margin-bottom:20px;color:#4F46E5}}
    ul{{list-style:none}}
    li{{border-bottom:1px solid #e2e8f0;padding:12px 0}}
    a{{color:#4F46E5;text-decoration:none;font-size:15px}}
    a:hover{{text-decoration:underline}}
    .latest{{background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 16px rgba(0,0,0,.06)}}
    .cta{{display:inline-block;background:linear-gradient(135deg,#4F46E5,#7C3AED);color:#fff;padding:13px 28px;border-radius:8px;font-weight:600;margin-top:16px;text-decoration:none}}
    .footer{{text-align:center;padding:32px;color:#94a3b8;font-size:.85em;border-top:1px solid #e2e8f0;margin-top:48px}}
  </style>
</head>
<body>
<div class="hero">
  <h1>CyberQuantic Weekly 📬</h1>
  <p>L'essentiel de l'IA B2B européenne chaque lundi — use cases, entreprises EU, APIs et prompts métier.</p>
  <form class="subscribe" action="/.netlify/functions/subscribe" method="post">
    <input type="email" name="email" placeholder="votre@email.com" required>
    <button type="submit">S'abonner →</button>
  </form>
</div>
<div class="container">
  <div style="text-align:center;margin-bottom:32px">
    <a href="/newsletters/latest.html" class="cta">Lire la dernière newsletter →</a>
  </div>
  <div class="grid">
    <div class="latest">
      <h2>📧 Dernières newsletters</h2>
      <ul>{nl_items if nl_items else '<li style="color:#94a3b8">Première édition en cours...</li>'}</ul>
    </div>
    <div class="latest">
      <h2>📝 Derniers articles blog</h2>
      <ul>{blog_items if blog_items else '<li style="color:#94a3b8">Premier article en cours...</li>'}</ul>
    </div>
  </div>
  <div style="text-align:center;margin-top:48px">
    <p style="color:#64748b;margin-bottom:16px">368 use cases IA B2B • 829 entreprises EU • 246 APIs</p>
    <a href="{CQ_MATCHER_URL}" class="cta">Trouver mes use cases IA →</a>
  </div>
</div>
<div class="footer">
  © 2026 CyberQuantic · <a href="{CQ_SITE_URL}">cyberquantic.com</a>
</div>
</body></html>"""
    (PUBLIC_DIR / 'index.html').write_text(html, encoding='utf-8')
    log.info('  🔄 Archive index rebuilt')


# ─── Netlify deploy ───────────────────────────────────────────────────────────

def deploy_to_netlify() -> dict:
    if not NETLIFY_AUTH_TOKEN or not NETLIFY_SITE_ID:
        return {'success': False, 'error': 'Netlify not configured'}
    try:
        import zipfile, io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in PUBLIC_DIR.rglob('*'):
                if f.is_file():
                    zf.write(f, f.relative_to(PUBLIC_DIR))
        buf.seek(0)
        r = req.post(
            f'https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys',
            headers={'Authorization': f'Bearer {NETLIFY_AUTH_TOKEN}', 'Content-Type': 'application/zip'},
            data=buf.getvalue(), timeout=120
        )
        if r.status_code in (200, 201):
            url = r.json().get('ssl_url') or r.json().get('url') or NETLIFY_SITE_URL
            log.info(f'  🌐 Netlify deployed: {url}')
            return {'success': True, 'url': url}
        return {'success': False, 'error': f'HTTP {r.status_code}: {r.text[:100]}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ─── Main publish function ────────────────────────────────────────────────────

def publish(draft: NewsletterDraft, test_email: str = None) -> PublicationResult:
    log.info(f'=== Agent 3 — Publishing: {draft.subject} ===')

    # 1. Save newsletter + blog to public/
    build_newsletter_archive(draft)
    build_blog_post(draft)
    build_archive_index()

    # 2. Send emails via Resend
    subscribers = load_subscribers()
    targets = [{'email': test_email, 'nom': 'Test'}] if test_email else subscribers

    sent = 0
    for sub in targets:
        email = sub.get('email', '')
        if not email:
            continue
        if send_email(email, draft.subject, draft.html_body, draft.preheader):
            sent += 1

    log.info(f'  📧 Emails sent: {sent}/{len(targets)}')

    # 3. Deploy to Netlify
    netlify_result = deploy_to_netlify()
    archive_url = netlify_result.get('url', NETLIFY_SITE_URL) if netlify_result['success'] else NETLIFY_SITE_URL
    blog_url = f"{archive_url}/blog/{draft.date_iso.replace('-','')}-{draft.blog_slug}.html" if draft.blog_slug else None

    return PublicationResult(
        success=True,
        newsletter_url=f"{archive_url}/newsletters/{draft.date_iso.replace('-','')}.html",
        blog_url=blog_url,
        subscribers_count=len(subscribers),
        emails_sent=sent,
        published_at=datetime.now(timezone.utc)
    )


if __name__ == '__main__':
    import sys
    from agent1_collector import collect
    from agent2_generator import generate
    test = sys.argv[1] if len(sys.argv) > 1 else None
    ctx = collect()
    draft = generate(ctx)
    result = publish(draft, test_email=test)
    print(f'Success: {result.success} | Emails: {result.emails_sent} | URL: {result.newsletter_url}')
