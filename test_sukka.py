#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run with python3 test_sukka.py after supplying sukka-review.json and building."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from build_sukka import (DOMAINSET_URL, NAME, ROOT, SOURCE_COUNT, SOURCE_SHA256,
                         blocked, build, parse_entries, rule_lines)


def main():
    source = (ROOT / "sources/sukka-reject.conf").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256
    review = json.loads((ROOT / "sukka-review.json").read_text(encoding="utf-8"))
    assert review["source_url"] == ("https://raw.githubusercontent.com/SukkaLab/ruleset.skk.moe/"
                                    "393edcad7e2f021383a82242a9614fd4a7aeb917/List/domainset/reject.conf")
    original = parse_entries(source.decode("utf-8"))
    assert len(original) == len(set(original)) == SOURCE_COUNT
    assert len([entry for entry in original if "_" in entry]) == 4
    removed = {item["entry"] for item in review["removals"]}
    protected = {
        ".taio.app": ["taio.app", "www.taio.app"],
        ".mob.com": ["webapi.sms.mob.com"],
        ".jpush.cn": ["api.jpush.cn", "device.jpush.cn"],
        ".jiguang.cn": ["docs.jiguang.cn"],
        ".getui.com": ["restapi.getui.com", "docs.getui.com"],
        ".plus.com": ["example.plus.com"],
        ".log.aliyuncs.com": ["cn-hangzhou.log.aliyuncs.com"],
        ".api.statsigcdn.com": ["api.statsigcdn.com"],
        ".data": ["example.data"],
    }
    assert removed == set(protected) and len(review["removals"]) == 9
    outputs = build(source, review)
    assert outputs == build(source, deepcopy(review))
    for name, data in outputs.items():
        assert (ROOT / name).read_bytes() == data, name
        assert "$content-hash" not in data.decode("utf-8")
    kept = parse_entries(outputs[f"{NAME}.domainset"].decode("utf-8"))
    assert kept == [entry for entry in original if entry not in removed]
    assert len(kept) == 134565
    assert sum(entry.startswith(".") for entry in kept) == 133409
    assert sum(not entry.startswith(".") for entry in kept) == 1156
    kept_set = set(kept)
    assert {entry for entry in original if "_" in entry} <= kept_set
    assert removed.isdisjoint(kept_set)
    assert all(not blocked(entry.lstrip("."), kept_set) for entry in removed)
    rules = [line for line in outputs[f"{NAME}.list"].decode("utf-8").splitlines()
             if line and not line.startswith("#")]
    assert all(line.count(",") == 1 for line in rules)
    assert all(line.split(",")[0] in {"DOMAIN", "DOMAIN-SUFFIX"} for line in rules)
    assert ["." + line.split(",")[1] if line.startswith("DOMAIN-SUFFIX,")
            else line.split(",")[1] for line in rules] == kept
    assert blocked("pagead2.googlesyndication.com", kept_set)
    assert blocked("www.googleadservices.com", kept_set)
    for hosts in protected.values():
        for domain in hosts:
            assert not blocked(domain, kept_set), domain
    for domain in ("events.statsigapi.net", "jpush.io", "getui.cn", "getui.net"):
        assert "." + domain in kept_set and blocked(domain, kept_set), domain
    synthetic = ["exact.example", ".suffix.example"]
    assert rule_lines(synthetic) == ["DOMAIN,exact.example", "DOMAIN-SUFFIX,suffix.example"]
    assert blocked("exact.example", set(synthetic))
    assert not blocked("child.exact.example", set(synthetic))
    assert blocked("suffix.example", set(synthetic))
    assert blocked("child.suffix.example", set(synthetic))
    module = outputs[f"{NAME}.sgmodule"].decode("utf-8")
    metadata = [line.split("=", 1)[0] for line in module.splitlines() if line.startswith("#!")]
    assert metadata == ["#!name", "#!desc", "#!author", "#!homepage"]
    assert "#!name=Sukka Reject Balanced" in module
    active = [line for line in module.splitlines() if line and not line.startswith("#")]
    assert active == ["[Rule]", f"DOMAIN-SET,{DOMAINSET_URL},REJECT,extended-matching"]
    assert all("DIRECT" not in line for line in rules + active)
    assert not any(line.startswith(("[MITM]", "[Script]", "[Proxy", "[Host]", "[DNS]"))
                   for line in rules + active)
    for bad in (" leading.example", "trailing.example ", "..example", "bad..example", "-bad.example",
                "bad-.example", "example,REJECT", "*.example", "https://example", "a" * 64 + ".com",
                "same.example\nsame.example"):
        try:
            parse_entries(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Accepted invalid domain: {bad}")
    invalid = deepcopy(review)
    item = {"entry": original[0], "reason": "Synthetic invalid-input check", "sources": [review["source_url"]]}
    invalid["removals"] = [item, item]
    missing = deepcopy(review)
    missing["removals"] = [dict(item, entry="not-in-source.invalid")]
    wrong_pin = dict(review, source_sha256="0" * 64)
    for raw, metadata in ((source + b"\n", review), (source, invalid), (source, missing), (source, wrong_pin)):
        try:
            build(raw, metadata)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted invalid source/review")
    # Exercise the CLI on invalid metadata: existing outputs must remain byte-for-byte intact.
    with TemporaryDirectory() as directory:
        sandbox = Path(directory)
        (sandbox / "sources").mkdir()
        (sandbox / "sources/sukka-reject.conf").write_bytes(source)
        (sandbox / "build_sukka.py").write_bytes((ROOT / "build_sukka.py").read_bytes())
        (sandbox / "sukka-review.json").write_text(json.dumps(invalid), encoding="utf-8")
        for name in outputs:
            (sandbox / name).write_bytes(b"sentinel\n")
        result = subprocess.run([sys.executable, str(sandbox / "build_sukka.py")], capture_output=True)
        assert result.returncode != 0 and b"Duplicate removal" in result.stderr
        assert all((sandbox / name).read_bytes() == b"sentinel\n" for name in outputs)
    subprocess.run([sys.executable, str(ROOT / "build_sukka.py"), "--check"], check=True)
    print(f"Sukka checks passed: {len(original)} source, {len(removed)} removed, {len(kept)} retained.")


if __name__ == "__main__":
    main()
