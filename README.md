# API GraphQL – Gestion des événements et de la billetterie

## Projet 24 – Architecture d'API GraphQL fédérée et optimisation du problème N+1 avec DataLoader et Strawberry Django

Une API GraphQL développée avec Django, Strawberry et PostgreSQL pour la gestion des événements et de la billetterie.

Ce projet vise à démontrer la création d'une API GraphQL avec des entités liées, à identifier le problème des requêtes N+1 et à optimiser les accès à la base de données grâce à DataLoader et aux mécanismes d'optimisation de l'ORM Django.

## Table des matières

- [Présentation du projet](#présentation-du-projet)
- [Modèle métier](#modèle-métier)
- [Technologies utilisées](#technologies-utilisées)
- [Fonctionnalités](#fonctionnalités)
- [Structure du projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation et configuration](#installation-et-configuration)
- [Lancement de l'application](#lancement-de-lapplication)
- [Utilisation de l'API GraphQL](#utilisation-de-lapi-graphql)
- [Optimisation du problème N+1](#optimisation-du-problème-n1)
- [Tests automatisés et intégration continue](#tests-automatisés-et-intégration-continue)
- [Assistant GraphQL basé sur l'IA](#assistant-graphql-basé-sur-lia)
- [Équipe du projet](#équipe-du-projet)
- [Captures d'écran et démonstration](#captures-décran-et-démonstration)

## Présentation du projet

L'application repose sur un domaine de gestion des événements et de la billetterie. Elle permet d'étudier les requêtes GraphQL imbriquées et d'analyser les performances des accès à la base de données.

L'objectif principal est de comparer une implémentation GraphQL classique à une implémentation optimisée utilisant :

- DataLoader pour regrouper les accès aux données liées.
- Les mécanismes d'optimisation de l'ORM Django.
- La limitation de la profondeur des requêtes.
- La limitation du nombre d'alias.
- La pagination par curseur Relay.

Une requête imbriquée sur quatre niveaux permet d'illustrer le problème N+1 :

`organizers → events → reservations → tickets`

Le projet intègre également un assistant basé sur l'intelligence artificielle qui génère et valide des requêtes GraphQL à partir de questions formulées en langage naturel.

## Modèle métier

L'application repose sur six entités principales et leurs relations :

```text
Organizer ──< Event ──< Reservation ──< Ticket
               │             │
             Venue       Participant
```

| Modèle | Principaux attributs |
|---|---|
| Organizer | name, country |
| Venue | name, city, capacity |
| Participant | full_name, email |
| Event | organizer, venue, title, starts_at |
| Reservation | event, participant, status, created_at |
| Ticket | reservation, seat, price, checked_in |

## Technologies utilisées

- **Langage :** Python 3.10+
- **Backend :** Django
- **API GraphQL :** Strawberry GraphQL
- **Intégration Django :** strawberry-graphql-django
- **Base de données :** PostgreSQL
- **Optimisation :** DataLoader et ORM Django
- **Pagination :** Relay Cursor Pagination
- **Tests :** Pytest
- **Intégration continue :** GitHub Actions
- **Intelligence artificielle :** API Gemini

## Fonctionnalités

### API GraphQL

- Deux endpoints : une API classique et une API optimisée.
- Interface GraphiQL pour tester les requêtes.
- Requêtes sur les organisateurs, événements, lieux, participants, réservations et billets.
- Filtrage et tri des événements.
- Mutations pour créer des événements et des réservations.
- Pagination par curseur Relay pour les événements.

### Optimisation des requêtes N+1

- Illustration du problème N+1 à travers des requêtes imbriquées.
- Utilisation de DataLoaders propres à chaque requête pour regrouper les accès aux données.
- Optimisation des accès à la base de données avec l'ORM Django.
- Comparaison entre les schémas classique et optimisé.
- Mesure du nombre de requêtes SQL et du temps d'exécution.
- Vérification de l'équivalence des résultats retournés par les deux implémentations.

### Sécurité

- Profondeur maximale des requêtes : 5 niveaux.
- Nombre maximal d'alias : 10.
- Tests automatisés des limites de sécurité.

### Génération des données de test

Une commande permet de générer un jeu de données reproductible contenant :

- 5 organisateurs.
- 10 lieux.
- 200 participants.
- 50 événements.
- 1 000 réservations.
- Environ 2 000 billets.

Le jeu de données est déterministe afin de faciliter les tests et les comparaisons entre les environnements.

## Structure du projet

```text
enterprise-graph-api/
│
├── config/                         # Configuration Django et routes
│
├── core/
│   ├── models.py                   # Les six modèles métier
│   ├── schema.py                   # Schéma GraphQL classique
│   ├── schema_optimized.py         # Schéma GraphQL optimisé
│   ├── loaders.py                  # DataLoaders
│   └── management/
│       └── commands/
│           └── seed_data.py        # Génération des données de test
│
├── tools/
│   ├── ai_graphql_helper.py
│   └── export_schema.py
│
├── queries/                        # Exemples de requêtes GraphQL
├── tests/                          # Tests automatisés
├── docs/
│   └── screenshots/                # Captures d'écran
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── manage.py
├── Pipfile
├── Pipfile.lock
├── .env.example
├── .gitignore
└── README.md
```

*Cette structure présente les principaux composants du projet. Les noms et chemins doivent correspondre à ceux du dépôt réel.*

## Prérequis

- Python 3.10 ou supérieur.
- PostgreSQL installé et en cours d'exécution.
- Git.
- Pipenv.

## Installation et configuration

### 1. Cloner le dépôt

```bash
git clone https://github.com/takwakebaier2010-stack/enterprise-graph-api
cd enterprise-graph-api
```

Remplacer `[URL_DU_DEPOT]` par l'adresse réelle du dépôt GitHub.

### 2. Installer les dépendances

```bash
pip install pipenv
pipenv install
pipenv shell
```

### 3. Créer la base de données PostgreSQL

Ouvrir PostgreSQL et exécuter :

```sql
CREATE DATABASE enterprise_graph;
```

Si la base existe déjà, cette étape peut être ignorée.

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet en copiant le fichier `.env.example`.

Configurer les informations de connexion :

```env
DB_NAME=enterprise_graph
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe_postgresql
DB_HOST=localhost
DB_PORT=5432
```

Pour utiliser l'assistant IA, ajouter également la clé API Gemini :

```env
GEMINI_API_KEY=votre_cle_api_gemini
```

**Important :** le fichier `.env` contient des informations confidentielles. Il ne doit jamais être envoyé sur GitHub. Seul le fichier `.env.example` doit être partagé.

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Générer les données de test

```bash
python manage.py seed_data
```

Pour supprimer et régénérer les données :

```bash
python manage.py seed_data --clear
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

## Lancement de l'application

Une fois le serveur démarré, les deux endpoints sont accessibles :

| Endpoint | Description |
|---|---|
| [http://127.0.0.1:8000/graphql/](http://127.0.0.1:8000/graphql/) | API GraphQL classique |
| [http://127.0.0.1:8000/graphql-optimized/](http://127.0.0.1:8000/graphql-optimized/) | API GraphQL optimisée |

Les deux endpoints disposent d'une interface GraphiQL permettant d'explorer le schéma et d'exécuter des requêtes.

## Utilisation de l'API GraphQL

### Exemple de requête : récupérer les organisateurs

```graphql
{
  organizers {
    id
    name
    country
  }
}
```

### Exemple de requête imbriquée sur quatre niveaux

```graphql
{
  organizers {
    id
    name
    events {
      id
      title
      reservations {
        id
        status
        tickets {
          id
          seat
          price
        }
      }
    }
  }
}
```

Cette requête illustre les relations entre les organisateurs, les événements, les réservations et les billets. Elle permet notamment d'étudier le problème N+1.

## Optimisation du problème N+1

Le projet compare le schéma GraphQL classique au schéma optimisé en exécutant les mêmes requêtes.

Les critères étudiés sont :

- Le nombre de requêtes SQL exécutées.
- Le temps d'exécution.
- L'équivalence des données retournées.

L'optimisation repose sur la combinaison de DataLoaders propres à chaque requête et des mécanismes d'optimisation de l'ORM Django.

### Résultats des benchmarks

Voici quelques résultats obtenus lors des tests du projet :

| Scénario | Schéma classique | Schéma optimisé |
|---|---:|---:|
| Requête imbriquée sur 4 niveaux | 1 061 requêtes | 4 requêtes |
| Événements | 105 requêtes | 3 requêtes |
| Réservations | 3 010 requêtes | 4 requêtes |

Ces résultats correspondent au jeu de données et à l'exécution utilisés lors des mesures. Ils ne constituent pas des valeurs universelles pour toutes les tailles de données.

Le script de benchmark permet de comparer le nombre de requêtes SQL, le temps d'exécution et les résultats des deux implémentations.

## Tests automatisés et intégration continue

Pour exécuter les tests automatisés :

```bash
pipenv run pytest -v
```

Les tests couvrent notamment :

- Le blocage des requêtes dépassant la profondeur maximale autorisée.
- Le blocage des requêtes contenant plus de 10 alias.
- L'acceptation des requêtes respectant les limites configurées.
- Le nombre de requêtes SQL utilisées par DataLoader.
- La comparaison des résultats entre les schémas classique et optimisé.

Le workflow GitHub Actions exécute automatiquement les vérifications configurées lors des push et des Pull Requests.

Il comprend notamment la configuration de la base de données, l'application des migrations et l'exécution des tests.

## Assistant GraphQL basé sur l'IA

Le projet intègre un assistant en ligne de commande qui transforme des questions formulées en langage naturel en requêtes GraphQL, puis les valide par rapport au schéma de l'API avant leur utilisation.

Lorsqu'une requête est invalide, les erreurs de validation sont transmises au modèle afin qu'il puisse proposer une correction, avec un maximum de trois tentatives.

### Les trois niveaux de validation

1. **Validation syntaxique et structurelle :** vérifie l'existence des types, champs et arguments dans le schéma à l'aide de `graphql-core`.
2. **Limitation de profondeur :** impose une profondeur maximale de 5 niveaux.
3. **Limitation des alias :** impose un maximum de 10 alias.

### Dépendances supplémentaires

Installer les dépendances nécessaires si elles ne sont pas déjà présentes dans l'environnement :

```bash
pipenv install graphql-core requests python-dotenv
```

### Configuration de l'API Gemini

Créer une clé API Gemini depuis [Google AI Studio](https://aistudio.google.com/).

Ajouter la clé dans le fichier `.env` :

```env
GEMINI_API_KEY=votre_cle_api_gemini
```

Cette clé est nécessaire uniquement pour la fonctionnalité de génération avec `--ask`.

### Exportation du schéma GraphQL

```bash
python tools/export_schema.py > schema.graphql
```

### Génération d'une requête validée

```bash
python tools/ai_graphql_helper.py --schema-file schema.graphql --ask "Lister les 5 événements les plus récents avec le nom de leur lieu et de leur organisateur"
```

### Génération et exécution d'une requête

Démarrer d'abord le serveur Django, puis exécuter :

```bash
python tools/ai_graphql_helper.py --ask "Afficher chaque organisateur avec ses événements" --run
```

L'endpoint utilisé par défaut est :

`http://localhost:8000/graphql-optimized/`

### Validation des requêtes enregistrées

```bash
python tools/ai_graphql_helper.py --schema-file schema.graphql --validate-dir queries
```

Sans `--schema-file`, l'assistant peut récupérer le schéma directement depuis l'API grâce à l'introspection.

La variable `GRAPHQL_URL` permet de choisir un autre endpoint, par exemple :

```env
GRAPHQL_URL=http://localhost:8000/graphql/
```

La commande retourne un code de sortie non nul lorsqu'une requête est invalide.

### Exemples de requêtes

| Fichier | Objectif | Résultat attendu |
|---|---|---|
| `queries/events_deep.graphql` | Requête imbriquée sur quatre niveaux | Valide |
| `queries/events_filtered.graphql` | Filtrage et tri des événements | Valide |
| `queries/tickets_checkin.graphql` | Billets et informations des participants | Valide |
| `queries/bad_field.graphql` | Champs inexistants (`date`, `location`) | Rejetée |

### Limites de l'assistant IA

- La validation vérifie la structure de la requête, mais pas l'ensemble des règles métier.
- Par exemple, `orderBy` est un argument de type chaîne de caractères, mais le resolver accepte uniquement `starts_at`, `-starts_at`, `title` et `-title`.
- Une requête structurellement valide n'est pas nécessairement pertinente par rapport à la question posée.
- Le modèle ne peut pas récupérer des données qui ne sont pas exposées par le schéma GraphQL.
- La clé API Gemini doit rester confidentielle dans le fichier `.env`.

## Équipe du projet

| Membre | Responsabilité |
|---|---|
| KEBAIER TAKWA | Backend Django et PostgreSQL |
| BEN HAMOUDA FATMA | GraphQL et Strawberry |
| ALMIA NOUR | DataLoader et optimisation |
| FEKI AYA | Sécurité, tests et intégration continue |
| HSSAN TASSNIM | Assistant GraphQL basé sur l'IA, validation des requêtes, README et démonstration |

## Captures d'écran et démonstration

Les captures d'écran illustrant l'application et ses principales fonctionnalités sont disponibles dans :

`docs/screenshots/`

Elles peuvent notamment présenter :

- Les interfaces GraphiQL classique et optimisée.
- Les requêtes GraphQL imbriquées.
- Le filtrage et la pagination des événements.
- L'optimisation avec DataLoader.
- Les résultats des benchmarks.
- L'exécution de l'assistant GraphQL basé sur l'IA.


## Conclusion

Ce projet met en pratique la conception d'une API GraphQL avec Django et Strawberry, en mettant l'accent sur l'optimisation des accès aux données, la résolution du problème N+1, la pagination, la sécurité, les tests automatisés et la génération de requêtes assistée par l'intelligence artificielle.

Il rassemble des notions de développement backend, de gestion de bases de données, d'architecture GraphQL, d'analyse des performances et d'intégration continue dans une application concrète de gestion des événements et de la billetterie.