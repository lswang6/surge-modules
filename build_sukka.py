#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build the reviewed Sukka domain set, policy-free rule list and Surge module."""

import argparse
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
SOURCE_SHA256 = "f699906c1c1e0db1614cb4ba29d515002dd5de12cf764f4675a1744533265928"
SOURCE_COUNT = 134574
NAME = "Sukka-Reject-Balanced"
DOMAINSET_URL = f"https://raw.githubusercontent.com/lswang6/surge-modules/main/{NAME}.domainset"
LABEL = r"[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?"
DOMAIN = re.compile(rf"\.?{LABEL}(?:\.{LABEL})*", re.ASCII)


def parse_entries(text):
    entries = []
    seen = set()
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if not DOMAIN.fullmatch(line) or len(line.lstrip(".")) > 253:
            raise ValueError(f"Invalid domain entry: {line!r}")
        if line in seen:
            raise ValueError(f"Duplicate domain entry: {line}")
        seen.add(line)
        entries.append(line)
    return entries


def validate_url(value):
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError("Source URLs must be single-line HTTPS URLs")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"Invalid source URL: {value!r}")


def rule_lines(entries):
    return [f"DOMAIN-SUFFIX,{entry[1:]}" if entry.startswith(".")
            else f"DOMAIN,{entry}" for entry in entries]


def blocked(domain, entries):
    if domain in entries:
        return True
    labels = domain.split(".")
    return any("." + ".".join(labels[i:]) in entries for i in range(len(labels)))


def build(source, review):
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source snapshot SHA-256 does not match the pinned version")
    fields = {"source_url", "source_sha256", "source_updated", "reviewed_on", "removals"}
    if not isinstance(review, dict) or set(review) != fields:
        raise ValueError("Invalid review metadata fields")
    if review["source_sha256"] != SOURCE_SHA256:
        raise ValueError("Review SHA-256 does not match the pinned source")
    validate_url(review["source_url"])
    for key in ("source_updated", "reviewed_on"):
        if not isinstance(review[key], str) or any(c.isspace() for c in review[key]):
            raise ValueError(f"Invalid {key}")
    if date.fromisoformat(review["reviewed_on"]).isoformat() != review["reviewed_on"]:
        raise ValueError("reviewed_on must use YYYY-MM-DD")
    datetime.fromisoformat(review["source_updated"].replace("Z", "+00:00"))
    text = source.decode("utf-8")
    if f"# Last Updated: {review['source_updated']}" not in text.splitlines():
        raise ValueError("Review source_updated does not match the source header")
    entries = parse_entries(text)
    if len(entries) != SOURCE_COUNT:
        raise ValueError("Unexpected source entry count")
    if not isinstance(review["removals"], list):
        raise ValueError("removals must be a list")
    available = set(entries)
    removals = set()
    for removal in review["removals"]:
        if not isinstance(removal, dict) or set(removal) != {"entry", "reason", "sources"}:
            raise ValueError("Invalid removal metadata fields")
        entry = removal["entry"]
        if not isinstance(entry, str) or entry not in available:
            raise ValueError(f"Removal is not an exact source entry: {entry!r}")
        if entry in removals:
            raise ValueError(f"Duplicate removal: {entry}")
        if not isinstance(removal["reason"], str) or not removal["reason"].strip():
            raise ValueError(f"Missing removal reason: {entry}")
        if not isinstance(removal["sources"], list) or not removal["sources"]:
            raise ValueError(f"Missing removal sources: {entry}")
        for url in removal["sources"]:
            validate_url(url)
        removals.add(entry)
    kept = [entry for entry in entries if entry not in removals]
    kept_set = set(kept)
    for entry in sorted(removals):
        if blocked(entry.lstrip("."), kept_set):
            raise ValueError(f"Removed domain is still blocked by a surviving rule: {entry}")
    header = (
        "# Sukka Reject Balanced\n"
        "# Surge © Sukka; maintained with contributors\n"
        f"# Source: {review['source_url']}\n"
        f"# Source updated: {review['source_updated']}\n"
        f"# Source snapshot SHA-256: {SOURCE_SHA256}\n"
        "# Unmodified source and upstream attribution: sources/sukka-reject.conf\n"
        "# SPDX-License-Identifier: AGPL-3.0-only\n"
        "# Upstream revision: 38ac44a1ae08ae3038c523beaec0d7390af4dc6b\n"
        "# License: LICENSE-AGPL-3.0; third-party attribution: SUKKA-REVIEW.md\n"
        f"# Modified by lswang6, {review['reviewed_on']}: {len(removals)} reviewed compatibility exclusions\n"
        f"# Entries: {len(kept)}\n"
        "# Review and limitations: SUKKA-REVIEW.md\n"
    )
    module = (
        "#!name=Sukka Reject Balanced\n"
        "#!desc=基于 Sukka 约13.4万条广告与追踪规则的兼容性调整快照，排除部分正常服务；免MITM、无脚本，不保证零误拦。来源、排除项及局限见仓库 README 与 SUKKA-REVIEW.md。\n"
        "#!author=Sukka and contributors; modified by lswang6\n"
        "#!homepage=https://github.com/lswang6/surge-modules\n\n"
        + header + "\n[Rule]\n"
        + f"DOMAIN-SET,{DOMAINSET_URL},REJECT,extended-matching\n"
    )
    return {
        f"{NAME}.domainset": (header + "\n".join(kept) + "\n").encode("utf-8"),
        f"{NAME}.list": (header + "\n".join(rule_lines(kept)) + "\n").encode("utf-8"),
        f"{NAME}.sgmodule": module.encode("utf-8"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check committed outputs without writing")
    args = parser.parse_args()
    try:
        outputs = build((ROOT / "sources/sukka-reject.conf").read_bytes(),
                        json.loads((ROOT / "sukka-review.json").read_text(encoding="utf-8")))
        if args.check:
            stale = [name for name, data in outputs.items()
                     if not (ROOT / name).is_file() or (ROOT / name).read_bytes() != data]
            if stale:
                raise ValueError("Missing or outdated outputs: " + ", ".join(stale))
        else:
            for name, data in outputs.items():
                (ROOT / name).write_bytes(data)
    except (OSError, ValueError) as error:
        parser.exit(1, f"build_sukka: {error}\n")
    print("Sukka outputs match the reviewed source." if args.check else "Built three Sukka outputs.")


if __name__ == "__main__":
    main()
