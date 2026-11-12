#!/usr/bin/env python3
"""Zero-dependency stdlib documentation hygiene gate (UNSLOP DOC-001..003, LAN-003, LAN-009)."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parent.parent

ADVISORY_PUBLIC_FK_GRADE: float = 8.0
ADVISORY_SENTENCE_WORDS: int = 30
MAX_REPO_DOC_SENTENCE_WORDS: int = 45
MAX_README_TLDR_WORDS: int = 60

HUMAN_FACING_DOC_GLOBS: tuple[str, ...] = (
    "README.md",
    "DESIGN.md",
    "TESTING.md",
    "docs/*.md",
    "apps/*/README.md",
    "packages/*/README.md",
)

OPERATIONAL_DOC_GLOBS: tuple[str, ...] = (
    "AGENTS.md",
    "STATUS.md",
    "GEMINI.md",
    "apps/web/AGENTS.md",
    "apps/web/CLAUDE.md",
)

BANNED_JARGON_AND_FILLER: dict[str, str] = {
    "and/or": "state 'A or B' or 'A, B, or both'",
    "as appropriate": "state the exact condition",
    "if applicable": "state the exact condition",
    "etc.": "list all required items or state the exact category",
    "leverage": "use 'use'",
    "utilize": "use 'use'",
    "synergy": "state the specific interaction",
    "hopefully": "state the expected result or verification check",
    "more or less": "give the exact range or tolerance",
    "could possibly": "use 'can' or state the condition",
    "delve": "state the specific analysis action",
    "delve into": "use 'examine' or 'analyze'",
    "tapestry": "use literal domain nouns",
    "testament to": "state the concrete evidence directly",
    "it is important to note": "delete throat-clearing filler and state the point",
    "in today's fast-paced": "delete generic AI preamble",
    "paradigm shift": "describe the specific architectural or methodological change",
    "holistic approach": "name the concrete dimensions covered",
    "seamless integration": "specify the interface contract",
    "game-changer": "state the measurable effect",
    "cutting-edge": "state the specific technical capability",
}

COMMON_ACRONYMS_ALLOWLIST: frozenset[str] = frozenset(
    {
        "API",
        "ASCII",
        "CLI",
        "CMS",
        "CPU",
        "CSS",
        "CSV",
        "DAG",
        "DNS",
        "DOCX",
        "DOM",
        "DPI",
        "FAQ",
        "GIT",
        "GPU",
        "GUI",
        "HTML",
        "HTTP",
        "HTTPS",
        "IDE",
        "IEC",
        "IETF",
        "ISBN",
        "ISO",
        "JSON",
        "JUNIT",
        "JWT",
        "LLM",
        "MAC",
        "MIT",
        "NIST",
        "OCR",
        "PDF",
        "PNG",
        "RAM",
        "REST",
        "RFC",
        "RGB",
        "SDK",
        "SHA",
        "SLO",
        "SOP",
        "SQL",
        "SSH",
        "SSL",
        "SVG",
        "TCP",
        "TLS",
        "TOML",
        "TSV",
        "UDP",
        "URI",
        "URL",
        "USA",
        "USB",
        "USD",
        "UTC",
        "UTF",
        "UUID",
        "WCAG",
        "WWW",
        "XML",
        "XSS",
        "YAML",
        "ZIP",
        "AGENTS",
        "BLOCKER",
        "DEMO",
        "DOCTYPE",
        "ERROR",
        "EST",
        "FAIL",
        "FALSE",
        "III",
        "INFO",
        "LICENSE",
        "MAJOR",
        "MAY",
        "MINOR",
        "MST",
        "MUST",
        "NEVER",
        "NONE",
        "NOT",
        "NOTE",
        "ONLY",
        "PASS",
        "PATCH",
        "PDT",
        "PST",
        "README",
        "REQUIRED",
        "SHALL",
        "SHOULD",
        "TBD",
        "TLDR",
        "TODO",
        "TRUE",
        "VII",
        "VIII",
        "WARN",
        "AAAS",
        "ADR",
        "APA",
        "ARES",
        "ASD",
        "ASES",
        "BMJ",
        "CDC",
        "DTCG",
        "FKGL",
        "GAO",
        "HAS",
        "JAMA",
        "JARS",
        "NAS",
        "NIH",
        "NNG",
        "PNAS",
        "SGCS",
        "STE",
        "SWCS",
        "UNSLOP",
    }
)

_FENCED_CODE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?-->", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]+\)")
_MD_LINK_TARGET_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
_URL_RE = re.compile(r"https?://\S+")
_FILE_URI_RE = re.compile(r"\bfile://\S+", re.IGNORECASE)
_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)
_ACRONYM_TOKEN_RE = re.compile(r"\b([A-Z]{3,10})s?\b")
_RULE_ID_RE = re.compile(r"\b[A-Z]{2,12}-[A-Z0-9][A-Z0-9._-]*\b")
_FILENAME_TOKEN_RE = re.compile(
    r"\b[A-Za-z0-9_.-]+\.(?:md|markdown|txt|json|jsonl|yml|yaml|toml|rst|svg|html|css|py|sh|xml|pdf)\b"
)
_DOMAIN_BRAND_RE = re.compile(r"\bGOV\.UK\b")
_TLDR_HEADING_RE = re.compile(
    r"^(#{1,4})\s+(?:TL;DR|TLDR|In Brief|Key Points|Plain Language Summary|Significance Statement|What This Study Adds|Research in Context|eLife Digest|Highlights)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)


def has_utf8_bom(path: Path) -> bool:
    """Return True when `path` begins with a UTF-8 byte-order mark."""
    return path.read_bytes().startswith(b"\xef\xbb\xbf")


def count_syllables(word: str) -> int:
    """Deterministically estimate English syllable count for an alphabetic word."""
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
        return 0
    if len(cleaned) <= 3:
        return 1

    if cleaned.endswith("e"):
        if not cleaned.endswith(("le", "ee", "oe", "ye")) or (
            cleaned.endswith("le") and len(cleaned) > 2 and cleaned[-3] in "aeiouy"
        ):
            cleaned = cleaned[:-1]
    elif cleaned.endswith("ed") and len(cleaned) > 4 and cleaned[-3] not in "td":
        cleaned = cleaned[:-2]
    elif cleaned.endswith("es") and len(cleaned) > 4 and not cleaned.endswith(("ses", "zes", "xes", "ches", "shes")):
        cleaned = cleaned[:-2]

    groups = _VOWEL_GROUP_RE.findall(cleaned)
    return max(1, len(groups))


def _strip_code_and_links(text: str, *, code_placeholder: str = "code") -> str:
    s = _FENCED_CODE_RE.sub("\n", text)
    s = _HTML_COMMENT_RE.sub("\n", s)
    s = _MD_LINK_RE.sub(r"\1", s)
    s = _URL_RE.sub("", s)
    return _INLINE_CODE_RE.sub(code_placeholder, s)


def _normalize_markdown_to_sentences(text: str) -> list[str]:
    s = _strip_code_and_links(text, code_placeholder="code")
    sentences: list[str] = []
    for raw_line in s.splitlines():
        line = raw_line.strip()
        if not line or re.fullmatch(r"[\|\s:\-]+", line):
            continue
        line = re.sub(r"^(?:#{1,6}|>|\*|-|\+|\d+\.)\s+", "", line)
        line = line.replace("**", "").replace("*", "").replace("|", ". ")
        for chunk in re.split(r"[.!?]+(?:\s+|$)", line):
            words = _WORD_RE.findall(chunk)
            if words:
                sentences.append(" ".join(words))
    return sentences


def compute_flesch_kincaid(text: str) -> dict[str, Any]:
    """Compute Flesch-Kincaid Grade Level (FKGL) as an advisory diagnostic."""
    sentences = _normalize_markdown_to_sentences(text)
    all_words: list[str] = []
    for sent in sentences:
        all_words.extend(_WORD_RE.findall(sent))

    if not all_words or not sentences:
        return {
            "words": 0,
            "sentences": 0,
            "syllables": 0,
            "words_per_sentence": 0.0,
            "syllables_per_word": 0.0,
            "grade_level": 0.0,
        }

    total_words = len(all_words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(w) for w in all_words)
    wps = total_words / total_sentences
    spw = total_syllables / total_words
    raw_grade = 0.39 * wps + 11.8 * spw - 15.59
    return {
        "words": total_words,
        "sentences": total_sentences,
        "syllables": total_syllables,
        "words_per_sentence": round(wps, 2),
        "syllables_per_word": round(spw, 2),
        "grade_level": round(max(0.0, raw_grade), 2),
    }


def compute_sentence_length_metrics(text: str) -> dict[str, int]:
    """Compute maximum prose sentence length across Markdown lines."""
    s = _strip_code_and_links(text, code_placeholder="item")
    procedural_sentences = 0
    descriptive_sentences = 0
    max_procedural = 0
    max_descriptive = 0

    for raw_line in s.splitlines():
        line = raw_line.strip()
        if not line or re.fullmatch(r"[\|\s:\-]+", line) or line.startswith("|"):
            continue
        is_procedural = bool(re.match(r"^(?:\d+\.|-|\*)\s+", line))
        cleaned = re.sub(r"^(?:#{1,6}|>|\*|-|\+|\d+\.)\s+", "", line)
        cleaned = cleaned.replace("**", "").replace("*", "")
        for chunk in re.split(r"[.!?]+(?:\s+|$)", cleaned):
            words = _WORD_RE.findall(chunk)
            if not words:
                continue
            wcount = len(words)
            if is_procedural:
                procedural_sentences += 1
                max_procedural = max(max_procedural, wcount)
            else:
                descriptive_sentences += 1
                max_descriptive = max(max_descriptive, wcount)

    return {
        "procedural_sentences": procedural_sentences,
        "descriptive_sentences": descriptive_sentences,
        "max_procedural_words": max_procedural,
        "max_descriptive_words": max_descriptive,
        "max_sentence_words": max(max_procedural, max_descriptive),
    }


def check_banned_jargon(text: str, *, context: str = "prose") -> list[str]:
    """Check prose for banned AI filler, corporate buzzwords, and ambiguous modals."""
    s = _strip_code_and_links(text, code_placeholder="item")
    lowered = s.lower()
    errors: list[str] = []
    for term, guidance in BANNED_JARGON_AND_FILLER.items():
        if term.endswith("."):
            pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?=\s|$|[)\],;:])", re.IGNORECASE)
        else:
            pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        if pattern.search(lowered):
            errors.append(f"[LAN-009:JARGON] {context}: banned filler/ambiguous term {term!r} ({guidance})")
    return errors


def check_undefined_acronyms(
    text: str,
    *,
    context: str = "prose",
    extra_allowed: set[str] | None = None,
) -> list[str]:
    """Detect unexpanded all-caps acronyms in prose (LAN-003)."""
    s = _strip_code_and_links(text, code_placeholder=" ")
    s = _FILENAME_TOKEN_RE.sub(" ", s)
    s = _DOMAIN_BRAND_RE.sub(" ", s)
    s = _RULE_ID_RE.sub(" ", s)

    allowed = set(COMMON_ACRONYMS_ALLOWLIST)
    if extra_allowed:
        allowed.update(extra_allowed)

    defined: set[str] = set()
    for m in re.finditer(r"[A-Za-z][A-Za-z\s/-]{2,}\(\s*([A-Z]{3,10})s?\s*\)", s):
        defined.add(m.group(1))
    for m in re.finditer(r"\b([A-Z]{3,10})\s*\([A-Za-z][A-Za-z\s/-]{3,}\)", s):
        defined.add(m.group(1))
    for m in re.finditer(r"(?:^|[\*\-\s])([A-Z]{3,10})\s*(?::|—|--)\s+[A-Za-z]", s, re.MULTILINE):
        defined.add(m.group(1))

    undefined_seen: list[str] = []
    for raw_line in s.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        alpha_chars = [ch for ch in stripped if ch.isalpha()]
        if alpha_chars and all(ch.isupper() for ch in alpha_chars) and len(alpha_chars) >= 8:
            continue
        for match in _ACRONYM_TOKEN_RE.finditer(stripped):
            acr = match.group(1)
            if acr in allowed or acr in defined or acr in undefined_seen:
                continue
            undefined_seen.append(acr)

    return [
        f"[LAN-003:ACRONYM] {context}: undefined acronym {acr!r}; expand at first use or replace with plain terms"
        for acr in undefined_seen
    ]


def extract_tldr_sections(markdown_text: str) -> list[str]:
    """Extract Markdown sections headed by TL;DR or equivalent summary headings."""
    matches = list(_TLDR_HEADING_RE.finditer(markdown_text))
    if not matches:
        return []
    sections: list[str] = []
    for m in matches:
        level = len(m.group(1))
        start = m.end()
        next_heading = re.search(rf"^#{{1,{level}}}\s+\S", markdown_text[start:], re.MULTILINE)
        end = start + next_heading.start() if next_heading else len(markdown_text)
        body = markdown_text[start:end].strip()
        if body:
            sections.append(body)
    return sections


def _markdown_heading_slugs(text: str) -> set[str]:
    """Extract GitHub-style heading anchor slugs from Markdown text."""
    slugs: set[str] = set()
    for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, re.MULTILINE):
        raw = re.sub(r"[`*_~]", "", match.group(1)).strip().lower()
        collapsed = re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", raw)).strip("-")
        gfm = re.sub(r"[^a-z0-9 -]", "", raw).replace(" ", "-").strip("-")
        if collapsed:
            slugs.add(collapsed)
        if gfm:
            slugs.add(gfm)
    return slugs


def check_markdown_links(markdown_text: str, *, source_file: Path, repo_root: Path = REPO_ROOT) -> list[str]:
    """Verify zero file:// URIs and that relative Markdown links + anchors resolve inside repo_root."""
    stripped = _FENCED_CODE_RE.sub("\n", markdown_text)
    stripped = _HTML_COMMENT_RE.sub("\n", stripped)
    stripped = _INLINE_CODE_RE.sub("code", stripped)

    errors: list[str] = []
    resolved_root = repo_root.resolve()
    rel_label = (
        str(source_file.resolve().relative_to(resolved_root))
        if source_file.resolve().is_relative_to(resolved_root)
        else str(source_file)
    )

    for _, raw_target in _MD_LINK_TARGET_RE.findall(stripped):
        target = raw_target.strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.lower().startswith("file://"):
            errors.append(f"[DOC-003:LINK] {rel_label}: machine-local file:// link {raw_target!r} is forbidden")
            continue
        if ' "' in target or " '" in target:
            target = target.split()[0]
        file_part, sep, fragment = target.partition("#")
        if file_part.startswith("/"):
            dest = (resolved_root / file_part.lstrip("/")).resolve()
        elif not file_part:
            dest = source_file.resolve()
        else:
            dest = (source_file.resolve().parent / file_part).resolve()

        if not dest.is_relative_to(resolved_root):
            errors.append(f"[DOC-003:LINK] {rel_label}: link {raw_target!r} escapes repository root")
            continue
        if not dest.exists():
            errors.append(f"[DOC-003:LINK] {rel_label}: broken relative link {raw_target!r}")
            continue
        if sep == "#" and fragment and dest.is_file() and dest.suffix.lower() in (".md", ".markdown"):
            slugs = _markdown_heading_slugs(dest.read_text(encoding="utf-8-sig"))
            if fragment.lower() not in slugs:
                errors.append(
                    f"[DOC-003:LINK] {rel_label}: broken Markdown heading anchor #{fragment} in {raw_target!r}"
                )

    unlinked = _MD_LINK_RE.sub(" ", stripped)
    for file_uri in _FILE_URI_RE.findall(unlinked):
        errors.append(f"[DOC-003:LINK] {rel_label}: machine-local file:// URI {file_uri!r} is forbidden")

    return errors


def _expand_doc_globs(repo_root: Path, patterns: tuple[str, ...]) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []
    for pat in patterns:
        for match in sorted(repo_root.glob(pat)):
            if match.is_file() and match not in seen:
                seen.add(match)
                ordered.append(match)
    return ordered


def audit_repo_docs(
    repo_root: Path = REPO_ROOT,
    *,
    human_globs: tuple[str, ...] = HUMAN_FACING_DOC_GLOBS,
    operational_globs: tuple[str, ...] = OPERATIONAL_DOC_GLOBS,
) -> tuple[list[str], list[str]]:
    """Audit repository human-facing and operational documentation."""
    errors: list[str] = []
    warnings: list[str] = []

    readme_path = repo_root / "README.md"
    if not readme_path.is_file():
        errors.append("[DOC-001:TLDR] Missing repository README.md")
    else:
        if has_utf8_bom(readme_path):
            errors.append("[DOC-001:TLDR] README.md contains a UTF-8 BOM (\\ufeff); save as plain UTF-8")
        readme_text = readme_path.read_text(encoding="utf-8-sig")
        tldrs = extract_tldr_sections(readme_text)
        if not tldrs:
            errors.append("[DOC-001:TLDR] README.md must include a '## TL;DR' section for human readers")
        else:
            tldr_fk = compute_flesch_kincaid(tldrs[0])
            if tldr_fk["words"] == 0 or tldr_fk["words"] > MAX_README_TLDR_WORDS:
                errors.append(
                    f"[DOC-001:TLDR] README.md TL;DR has {tldr_fk['words']} words (must be 1..{MAX_README_TLDR_WORDS})"
                )

    human_docs = _expand_doc_globs(repo_root, human_globs)
    operational_docs = [p for p in _expand_doc_globs(repo_root, operational_globs) if p not in set(human_docs)]

    for doc_path in human_docs:
        rel = str(doc_path.relative_to(repo_root))
        if doc_path != readme_path and has_utf8_bom(doc_path):
            errors.append(f"[DOC-001:TLDR] {rel}: contains a UTF-8 BOM (\\ufeff); save as plain UTF-8")
        text = doc_path.read_text(encoding="utf-8-sig")
        fk = compute_flesch_kincaid(text)
        len_metrics = compute_sentence_length_metrics(text)
        errors.extend(check_banned_jargon(text, context=rel))
        errors.extend(check_undefined_acronyms(text, context=rel))
        if len_metrics["max_sentence_words"] > MAX_REPO_DOC_SENTENCE_WORDS:
            errors.append(
                f"[DOC-002:RUNON] {rel}: longest sentence has {len_metrics['max_sentence_words']} words "
                f"(repository documentation max is {MAX_REPO_DOC_SENTENCE_WORDS})"
            )
        elif len_metrics["max_sentence_words"] > ADVISORY_SENTENCE_WORDS:
            warnings.append(
                f"[LAN-004:ADVISORY] {rel}: longest sentence has {len_metrics['max_sentence_words']} words "
                f"(advisory target <= {ADVISORY_SENTENCE_WORDS})"
            )
        if fk["grade_level"] > ADVISORY_PUBLIC_FK_GRADE:
            warnings.append(
                f"[LAN-010:ADVISORY] {rel}: Flesch-Kincaid Grade Level is {fk['grade_level']} "
                f"(advisory target <= {ADVISORY_PUBLIC_FK_GRADE})"
            )
        errors.extend(check_markdown_links(text, source_file=doc_path, repo_root=repo_root))

    for doc_path in operational_docs:
        rel = str(doc_path.relative_to(repo_root))
        if has_utf8_bom(doc_path):
            errors.append(f"[DOC-001:TLDR] {rel}: contains a UTF-8 BOM (\\ufeff); save as plain UTF-8")
        text = doc_path.read_text(encoding="utf-8-sig")
        errors.extend(check_banned_jargon(text, context=rel))
        errors.extend(check_markdown_links(text, source_file=doc_path, repo_root=repo_root))

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    errors, warnings = audit_repo_docs(REPO_ROOT)
    for w in warnings:
        print(f"ADVISORY: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("OK: All scoped documentation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
