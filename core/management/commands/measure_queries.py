import asyncio
import json
import logging
import time

from django.core.management.base import BaseCommand

from core.loaders import make_loaders
from core.schema import schema
from core.schema_optimized import schema_optimized

PRESETS = {
    "nested4": """{ organizers { name events { title reservations {
                    status tickets { seat price } } } } }""",
    "events": """{ events(orderBy: "-starts_at") {
                    title organizer { name } venue { name city } } }""",
    "reservations": """{ reservations { status event { title }
                    participant { fullName } tickets { seat price } } }""",
    "tickets": """{ tickets { seat reservation { status event { title } } } }""",
}


class SqlCounter(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.count = 0

    def emit(self, record):
        self.count += 1


def canon(x):
    """Trie récursivement les listes : on compare le contenu, pas l'ordre SQL."""
    if isinstance(x, dict):
        return {k: canon(v) for k, v in sorted(x.items())}
    if isinstance(x, list):
        return sorted((canon(i) for i in x), key=lambda i: json.dumps(i, sort_keys=True))
    return x


def run(label, fn):
    logger = logging.getLogger("django.db.backends")
    counter, old = SqlCounter(), logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(counter)
    t0 = time.perf_counter()
    try:
        result = fn()
    finally:
        elapsed = time.perf_counter() - t0
        logger.removeHandler(counter)
        logger.setLevel(old)
    if result.errors:
        raise RuntimeError(f"{label}: {result.errors}")
    return counter.count, elapsed, result.data


class Command(BaseCommand):
    help = "Compare le nombre de requêtes SQL avant/après DataLoader."

    def add_arguments(self, parser):
        parser.add_argument("--preset", choices=PRESETS, help="Une seule requête prédéfinie")
        parser.add_argument("--query", help="Requête GraphQL personnalisée")

    def handle(self, *args, **opts):
        if opts["query"]:
            queries = {"custom": opts["query"]}
        elif opts["preset"]:
            queries = {opts["preset"]: PRESETS[opts["preset"]]}
        else:
            queries = PRESETS

        for name, q in queries.items():
            n1, t1, d1 = run("AVANT", lambda: schema.execute_sync(q))
            n2, t2, d2 = run(
                "APRÈS",
                lambda: asyncio.run(
                    schema_optimized.execute(q, context_value={"loaders": make_loaders()})
                ),
            )
            same = canon(d1) == canon(d2)
            self.stdout.write(f"\n== {name} ==")
            self.stdout.write(f"  AVANT : {n1:>5} requêtes, {t1*1000:8.1f} ms")
            self.stdout.write(f"  APRÈS : {n2:>5} requêtes, {t2*1000:8.1f} ms")
            self.stdout.write(
                self.style.SUCCESS("  Résultats identiques ✔") if same
                else self.style.ERROR("  Résultats DIFFÉRENTS ✘")
            )