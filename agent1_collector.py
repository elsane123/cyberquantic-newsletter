"""
Agent 1 — Collector
Fetch weekly content from CyberQuantic API: use case, company, API, prompt
"""
import json, random, datetime, requests
from config import *
from models import CQUseCase, CQCompany, CQApi, CQPrompt, NewsletterContext
from prompts import EU_AI_ACT_TIPS, AI_STATS


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {'used_usecases': [], 'used_companies': [], 'used_apis': [], 'used_prompts': [], 'newsletter_count': 0, 'blog_count': 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def get_session() -> requests.Session:
    s = requests.Session()
    r = s.post(f'{CQ_BASE}/login', json={'email': CQ_EMAIL, 'password': CQ_PASSWORD})
    r.raise_for_status()
    return s


def pick_unused(items: list, used_ids: list) -> dict:
    """Pick a random unused item; reset used list if all exhausted."""
    unused = [x for x in items if (x.get('_id') or x.get('id', '')) not in used_ids]
    if not unused:
        unused = items  # reset rotation
    return random.choice(unused)


def extract_tag_values(tags: list, type_name: str) -> list:
    """Extract values from structured tags (KB elements). Tags can be objects or strings."""
    results = []
    for tag in tags:
        if isinstance(tag, dict) and tag.get('typeName') == type_name:
            results.extend(tag.get('values', []))
    return results



def collect() -> NewsletterContext:
    print('🔍 Agent 1 — Collecting data from CyberQuantic API...')
    session = get_session()
    state = load_state()

    # ── Use Cases (x2: newsletter + blog) ────────────────────────────────────
    r = session.get(f'{CQ_BASE}/usecases')
    all_ucs = [uc for uc in r.json() if uc.get('isVisible')]

    raw_uc = pick_unused(all_ucs, state['used_usecases'])
    uc_id = raw_uc.get('_id') or raw_uc.get('id', '')
    state['used_usecases'].append(uc_id)

    # Pick blog UC (different from newsletter UC)
    raw_blog_uc = pick_unused(all_ucs, state['used_usecases'])
    blog_id = raw_blog_uc.get('_id') or raw_blog_uc.get('id', '')
    state['used_usecases'].append(blog_id)

    def uc_to_model(raw) -> CQUseCase:
        # Use cases use displayIn for sector/function (not structured tags)
        display_in = raw.get('displayIn', [])
        sector   = display_in[0].get('level2', '') if display_in else ''
        function = display_in[0].get('level3', '') if display_in else ''
        goals    = raw.get('goals', [])
        desc_fr  = raw.get('translations', {}).get('fr', {}).get('description', '')
        desc     = desc_fr or raw.get('description', '') or raw.get('scope', '')
        roi      = raw.get('roi', '') or raw.get('perceiveInfos', '') or ''
        if isinstance(roi, list): roi = ' | '.join(roi)
        return CQUseCase(
            id=raw.get('_id') or raw.get('id', ''),
            name=raw.get('name', ''),
            description=desc,
            sector=sector,
            function=function,
            goal=goals[0] if goals else '',
            roi=str(roi)[:300],
            targetAudiences=raw.get('targetAudiences', [])[:5]
        )


    use_case = uc_to_model(raw_uc)
    blog_uc  = uc_to_model(raw_blog_uc)
    print(f'  ✅ Use case: {use_case.name}')
    print(f'  ✅ Blog UC : {blog_uc.name}')

    # ── Companies ─────────────────────────────────────────────────────────────
    r = session.get(f'{CQ_BASE}/knowledge-bases/{KB_COMPANIES}?includeElements=true')
    all_companies = r.json().get('elements', [])

    raw_co = pick_unused(all_companies, state['used_companies'])
    co_id = raw_co.get('id') or raw_co.get('_id', '')
    state['used_companies'].append(co_id)
    tags = raw_co.get('tags', [])
    company = CQCompany(
        id=co_id,
        title=raw_co.get('title', ''),
        description=raw_co.get('translations', {}).get('fr', {}).get('scope', raw_co.get('scope', raw_co.get('description', ''))),
        country=raw_co.get('country', ''),
        website=raw_co.get('link', ''),
        capabilities=extract_tag_values(tags, 'Capabilities'),
        industry=extract_tag_values(tags, 'Industry')
    )
    print(f'  ✅ Company : {company.title} ({company.country})')

    # ── APIs ──────────────────────────────────────────────────────────────────
    r = session.get(f'{CQ_BASE}/knowledge-bases/{KB_APIS}?includeElements=true')
    all_apis = r.json().get('elements', [])

    raw_api = pick_unused(all_apis, state['used_apis'])
    api_id = raw_api.get('id') or raw_api.get('_id', '')
    state['used_apis'].append(api_id)
    api_tags = raw_api.get('tags', [])
    api = CQApi(
        id=api_id,
        title=raw_api.get('title', ''),
        description=raw_api.get('translations', {}).get('fr', {}).get('scope', raw_api.get('scope', raw_api.get('description', ''))),
        website=raw_api.get('link', ''),
        capabilities=extract_tag_values(api_tags, 'Capabilities')
    )
    print(f'  ✅ API     : {api.title}')

    # ── Prompts ───────────────────────────────────────────────────────────────
    r = session.get(f'{CQ_BASE}/knowledge-bases/{KB_PROMPTS}?includeElements=true')
    all_prompts = r.json().get('elements', [])

    raw_prompt = pick_unused(all_prompts, state['used_prompts'])
    p_id = raw_prompt.get('id') or raw_prompt.get('_id', '')
    state['used_prompts'].append(p_id)
    p_tags = raw_prompt.get('tags', [])
    prompt = CQPrompt(
        id=p_id,
        title=raw_prompt.get('title', ''),
        description=raw_prompt.get('translations', {}).get('fr', {}).get('scope', raw_prompt.get('scope', raw_prompt.get('description', ''))),
        function=next(iter(extract_tag_values(p_tags, 'Function')), '')
    )
    print(f'  ✅ Prompt  : {prompt.title}')

    # ── Rotation state ────────────────────────────────────────────────────────
    state['newsletter_count'] += 1
    save_state(state)

    # ── Static tips / stats ───────────────────────────────────────────────────
    week = datetime.date.today().isocalendar()[1]
    tip  = EU_AI_ACT_TIPS[week % len(EU_AI_ACT_TIPS)]
    stat = AI_STATS[week % len(AI_STATS)]

    now = datetime.date.today()
    days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    months_fr = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    date_str = f"{days_fr[now.weekday()]} {now.day} {months_fr[now.month - 1]} {now.year}"

    ctx = NewsletterContext(
        date_str=date_str,
        date_iso=now.isoformat(),
        week_number=week,
        use_case=use_case,
        company=company,
        api=api,
        prompt=prompt,
        blog_use_case=blog_uc,
        eu_ai_act_tip=tip,
        ai_stat=stat
    )
    print(f'\n📦 Context built for {date_str} (Week {week})')
    return ctx


if __name__ == '__main__':
    ctx = collect()
    print(ctx.model_dump_json(indent=2))
