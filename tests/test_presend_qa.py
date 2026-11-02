import json
import unittest

from presend_qa import run

with open("examples/deliveries.json", encoding="utf-8") as fh:
    D = {d["market"]: d for d in json.load(fh)}


def failed(market):
    return {r["check"] for r in run(D[market])["results"] if not r["ok"]}


class PresendQaTest(unittest.TestCase):
    def test_clean_delivery_passes(self):
        self.assertEqual(run(D["HR"])["verdict"], "PASS")

    def test_si_missing_unsubscribe(self):
        self.assertEqual(failed("SI"), {"unsubscribe"})

    def test_at_missing_proof(self):
        self.assertEqual(failed("AT"), {"proof"})

    def test_gr_price_and_quiet_hours(self):
        self.assertEqual(failed("GR"), {"price_locale", "quiet_hours"})

    def test_hu_consent_and_subject_warning(self):
        self.assertEqual(failed("HU"), {"consent", "subject_length"})
        self.assertEqual(run(D["HU"])["verdict"], "BLOCK")

    def test_warning_alone_does_not_block(self):
        d = dict(D["HR"], subject="x" * 60)
        self.assertEqual(run(d)["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
