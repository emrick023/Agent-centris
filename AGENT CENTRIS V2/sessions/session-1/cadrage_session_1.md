# Session 1 - Cadrage et gabarit

## Objectif
Préparer un cadre d'extraction strict avant la collecte des annonces.

## Portée validée
- Source de départ: https://www.centris.ca/fr/plex~a-vendre~sherbrooke?q=H4sIAAAAAAAACl2MQQuCQBCF_8uePVTHbmEQEURkeBEPmz51aGpldq0W8b-3YgfxNt9735tePdmqrVqpSN3FPCCxKRGCwKaqqMAJfsLO4gBTi24bnzS6RditImXHMyV8AmZ5YGgpmrN-_r9UxA7yLysClzbV3I3rrJ-CYxnUWDvURnyYvMc-RFdYKvFypFkN0VxOwEyv-uZbzPxEMxbiRUwLcX5hXhjfhRmT83uyTqhwO-aZvN6oIR9-ZJ3voSoBAAA&sortSeed=507636527&sort=DateDesc&pageSize=20
- Couverture: 5 pages au total (page initiale + 4 pages suivantes)
- Type admissible: plex uniquement
- Localisation admissible: Sherbrooke et ses arrondissements uniquement

## Critères d'exclusion
- Annonces hors Sherbrooke/arrondissements
- Annonces qui ne sont pas des plex

## Champs à extraire (ordre final Excel)
1. Adresse
2. Prix
3. Année de construction
4. Superficie du terrain
5. Nombre d’unités
6. Unité résidentielle
7. Revenu brut potentiel
8. Évaluation municipale
9. Taxes
10. Dépenses

## Règles de qualité
- Ouvrir chaque annonce individuellement
- Valeurs numériques: chiffres bruts uniquement, sans symboles ni unités (pas de $, pc, mc, etc.)
  - Prix: entier brut (ex: 674900)
  - Année de construction: entier 4 chiffres (ex: 1961)
  - Superficie du terrain: entier brut (ex: 4500)
  - Nombre d'unités: entier brut uniquement (ex: 3, pas "Résidentiel (3)")
  - Revenu brut potentiel: entier brut (ex: 34320)
  - Évaluation municipale: entier brut (ex: 364300)
  - Taxes: entier brut (ex: 4363)
  - Dépenses: entier brut (ex: 4992)
- Adresse: texte tel qu'affiché (exception à la règle chiffres bruts)
- Unité résidentielle: description telle qu'affichée (ex: 1 x 3 ½, 2 x 5 ½)
- Si une donnée est absente: inscrire "Non indiqué"
- Ne rien estimer
- Une seule ligne par annonce (anti-doublon)

## Livrable préparé en Session 1
- Fichier gabarit Excel: `sessions/session-1/gabarit_extraction_immobilier.xlsx`
- Onglet principal: `Annonces admissibles`
- Onglet guide: `Règles`
- Statut: cadrage et gabarit terminés, extraction non démarrée
