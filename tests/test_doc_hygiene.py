"""Stdlib unit and adversarial regression tests for White Rabbit documentation hygiene."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_docs import (  # noqa: E402
    audit_repo_docs,
    check_markdown_links,
    check_undefined_acronyms,
)


class TestDocHygiene(unittest.TestCase):
    """Enforce UNSLOP DOC-001..003, LAN-003, and LAN-009 on White Rabbit docs."""

    def test_live_repository_docs_pass_hygiene_gate(self) -> None:
        errors, _ = audit_repo_docs(REPO_ROOT)
        self.assertEqual(errors, [], f"Live repository documentation failed audit:\n" + "\n".join(errors))

    def test_adversarial_mutations_fail_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()

            valid_readme = (
                "# Sample Project\n\n"
                "## TL;DR\n\n"
                "Takes a target query and checks source pages. See [Guide](docs/guide.md#workflow).\n"
            )
            (root / "README.md").write_text(valid_readme, encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Agent Rules\n\nRun documentation checks before commit.\n",
                encoding="utf-8",
            )
            (root / "docs" / "guide.md").write_text(
                "# Guide\n\n## Workflow\n\nProvide a target query and verify exported evidence rows.\n",
                encoding="utf-8",
            )

            base_errors, _ = audit_repo_docs(root)
            self.assertEqual(base_errors, [])

            # 1. UTF-8 BOM in README.md fails DOC-001:TLDR
            (root / "README.md").write_bytes(b"\xef\xbb\xbf" + valid_readme.encode("utf-8"))
            bom_errors, _ = audit_repo_docs(root)
            self.assertTrue(any("DOC-001:TLDR" in e and "BOM" in e for e in bom_errors), bom_errors)

            # 2. Missing TL;DR fails DOC-001:TLDR
            (root / "README.md").write_text("# Sample Project\n\nNo summary section here.\n", encoding="utf-8")
            no_tldr_errors, _ = audit_repo_docs(root)
            self.assertTrue(any("DOC-001:TLDR" in e for e in no_tldr_errors), no_tldr_errors)

            # 3. Oversized (>60-word) TL;DR and >45-word run-on sentence fail DOC-001:TLDR and DOC-002:RUNON
            runon_tldr = " ".join(["plain"] * 64) + "."
            (root / "README.md").write_text(f"# Sample Project\n\n## TL;DR\n\n{runon_tldr}\n", encoding="utf-8")
            long_errors, _ = audit_repo_docs(root)
            self.assertTrue(any("DOC-001:TLDR" in e for e in long_errors), long_errors)
            self.assertTrue(any("DOC-002:RUNON" in e for e in long_errors), long_errors)

            # Restore clean README.md
            (root / "README.md").write_text(valid_readme, encoding="utf-8")

            # 4. Banned jargon, undefined acronym, >45-word prose sentence, file:// link, and broken links/anchors fail
            forty_eight_words = " ".join(["clear"] * 48) + "."
            (root / "docs" / "guide.md").write_text(
                "# Guide\n\n## Workflow\n\n"
                "We leverage XYZQ and/or update buckets as appropriate. "
                f"{forty_eight_words} "
                "See [Local](file:///tmp/local.md), [Missing](missing.md), and [Bad Anchor](../README.md#missing-anchor).\n",
                encoding="utf-8",
            )
            slop_errors, _ = audit_repo_docs(root)
            self.assertTrue(any("LAN-009:JARGON" in e and "'leverage'" in e for e in slop_errors), slop_errors)
            self.assertTrue(any("LAN-009:JARGON" in e and "'and/or'" in e for e in slop_errors), slop_errors)
            self.assertTrue(any("LAN-003:ACRONYM" in e and "'XYZQ'" in e for e in slop_errors), slop_errors)
            self.assertTrue(any("DOC-002:RUNON" in e for e in slop_errors), slop_errors)
            self.assertTrue(any("DOC-003:LINK" in e and "file://" in e for e in slop_errors), slop_errors)
            self.assertTrue(any("DOC-003:LINK" in e and "missing.md" in e for e in slop_errors), slop_errors)
            self.assertTrue(any("DOC-003:LINK" in e and "#missing-anchor" in e for e in slop_errors), slop_errors)

            # 5. Expanded acronym passes LAN-003:ACRONYM
            self.assertEqual(
                check_undefined_acronyms("Define Example Quality Metric (XYZQ) before reusing XYZQ."),
                [],
            )

            # 6. Escaping repo root link fails DOC-003:LINK
            escape_errors = check_markdown_links(
                "See [Outside](../../outside.md).",
                source_file=root / "README.md",
                repo_root=root,
            )
            self.assertTrue(any("DOC-003:LINK" in e and "escapes repository root" in e for e in escape_errors), escape_errors)


if __name__ == "__main__":
    unittest.main()
