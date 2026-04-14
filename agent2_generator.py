"""
Agent 2 — Generator
Use Claude to generate newsletter HTML + blog article from the weekly context
"""
import re
from openai import OpenAI
from config import *
from models import NewsletterContext, NewsletterDraft
from prompts import NEWSLETTER_SYSTEM, BLOG_SYSTEM, newsletter_prompt, blog_prompt


def llm_client() -> OpenAI:
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)


def call_llm(system: str, user: str) -> str:
    client = llm_client()
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user',   'content': user}
        ]
    )
    return resp.choices[0].message.content or ''


def parse_newsletter(raw: str) -> tuple[str, str, str]:
    """Extract SUBJECT, PREHEADER and HTML body from LLM output."""
    subject  = 'CyberQuantic Weekly — L\'essentiel de l\'IA B2B'
    preheader = 'Use case, entreprise EU, API et prompt de la semaine'
    html = raw

    lines = raw.split('\n')
    html_lines = []
    for line in lines:
        if line.startswith('SUBJECT:'):
            subject = line.replace('SUBJECT:', '').strip()
        elif line.startswith('PREHEADER:'):
            preheader = line.replace('PREHEADER:', '').strip()
        else:
            html_lines.append(line)
    html = '\n'.join(html_lines).strip()
    # Remove accidental markdown fences
    html = re.sub(r'^```html\s*', '', html, flags=re.MULTILINE)
    html = re.sub(r'^```\s*$', '', html, flags=re.MULTILINE)
    return subject, preheader, html.strip()


def parse_blog(raw: str) -> tuple[str, str, str]:
    """Extract SLUG, TITLE and HTML body from LLM output."""
    slug  = 'use-case-ia-semaine'
    title = 'Use Case IA de la Semaine'
    html  = raw

    lines = raw.split('\n')
    html_lines = []
    for line in lines:
        if line.startswith('SLUG:'):
            slug = line.replace('SLUG:', '').strip()
        elif line.startswith('TITLE:'):
            title = line.replace('TITLE:', '').strip()
        else:
            html_lines.append(line)
    html = '\n'.join(html_lines).strip()
    html = re.sub(r'^```html\s*', '', html, flags=re.MULTILINE)
    html = re.sub(r'^```\s*$', '', html, flags=re.MULTILINE)
    return slug, title, html.strip()


def wrap_blog_in_page(title: str, content_html: str, date_iso: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — CyberQuantic</title>
  <meta name="description" content="{title} — Analyse experte IA B2B par CyberQuantic">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc; color: #1e293b; line-height: 1.7; }}
    .page {{ max-width: 820px; margin: 0 auto; background: #fff;
             padding: 48px 64px; min-height: 100vh; }}
    @media(max-width:640px){{ .page {{ padding: 24px 20px; }} }}
    h1 {{ font-size: 2em; font-weight: 800; margin-bottom: 16px; line-height: 1.3; }}
    h2 {{ font-size: 1.4em; font-weight: 700; margin: 40px 0 12px; color: #4F46E5; }}
    h3 {{ font-size: 1.1em; font-weight: 600; margin: 28px 0 8px; }}
    p  {{ margin-bottom: 16px; }}
    ul, ol {{ margin: 0 0 16px 24px; }}
    li {{ margin-bottom: 8px; }}
    a  {{ color: #4F46E5; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px;
             font-size: 0.9em; font-family: monospace; }}
    pre  {{ background: #f1f5f9; padding: 16px; border-radius: 8px;
             overflow-x: auto; margin-bottom: 16px; }}
    .header {{ background: linear-gradient(135deg,#4F46E5 0%,#7C3AED 100%);
               padding: 40px 64px; text-align: center; margin: -48px -64px 48px; }}
    @media(max-width:640px){{ .header {{ margin: -24px -20px 32px; padding: 32px 20px; }} }}
    .header h1 {{ color: #fff; }}
    .header p  {{ color: rgba(255,255,255,0.8); font-size: 0.9em; }}
    .cta {{ display: inline-block; background: linear-gradient(135deg,#4F46E5,#7C3AED);
             color: #fff !important; padding: 14px 32px; border-radius: 8px;
             font-weight: 600; margin: 24px 0; }}
    .footer {{ border-top: 1px solid #e2e8f0; margin-top: 48px; padding-top: 24px;
               text-align: center; color: #94a3b8; font-size: 0.85em; }}
  </style>
</head>
<body>
<div class="page">
  <div class="header">
    <h1>CyberQuantic Blog</h1>
    <p>L'IA B2B en Europe — Analyses & Guides pratiques</p>
  </div>
  <p style="color:#94a3b8;font-size:0.85em;margin-bottom:32px">Publié le {date_iso} par <strong style="color:#4F46E5">CyberQuantic</strong></p>
  {content_html}
  <p style="margin-top:40px">
    <a href="{CQ_MATCHER_URL}" class="cta">Trouvez vos use cases IA →</a>
  </p>
  <div class="footer">
    <p>© 2026 CyberQuantic · <a href="{CQ_SITE_URL}">cyberquantic.com</a> · <a href="{CQ_MATCHER_URL}">Use Case Matcher</a></p>
    <p style="margin-top:8px"><a href="/blog">Retour au blog</a></p>
  </div>
</div>
</body>
</html>"""


def generate(ctx: NewsletterContext) -> NewsletterDraft:
    print('\n✍️  Agent 2 — Generating newsletter + blog with Claude...')

    # ── Newsletter ────────────────────────────────────────────────────────────
    print('  📧 Generating newsletter HTML...')
    raw_newsletter = call_llm(NEWSLETTER_SYSTEM, newsletter_prompt(ctx))
    subject, preheader, newsletter_html = parse_newsletter(raw_newsletter)
    print(f'  ✅ Subject  : {subject}')
    print(f'  ✅ Length   : {len(newsletter_html)} chars')

    # ── Blog Article ─────────────────────────────────────────────────────────
    print('  📝 Generating blog article HTML...')
    raw_blog = call_llm(BLOG_SYSTEM, blog_prompt(ctx.blog_use_case))
    slug, title, blog_content = parse_blog(raw_blog)
    blog_html = wrap_blog_in_page(title, blog_content, ctx.date_iso)
    print(f'  ✅ Blog slug: {slug}')
    print(f'  ✅ Blog title: {title}')

    # ── Save to output ────────────────────────────────────────────────────────
    ts = ctx.date_iso.replace('-', '')
    (OUTPUT_DIR / f'newsletter_{ts}.html').write_text(newsletter_html, encoding='utf-8')
    (OUTPUT_DIR / f'blog_{ts}_{slug}.html').write_text(blog_html, encoding='utf-8')
    print(f'  💾 Saved to output/')

    return NewsletterDraft(
        date_str=ctx.date_str,
        date_iso=ctx.date_iso,
        subject=subject,
        preheader=preheader,
        html_body=newsletter_html,
        blog_html=blog_html,
        blog_title=title,
        blog_slug=slug
    )


if __name__ == '__main__':
    from agent1_collector import collect
    ctx = collect()
    draft = generate(ctx)
    print(f'\nDraft ready: {draft.subject}')
