# CyberQuantic Weekly — Newsletter & Blog Pipeline

Pipeline automatisé pour générer et publier chaque semaine la newsletter **CyberQuantic Weekly** et deux articles de blog, en utilisant les données de la plateforme CyberQuantic.

## 🏗️ Architecture

```
Agent 1 (Collector)   → CyberQuantic API → use case + entreprise EU + API + prompt
Agent 2 (Generator)   → Claude via OpenRouter → newsletter HTML + article blog
Agent 3 (Publisher)   → Resend (email) + Netlify (archive publique)
Agent 4 (Scheduler)   → APScheduler (lundi 8h UTC)
```

## 📦 Contenu de la newsletter

1. 🎯 **Use Case de la semaine** — guide d'implémentation + ROI
2. 🏢 **Entreprise EU à suivre** — spotlight des 829 entreprises
3. 🔌 **API / Outil recommandé** — depuis les 246 APIs cataloguées
4. 💡 **Prompt métier prêt à l'emploi** — depuis la bibliothèque de 82 prompts
5. 📊 **Chiffre IA de la semaine** — statistique B2B percutante
6. ⚖️ **EU AI Act** — conseil pratique compliance 2026
7. 🔗 **CTA** → Use Case Matcher CyberQuantic

## 🚀 Installation

```bash
cd cyberquantic-newsletter
pip install -r requirements.txt
cp .env.example .env  # puis remplir les clés
```

## 💻 Usage

```bash
# Test complet (email admin uniquement)
python main.py test elsane.tiberini@gmail.com

# Envoyer à tous les subscribers
python main.py send

# Collector seul (debug)
python main.py collect

# Démarrer le scheduler (lundi 8h UTC)
python agent4_scheduler.py
```

## 🔑 Variables d'environnement

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Clé OpenRouter pour Claude |
| `RESEND_API_KEY` | Clé Resend pour l'envoi email |
| `RESEND_FROM` | Adresse expéditeur (ex: `CyberQuantic Weekly <contact@cyberquantic.com>`) |
| `NETLIFY_AUTH_TOKEN` | Token Netlify pour le déploiement |
| `NETLIFY_SITE_ID_NEWSLETTER` | ID du site Netlify newsletter |

## 👥 Gestion des subscribers

Les abonnés sont stockés dans `subscribers.json` :

```json
{
  "subscribers": [
    { "email": "contact@company.com", "nom": "Jean Dupont", "actif": true }
  ]
}
```

Quand quelqu'un s'inscrit via la landing page Netlify, vous recevez une notification email. Ajoutez manuellement à `subscribers.json`.

## 📁 Structure

```
cyberquantic-newsletter/
├── config.py              # Configuration centralisée
├── models.py              # Modèles de données Pydantic
├── prompts.py             # Prompts Claude + listes statiques
├── agent1_collector.py    # Collecte données CyberQuantic API
├── agent2_generator.py    # Génération newsletter + blog avec Claude
├── agent3_publisher.py    # Publication Resend + Netlify
├── agent4_scheduler.py    # Scheduler APScheduler
├── main.py                # Orchestrateur
├── subscribers.json       # Liste des abonnés
├── state.json             # Rotation (UCs/entreprises déjà utilisés)
├── public/                # Site statique déployé sur Netlify
│   ├── index.html         # Landing page + archive
│   ├── newsletters/       # Toutes les newsletters
│   └── blog/              # Tous les articles blog
├── netlify/functions/
│   └── subscribe.js       # Serverless subscribe form handler
└── netlify.toml           # Config Netlify
```
