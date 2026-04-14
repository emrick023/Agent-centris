# Guide de configuration — Automatisation Centris (GitHub Actions)

Extraction quotidienne des plex à vendre (~50 km autour de Sherbrooke)  
→ Fichier Excel envoyé par email chaque matin à 7h00, automatiquement.

---

## Étape 1 — Créer un dépôt GitHub privé

1. Aller sur [github.com](https://github.com) → **New repository**
2. Nom : `centris-plex-extraction` (ou autre)
3. Visibilité : **Private**
4. Cliquer **Create repository**

---

## Étape 2 — Uploader les fichiers dans le dépôt

Dans le dépôt GitHub, uploader ces 3 fichiers (glisser-déposer dans l'interface web) :

```
extraction_50km.py
requirements.txt
.github/workflows/extraction.yml
```

> **Important :** Le dossier `.github/workflows/` doit être créé exactement ainsi.  
> Sur l'interface web GitHub : cliquer **Add file → Create new file**,  
> taper ``.github/workflows/extraction.yml`` comme nom de fichier,  
> puis coller le contenu du fichier `extraction.yml`.

---

## Étape 3 — Activer l'authentification à 2 facteurs sur Gmail (si pas déjà fait)

1. Aller sur [myaccount.google.com](https://myaccount.google.com)
2. **Sécurité** → **Validation en 2 étapes** → Activer

> Sans cette étape, les mots de passe d'application ne sont pas disponibles.

---

## Étape 4 — Créer un mot de passe d'application Gmail

1. Aller sur [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Dans **Nom de l'application** : taper `Centris Extraction`
3. Cliquer **Créer**
4. Copier le code à **16 caractères** généré (ex: `abcd efgh ijkl mnop`)

> Ce code remplace ton vrai mot de passe Gmail pour les scripts automatiques.  
> Il peut être révoqué à tout moment sans changer ton vrai mot de passe.

---

## Étape 5 — Configurer les Secrets GitHub

Dans ton dépôt GitHub :  
**Settings → Secrets and variables → Actions → New repository secret**

Créer ces 3 secrets (exactement ces noms) :

| Nom du secret      | Valeur                                    |
|--------------------|-------------------------------------------|
| `GMAIL_USER`       | Ton adresse Gmail (ex: `toi@gmail.com`)  |
| `GMAIL_APP_PASSWORD` | Le code à 16 caractères de l'étape 4  |
| `EMAIL_DEST`       | L'adresse qui reçoit le fichier Excel    |

---

## Étape 6 — Tester manuellement

1. Dans ton dépôt GitHub, aller dans l'onglet **Actions**
2. Cliquer sur le workflow **"Extraction Centris — 7h00 chaque matin"**
3. Cliquer **Run workflow** → **Run workflow** (bouton vert)
4. Attendre ~30–60 minutes (le script visite toutes les villes)
5. Vérifier que l'email arrive avec le fichier `.xlsx` en pièce jointe

---

## Planification automatique

Le workflow se déclenche automatiquement :

| Saison               | Heure locale | Heure UTC | Cron         |
|----------------------|-------------|-----------|--------------|
| Hiver (nov → mars)  | 7h00 EST    | 12h00     | `0 12 * 11,12,1,2,3 *`    |
| Été (avr → oct)     | 7h00 EDT    | 11h00     | `0 11 * 4,5,6,7,8,9,10 *` |

> GitHub Actions utilise toujours UTC. Les deux lignes `cron` couvrent  
> automatiquement le changement d'heure hiver/été.

---

## Structure des fichiers

```
centris-plex-extraction/
├── extraction_50km.py          ← Script principal (extraction + email)
├── requirements.txt            ← Dépendances Python (openpyxl)
└── .github/
    └── workflows/
        └── extraction.yml      ← Planificateur GitHub Actions
```

---

## Résolution de problèmes

**L'email n'arrive pas**
- Vérifier que `GMAIL_APP_PASSWORD` est bien le code à 16 caractères (sans espaces)
- Vérifier le dossier Spam
- Dans l'onglet Actions de GitHub, cliquer sur le run → voir les logs de l'étape "Lancer extraction_50km.py"

**Le workflow ne se déclenche pas à 7h**
- GitHub peut avoir jusqu'à 30 min de délai sur les crons planifiés
- Les dépôts inactifs depuis 60 jours ont leur planification désactivée → ouvrir l'onglet Actions et réactiver

**Le script plante en cours de route**
- Le fichier Excel partiel est quand même sauvegardé comme artefact GitHub
- Voir les logs pour identifier quelle ville pose problème
- Le script reprend de zéro au prochain lancement

---

## Coût

- **GitHub Actions** : gratuit jusqu'à 2 000 minutes/mois (plan Free)
  - Le script tourne ~45–60 min/jour → ~1 500 min/mois → dans la limite gratuite
- **Gmail** : gratuit, aucune limite pour usage personnel

---
