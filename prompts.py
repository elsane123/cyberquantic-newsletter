"""
CyberQuantic Weekly — Prompts Claude pour génération newsletter + blog
"""

NEWSLETTER_SYSTEM = """Tu es l'éditeur en chef de CyberQuantic Weekly, la newsletter de référence sur l'IA B2B en Europe.
Ton style est : expert mais accessible, concret et actionnable, bilingue (sections en français avec termes EN quand pertinent).
Tu génères du HTML email inline-styled, compatible avec tous les clients email.
Chaque section doit apporter une valeur immédiate et pratique au lecteur."""

def newsletter_prompt(ctx) -> str:
    return f"""Génère la newsletter hebdomadaire CyberQuantic Weekly pour la semaine du {ctx.date_str}.

DONNÉES DE LA SEMAINE :

1. USE CASE VEDETTE :
   Titre: {ctx.use_case.name}
   Description: {ctx.use_case.description[:400]}
   Secteur: {ctx.use_case.sector}
   Fonction: {ctx.use_case.function}
   ROI: {ctx.use_case.roi}
   Audiences: {', '.join(ctx.use_case.targetAudiences[:3])}

2. ENTREPRISE EU SPOTLIGHT :
   Nom: {ctx.company.title}
   Pays: {ctx.company.country}
   Description: {ctx.company.description[:300]}
   Capabilities: {', '.join(ctx.company.capabilities[:4])}
   Industries: {', '.join(ctx.company.industry[:3])}
   Site: {ctx.company.website}

3. API / OUTIL RECOMMANDÉ :
   Nom: {ctx.api.title}
   Description: {ctx.api.description[:250]}
   Capabilities: {', '.join(ctx.api.capabilities[:3])}
   Site: {ctx.api.website}

4. PROMPT MÉTIER :
   Titre: {ctx.prompt.title}
   Description: {ctx.prompt.description[:200]}
   Fonction: {ctx.prompt.function}

5. STAT IA : {ctx.ai_stat if ctx.ai_stat else 'Génère une statistique IA B2B récente et percutante'}

6. EU AI ACT TIP : {ctx.eu_ai_act_tip if ctx.eu_ai_act_tip else 'Génère un conseil pratique sur la conformité EU AI Act 2026'}

Génère la newsletter complète en HTML inline avec cette structure EXACTE :

<structure>
  [HEADER avec logo CyberQuantic, dégradé violet #4F46E5→#7C3AED, date]
  [INTRO : 2-3 phrases d'accroche sur l'IA B2B cette semaine]
  [SECTION 1 : 🎯 Use Case de la semaine — titre accrocheur, description pratique, ROI concret, comment implémenter en 3 étapes]
  [SECTION 2 : 🏢 Entreprise EU à suivre — contexte, pourquoi maintenant, lien vers leur site]
  [SECTION 3 : 🔌 API/Outil de la semaine — ce que ça fait, pour qui, lien docs]
  [SECTION 4 : 💡 Prompt Prêt à l'Emploi — encadré avec le prompt copiable en code block style]
  [SECTION 5 : 📊 Chiffre de la semaine — stat mise en valeur visuellement]
  [SECTION 6 : ⚖️ EU AI Act — conseil pratique compliance 2026]
  [CTA PRINCIPAL : bouton "Trouvez vos use cases IA →" vers {ctx.use_case.name} matcher URL]
  [FOOTER avec liens utiles, unsubscribe, copyright]
</structure>

Contraintes HTML :
- Tout le CSS doit être inline (style="...")
- Max width 600px, fond #f1f5f9 extérieur, fond #fff intérieur
- Utiliser des emojis pour les titres de section
- Liens en #4F46E5
- Boutons CTA : background linear-gradient(135deg,#4F46E5,#7C3AED), texte blanc
- Polices : -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
- IMPORTANT : Retourner UNIQUEMENT le HTML, sans markdown ni commentaires

Aussi retourne sur la 1ère ligne (avant le HTML) le sujet de l'email préfixé par SUBJECT: et le preheader préfixé par PREHEADER:
Format:
SUBJECT: [sujet accrocheur ≤60 chars]
PREHEADER: [preheader ≤90 chars]
[HTML complet ici]
"""


BLOG_SYSTEM = """Tu es un rédacteur expert en IA B2B pour CyberQuantic.
Tu rédiges des articles de blog en français, SEO-optimisés, experts mais accessibles.
Tu génères du HTML complet, prêt à être publié."""

def blog_prompt(use_case) -> str:
    return f"""Rédige un article de blog SEO complet pour CyberQuantic sur le use case suivant.

USE CASE :
  Titre: {use_case.name}
  Description: {use_case.description[:500]}
  Secteur: {use_case.sector}
  Fonction: {use_case.function}
  ROI: {use_case.roi}
  Audiences: {', '.join(use_case.targetAudiences[:4])}

STRUCTURE DE L'ARTICLE (1200-1500 mots) :
1. Titre H1 SEO accrocheur
2. Introduction (problématique business, pourquoi maintenant)
3. Le use case expliqué (ce que c'est, comment ça fonctionne)
4. Cas d'usage concret dans le secteur {use_case.sector}
5. ROI et bénéfices mesurables
6. Guide d'implémentation en 3 étapes pratiques
7. Les outils / APIs recommandés (génériques, pas de noms propriétaires)
8. Conclusion + CTA vers le Use Case Matcher CyberQuantic

Retourne le HTML complet d'un article blog avec :
- Style inline minimal et propre
- Balises h1, h2, h3, p, ul, code bien structurées
- Fond blanc, texte #1e293b, liens #4F46E5
- Meta description SEO (dans un commentaire HTML en tête)
- SLUG suggéré en 1ère ligne : SLUG: [kebab-case-titre]
- TITLE: [titre H1]
[HTML complet ici]
"""


EU_AI_ACT_TIPS = [
    "Les systèmes d'IA à haut risque (ex: RH, crédit, sécurité) doivent être documentés avant déploiement selon l'EU AI Act Article 11.",
    "L'EU AI Act impose une transparence obligatoire pour les chatbots IA : l'utilisateur doit savoir qu'il interagit avec une IA.",
    "Les entreprises traitant des données personnelles avec l'IA doivent compléter une DPIA (Data Protection Impact Assessment) sous RGPD.",
    "L'EU AI Act interdit les systèmes de scoring social et la reconnaissance faciale en temps réel dans les espaces publics (sauf exceptions).",
    "Dès 2026, les systèmes IA à haut risque nécessitent un système de management de la qualité documenté (Art. 9 EU AI Act).",
    "Les modèles d'IA générative (GPT, Claude, Gemini) tombent sous les obligations de transparence de l'EU AI Act depuis août 2024.",
    "Une entreprise qui déploie un LLM pour des décisions RH doit maintenir des logs d'audit pendant au moins 6 mois.",
    "L'EU AI Act prévoit des amendes jusqu'à 35M€ ou 7% du CA mondial pour les violations les plus graves.",
]

AI_STATS = [
    "73% des entreprises européennes déclarent que le ROI de leurs projets IA a dépassé leurs attentes initiales (McKinsey 2025).",
    "Les entreprises utilisant l'IA dans leur service client réduisent leur temps de résolution de 35% en moyenne.",
    "L'IA générative pourrait ajouter 2,6 à 4,4 billions € de valeur annuelle à l'économie mondiale selon McKinsey.",
    "60% des CDO européens citent le manque de données de qualité comme principal frein à l'adoption de l'IA en 2025.",
    "Les équipes marketing utilisant l'IA génèrent 3x plus de contenu avec 40% moins de ressources humaines.",
    "L'automatisation IA des processus de back-office réduit les erreurs de traitement de 85% en moyenne.",
    "En 2026, 80% des nouvelles applications enterprise incluront au moins une fonctionnalité d'IA générative.",
    "Les entreprises early adopters de l'IA affichent une croissance du chiffre d'affaires 1,5x supérieure à leurs concurrents.",
]
