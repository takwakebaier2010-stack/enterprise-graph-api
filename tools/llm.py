import os
import time
import requests
import urllib3.util.connection as _cn
_cn.HAS_IPV6 = False  # this network has no working IPv6

URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


def _models():
    first = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    backups = os.getenv("GEMINI_BACKUP_MODELS", "gemini-4-hydrogen").split(",")
    return [first] + [m.strip() for m in backups if m.strip() and m.strip() != first]


def ask_llm(system, user):
    provider = os.getenv("LLM_PROVIDER", "gemini")
    if provider == "anthropic":
        import anthropic
        msg = anthropic.Anthropic().messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=1000,
            system=system, messages=[{"role": "user", "content": user}])
        return msg.content[0].text
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is missing in .env")
    last = ""
    for model in _models():
        for attempt in range(1, 4):
            try:
                r = requests.post(
                    URL, headers={"Authorization": f"Bearer {key}"},
                    json={"model": model,
                          "messages": [{"role": "system", "content": system},
                                       {"role": "user", "content": user}]},
                    timeout=40)
            except requests.exceptions.RequestException as e:
                last = f"{model}: {type(e).__name__}"
                print(f"[{model}] {type(e).__name__}, retry {attempt}/3...")
                time.sleep(3 * attempt)
                continue
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            last = f"{model}: {r.status_code} {r.text[:200]}"
            if r.status_code in (429, 503):
                print(f"[{model}] busy ({r.status_code}), retry {attempt}/3...")
                time.sleep(5 * attempt)
                continue
            break
    raise SystemExit(f"LLM error, all models failed. Last: {last}")
