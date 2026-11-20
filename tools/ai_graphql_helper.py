"""AI GraphQL helper: natural language -> GraphQL query validated against the schema."""
import argparse, glob, json, os, sys
import requests
from graphql import (build_client_schema, build_schema, get_introspection_query,
                     parse, validate, print_schema, GraphQLError)
from graphql.language import (FieldNode, InlineFragmentNode, FragmentSpreadNode,
                              FragmentDefinitionNode, OperationDefinitionNode)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ENDPOINT = os.getenv("GRAPHQL_URL", "http://localhost:8000/graphql-optimized/")
MAX_DEPTH = 5      # same as QueryDepthLimiter in core/schema_optimized.py
MAX_ALIASES = 10   # same as MaxAliasesLimiter


def load_schema(path=None):
    if path:  # offline mode (CI): schema.graphql
        with open(path, encoding="utf-8") as f:
            return build_schema(f.read())
    r = requests.post(ENDPOINT, json={"query": get_introspection_query()}, timeout=30)
    r.raise_for_status()
    return build_client_schema(r.json()["data"])  # live introspection


def _depth(node, frags, d=0):
    sel = getattr(node, "selection_set", None)
    if not sel:
        return d
    best = d
    for s in sel.selections:
        if isinstance(s, FieldNode):
            if s.name.value.startswith("__"):
                continue
            best = max(best, _depth(s, frags, d + 1))
        elif isinstance(s, InlineFragmentNode):
            best = max(best, _depth(s, frags, d))
        elif isinstance(s, FragmentSpreadNode) and s.name.value in frags:
            best = max(best, _depth(frags[s.name.value], frags, d))
    return best


def _aliases(doc):
    count = 0
    stack = list(doc.definitions)
    while stack:
        n = stack.pop()
        if isinstance(n, FieldNode) and n.alias:
            count += 1
        sel = getattr(n, "selection_set", None)
        if sel:
            stack.extend(sel.selections)
    return count


def check(schema, query):
    """Return a list of errors: syntax, schema validation, depth and alias limits."""
    try:
        doc = parse(query)
    except GraphQLError as e:
        return [f"Syntax: {e.message}"]
    errors = [e.message for e in validate(schema, doc)]
    frags = {d.name.value: d for d in doc.definitions if isinstance(d, FragmentDefinitionNode)}
    for d in doc.definitions:
        if isinstance(d, OperationDefinitionNode):
            depth = _depth(d, frags)
            if depth > MAX_DEPTH:
                errors.append(f"Depth {depth} exceeds the server limit ({MAX_DEPTH})")
    n = _aliases(doc)
    if n > MAX_ALIASES:
        errors.append(f"{n} aliases exceed the server limit ({MAX_ALIASES})")
    return errors


def clean(text):
    t = text.strip()
    for prefix in ("```graphql", "```"):
        if t.startswith(prefix):
            t = t[len(prefix):]
    return t.removesuffix("```").strip()


def generate(schema, question, retries=3):
    import anthropic
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    sdl, feedback = print_schema(schema), ""
    system = (
        "You write exactly ONE GraphQL query. No markdown, no explanation.\n"
        "Use only types and fields from this schema.\n"
        f"Maximum nesting depth: {MAX_DEPTH}. Maximum aliases: {MAX_ALIASES}.\n"
        "Fields are camelCase (startsAt, fullName, checkedIn, organizerId, orderBy).\n"
        "The orderBy argument only accepts these exact values: starts_at, -starts_at, title, -title.\n\n" + sdl
    )
    errors = []
    for attempt in range(1, retries + 1):
        msg = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=1000,
            system=system, messages=[{"role": "user", "content": question + feedback}])
        q = clean(msg.content[0].text)
        errors = check(schema, q)
        print(f"[attempt {attempt}] {'VALID' if not errors else 'INVALID'}", file=sys.stderr)
        for e in errors:
            print("   -", e, file=sys.stderr)
        if not errors:
            return q
        feedback = ("\n\nYour previous query was invalid:\n" + q + "\nErrors:\n"
                    + "\n".join(errors) + "\nFix it and return only the query.")
    raise SystemExit(f"No valid query produced: {errors}")


def execute(query):
    r = requests.post(ENDPOINT, json={"query": query}, timeout=60)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="AI GraphQL helper validated by the schema")
    ap.add_argument("--ask", help="question in natural language")
    ap.add_argument("--schema-file", help="schema.graphql (otherwise live introspection)")
    ap.add_argument("--validate-dir", help="folder of .graphql queries to validate")
    ap.add_argument("--run", action="store_true", help="execute the generated query")
    a = ap.parse_args()

    schema = load_schema(a.schema_file)
    if a.ask:
        q = generate(schema, a.ask)
        print(q)
        if a.run:
            execute(q)
    if a.validate_dir:
        bad = 0
        for f in sorted(glob.glob(os.path.join(a.validate_dir, "*.graphql"))):
            with open(f, encoding="utf-8") as fh:
                errs = check(schema, fh.read())
            print(("FAIL " if errs else "OK   ") + f)
            for e in errs:
                print("     -", e)
            bad += bool(errs)
        sys.exit(1 if bad else 0)
