"""Nine pre-send QA checks that run every time, for humans and agents alike.

Each check is deterministic and maps to a delivery best practice in Adobe Campaign's
own guidance (proofs, opt-out link, subject length, seeds, typologies). No AI involved.
Standard library only. Synthetic deliveries only.
"""
import json
import re
import sys

ENGLISH_PRICE = re.compile(r"€\s?\d{1,3}(,\d{3})*\.\d{2}")
LOCAL_PRICE = re.compile(r"\d{1,3}(\.\d{3})*,\d{2}\s?€")
MARKET_RULES = {
    # local quiet hours (send window) and whether English price formatting is acceptable
    "default": {"window": ("08:00", "21:00"), "english_price_ok": False},
    "IE": {"window": ("08:00", "21:00"), "english_price_ok": True},
}


def rules_for(market):
    return MARKET_RULES.get(market, MARKET_RULES["default"])


def check_unsubscribe(d):
    ok = bool(re.search(r'href="[^"]*unsubscribe[^"]*"', d["html"], re.I))
    return ok, "unsubscribe link present" if ok else "no unsubscribe link"


def check_legal_footer(d):
    ok = 'id="legal-footer"' in d["html"]
    return ok, "legal footer present" if ok else "no market legal footer"


def check_price_locale(d):
    r = rules_for(d["market"])
    if ENGLISH_PRICE.search(d["html"]) and not r["english_price_ok"]:
        return False, "English price format in a local-format market"
    return True, "price format matches market"


def check_consent(d):
    ok = "marketing_optin" in d.get("audience_filters", [])
    return ok, "consent filter applied" if ok else "no marketing-consent filter"


def check_proof(d):
    ok = bool(d.get("proof_approved_by"))
    return ok, "proof signed off" if ok else "no proof sign-off"


def check_quiet_hours(d):
    start, end = rules_for(d["market"])["window"]
    t = d["send_local_time"]
    ok = start <= t <= end
    return ok, f"sends at {t} local" if ok else f"{t} local is outside {start}-{end}"


def check_typology(d):
    ok = d.get("typology") not in (None, "", "none")
    return ok, "typology set" if ok else "no marketing typology"


def check_seeds(d):
    ok = len(d.get("seed_list", [])) > 0
    return ok, "seed list present" if ok else "no seed addresses"


def check_subject(d):
    n = len(d["subject"])
    return n <= 50, f"subject {n} chars" + ("" if n <= 50 else " (over 50: warning)")


CHECKS = [("unsubscribe", check_unsubscribe, "error"), ("legal_footer", check_legal_footer, "error"),
          ("price_locale", check_price_locale, "error"), ("consent", check_consent, "error"),
          ("proof", check_proof, "error"), ("quiet_hours", check_quiet_hours, "error"),
          ("typology", check_typology, "error"), ("seeds", check_seeds, "error"),
          ("subject_length", check_subject, "warning")]


def run(delivery):
    results = []
    for name, fn, level in CHECKS:
        ok, msg = fn(delivery)
        results.append({"check": name, "ok": ok, "level": level, "message": msg})
    blocking = [r for r in results if not r["ok"] and r["level"] == "error"]
    return {"delivery": delivery["id"], "market": delivery["market"],
            "verdict": "BLOCK" if blocking else "PASS", "results": results}


def main(path):
    with open(path, encoding="utf-8") as fh:
        deliveries = json.load(fh)
    exit_code = 0
    for d in deliveries:
        r = run(d)
        fails = [x["message"] for x in r["results"] if not x["ok"]]
        print(f"{r['market']}  {r['delivery']:<10} {r['verdict']:<5} " + ("; ".join(fails) or "all 9 checks passed"))
        exit_code |= r["verdict"] == "BLOCK"
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "examples/deliveries.json"))
