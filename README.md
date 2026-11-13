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
- Pipenv (`pip install --user pipenv`)

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

2. Install pipenv

```bash
pip install --user pipenv
```

3. Install the dependencies and open the virtual environment

```bash
pipenv install
pipenv shell
```

`pipenv install` reads `Pipfile.lock`, so everyone gets the same package versions. Run the next commands inside `pipenv shell` (or put `pipenv run` before each command).

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
Pipfile
Pipfile.lock
requirements.txt
.env.example
```

## Features

- [x] PostgreSQL database with 6 related models
- [x] Test data generator
- [x] GraphQL endpoint with GraphiQL
- [ ] [Queries, mutations, filters, pagination]
- [ ] [DataLoader and N+1 optimization]
- [ ] [Query depth and alias limits]
- [ ] [Automated tests and CI]
- [ ] [AI GraphQL helper]

(Each member updates the line of their own part.)

## Team

| Member | Responsibility |
|---|---|
| [KEBAIER TAKWA ] | Backend Django & PostgreSQL |
| [BEN HAMOUDA FATMA] | GraphQL & Strawberry |
| [ALMIA NOUR] | DataLoader & optimization |
| [FEKI AYA] | Security, tests & CI |
| [HSSAN TASSNIM] | [Responsibility] |

## Running the tests

[To be completed by the member in charge of tests.]
