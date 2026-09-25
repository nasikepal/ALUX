"""
Honesty guardrails for the Production OS pipeline.

Runs the full pipeline with the network disabled (every provider returns nothing) and checks that
the output never invents what it did not find: no fabricated source notes, no "verified" claims,
no assets with made-up resolution/license, no placeholder media treated as real files.

Run from the vault root:
    .venv/bin/python -m unittest discover -s 08_AUTOMATION/tests -v
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent / "Scripts"
sys.path.insert(0, str(SCRIPTS))

import requests  # noqa: E402

from core.config import config, Config, RelevanceWeights  # noqa: E402

SCRIPT = """---
title: Honesty Test
project: Test
---
# Honesty Test

## Hook
Billionaires quietly move 4 billion dollars into physical real estate while the market sleeps.

## Body
Studies show 72 percent of wealthy families never chase trends and buy privacy instead.
"""


def _no_network(*args, **kwargs):
    raise requests.ConnectionError("network disabled in tests")


class OfflinePipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="alux-test-"))
        # Point every output directory at a throwaway vault.
        cls.patches = [
            mock.patch.object(config, attr, cls.tmp / getattr(config, attr).relative_to(config.vault_root))
            for attr in ("sources_dir", "research_inbox_dir", "shots_dir", "scripts_dir")
        ]
        cls.patches.append(mock.patch("requests.get", _no_network))
        for p in cls.patches:
            p.start()

        # Placeholder media like the upstream 04_MEDIA files: right names, zero bytes.
        media = cls.tmp / "media"
        (media / "SFX").mkdir(parents=True)
        (media / "Footage").mkdir(parents=True)
        (media / "SFX" / "Studio_Sub_Bass_Boom_Impact.wav").write_bytes(b"")
        (media / "Footage" / "Studio_Penthouse_City_Skyline_4K.mp4").write_bytes(b"x" * 24)

        from providers.local_media import local_media_provider
        cls.index_patch = mock.patch.object(local_media_provider, "index_path", cls.tmp / "index.json")
        cls.index_patch.start()
        cls.indexed_count = local_media_provider.build_index([media])

        script_path = cls.tmp / "02_SCRIPTS" / "Draft" / "Honesty Test.md"
        script_path.parent.mkdir(parents=True)
        script_path.write_text(SCRIPT, encoding="utf-8")
        cls.script_path = script_path

        import cli
        cls.cli = cli
        cls.cli.run_pipeline(script_path)

    @classmethod
    def tearDownClass(cls):
        cls.index_patch.stop()
        for p in cls.patches:
            p.stop()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _all_output_text(self) -> str:
        return "\n".join(p.read_text(encoding="utf-8") for p in self.tmp.rglob("*.md")) + "\n".join(
            p.read_text(encoding="utf-8-sig") for p in self.tmp.rglob("*.csv"))

    def test_placeholder_media_not_indexed(self):
        self.assertEqual(self.indexed_count, 0)

    def test_no_source_notes_without_real_sources(self):
        sources = list((self.tmp / "06_SOURCES").rglob("*.md")) if (self.tmp / "06_SOURCES").exists() else []
        self.assertEqual(sources, [], "source notes were written although no search returned anything")

    def test_unsourced_claims_get_inbox_cards_with_leads(self):
        cards = list((self.tmp / "03_RESEARCH" / "_INBOX").glob("*NO SOURCE FOUND.md"))
        self.assertGreater(len(cards), 0)
        text = cards[0].read_text(encoding="utf-8")
        self.assertIn("verification_status: unverified", text)
        self.assertIn("not sources", text)

    def test_no_fabricated_publishers_or_verification(self):
        text = self._all_output_text()
        for fake in ["The Lancet", "New England Journal", "Cell Metabolism", "Verified & Linked",
                     "Verified Citations", "Verified enterprise disclosure", "4K UHD (3840x2160)",
                     "Commercial / Royalty-Free", "CC0 / Royalty Free", "Royalty-Free / CC"]:
            self.assertNotIn(fake, text, f"fabricated label found in output: {fake!r}")

    def test_script_status_is_honest(self):
        text = self.script_path.read_text(encoding="utf-8")
        self.assertIn("broll_status: needs_sourcing", text)
        self.assertIn("research_status: needs_research", text)
        self.assertNotIn("completed", text.split("---")[1])
        self.assertIn("NO ASSET FOUND", text)
        self.assertIn("No source found", text)

    def test_cut_list_flags_missing_assets(self):
        csv_files = list(self.tmp.rglob("*_CutList.csv"))
        self.assertEqual(len(csv_files), 1)
        text = csv_files[0].read_text(encoding="utf-8-sig")
        self.assertIn("Broll_Status", text)
        self.assertIn("NO ASSET - search link", text)


class SourceScoringTest(unittest.TestCase):
    def test_match_score_has_no_floor_and_reputation_is_separate(self):
        from scoring.relevance import RelevanceEngine
        score, cred = RelevanceEngine().score_source_fact(
            {"publisher": "Reuters", "title": "Weather in Oslo", "excerpt": "Rain expected"},
            "Billionaires move 4 billion into real estate")
        self.assertEqual(score, 0.0)
        self.assertEqual(cred, "high")

    def test_medium_publishers_are_not_upgraded(self):
        from scoring.relevance import RelevanceEngine
        _, cred = RelevanceEngine().score_source_fact({"publisher": "Forbes", "title": ""}, "x")
        self.assertEqual(cred, "medium")


class SettingsLoadingTest(unittest.TestCase):
    def test_settings_weights_are_applied(self):
        with tempfile.TemporaryDirectory() as d:
            system = Path(d)
            (system / "Settings.md").write_text(
                "---\nwords_per_second: 2.1\nweights:\n  semantic_relevance: 0.30\n  narrative_function: 0.05\n"
                "  visual_specificity: 0.15\n  artistic_interpretation: 0.15\n  cinematic_compatibility: 0.10\n"
                "  temporal_relevance: 0.10\n  geographic_relevance: 0.05\n  editorial_utility: 0.05\n"
                "  source_quality: 0.05\n---\n", encoding="utf-8")
            c = Config()
            c.system_dir = system
            c.load_from_settings()
            self.assertAlmostEqual(c.weights.semantic_relevance, 0.30)
            self.assertAlmostEqual(c.words_per_second, 2.1)

    def test_invalid_weight_sum_keeps_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            system = Path(d)
            (system / "Settings.md").write_text("---\nweights:\n  semantic_relevance: 0.9\n---\n", encoding="utf-8")
            c = Config()
            c.system_dir = system
            c.load_from_settings()
            self.assertEqual(c.weights, RelevanceWeights())


if __name__ == "__main__":
    unittest.main()
