# Events & Ticketing GraphQL API

Group project: **Project 24 – Federated GraphQL API Architecture & DataLoader N+1 Optimization with Strawberry Django**

A GraphQL API built with Django, Strawberry and PostgreSQL for an events and ticketing domain. The project shows the N+1 query problem and how DataLoader fixes it.

## Domain model

```
Organizer ──< Event ──< Reservation ──< Ticket
               │            │
             Venue      Participant
```

| Model | Main fields |
|---|---|
| Organizer | name, country |
| Venue | name, city, capacity |
| Participant | full_name, email |
| Event | organizer, venue, title, starts_at |
| Reservation | event, participant, status, created_at |
| Ticket | reservation, seat, price, checked_in |

The deepest query follows four levels: `organizers → events → reservations → tickets`.

## Tech stack

- Python 3.10+
- Django
- Strawberry GraphQL + strawberry-graphql-django
- PostgreSQL

## Prerequisites

- Python 3.10 or higher
- PostgreSQL installed and running
- Git

## Installation

1. Clone the repository

```bash
git clone [REPOSITORY_URL]
cd [REPOSITORY_FOLDER]
```

2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Create the PostgreSQL database

```sql
CREATE DATABASE enterprise_graph;
```

5. Configure the environment

Copy `.env.example` to `.env` and set your own PostgreSQL password:

```
DB_NAME=enterprise_graph
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

6. Apply the migrations

```bash
python manage.py migrate
```

7. Load the test data

```bash
python manage.py seed_data
```

This creates 5 organizers, 10 venues, 200 participants, 50 events, 1000 reservations and about 2000 tickets. The data is the same on every machine. Use `python manage.py seed_data --clear` to reset it.

8. Start the server

```bash
python manage.py runserver
```

## Usage

Open http://127.0.0.1:8000/graphql/ to use the GraphiQL interface.

Example query:

```graphql
{
  organizers {
    id
    name
    country
  }
}
```

## Project structure

```
config/                  Django settings and URLs
core/
  models.py              The 6 models
  schema.py              GraphQL schema (Strawberry)
  management/commands/
    seed_data.py         Test data generator
manage.py
requirements.txt
.env.example
```

## Features

- [x] PostgreSQL database with 6 related models
- [x] Test data generator
- [x] GraphQL endpoint with GraphiQL
- [ ] [Queries, mutations, filters, pagination]
- [ ] [DataLoader and N+1 optimization]
- [x] GraphQL query depth and alias limits
- [x] Automated security tests with Pytest
- [x] GitHub Actions CI workflow
- [x] AI GraphQL helper (natural language to validated GraphQL queries)

(Each member updates the line of their own part.)

## Team

| Member | Responsibility |
|---|---|
| [KEBAIER TAKWA ] | Backend Django & PostgreSQL |
| [BEN HAMOUDA FATMA] | GraphQL & Strawberry |
| [ALMIA NOUR] | DataLoader & optimization |
| [FEKI AYA] | Security, tests & CI |
| [HSSAN TASSNIM] | AI GraphQL helper, query validation, README and demo |

## Running the tests

Run the automated security tests with:

```bash
pipenv run pytest -v
```

The tests verify:
- Deep GraphQL queries are blocked.
- Queries with more than 10 aliases are blocked.
- Normal GraphQL queries are accepted.

GitHub Actions automatically runs the tests on every push and pull request.

## AI GraphQL helper

A command-line assistant that turns a question in natural language into a GraphQL query and **validates it against the schema before it is used**. If the query is invalid, the errors are sent back to the model, which corrects itself (up to 3 attempts).

The validation has three layers:

1. **Syntax and schema**: every type, field and argument must exist in the schema (`graphql-core`).
2. **Depth limit**: maximum depth of 5, the same as `QueryDepthLimiter` in `core/schema_optimized.py`.
3. **Alias limit**: maximum 10 aliases, the same as `MaxAliasesLimiter`.

### Setup

```bash
pip install graphql-core requests python-dotenv
```

Add a free Gemini API key from Google AI Studio (aistudio.google.com) to `.env` (never commit it). The key is only needed for `--ask`. Use `>>` so the database lines stay:

```bash
echo "GEMINI_API_KEY=your_key_here" >> .env
```

Export the schema (needed for offline validation):

```bash
python tools/export_schema.py > schema.graphql
```

### Usage

Generate a validated query from a question:

```bash
python tools/ai_graphql_helper.py --schema-file schema.graphql --ask "List the 5 latest events with their venue name and organizer name"
```

Generate and execute it on the running server (default: `http://localhost:8000/graphql-optimized/`):

```bash
python tools/ai_graphql_helper.py --ask "Show each organizer with their events" --run
```

Validate saved queries (exit code 1 if one is invalid, so CI can use it):

```bash
python tools/ai_graphql_helper.py --schema-file schema.graphql --validate-dir queries
```

Without `--schema-file`, the schema is loaded by live introspection. Set `GRAPHQL_URL` to use another endpoint, for example the naive one (`/graphql/`).

### Example queries

| File | Purpose | Expected |
|---|---|---|
| `queries/events_deep.graphql` | 4-level nested query | valid |
| `queries/events_filtered.graphql` | filters and ordering | valid |
| `queries/tickets_checkin.graphql` | tickets with participant | valid |
| `queries/bad_field.graphql` | non-existent fields (`date`, `location`) | rejected |

### Screenshots and demo

Screenshots are in `docs/screenshots/`. Demo video: [add the link here]

### Limits

- The validation checks the **structure** of a query, not business rules. For example, `orderBy` is a plain `String` in the schema, but the resolver only accepts `starts_at`, `-starts_at`, `title` and `-title`. These values are given to the model in the prompt, and `--run` shows runtime errors.
- A valid query is not always a relevant one: check the result against your question.
- The model cannot produce data that the schema does not expose (for example, computed counts).
- The API key must stay in `.env`, which is ignored by Git.