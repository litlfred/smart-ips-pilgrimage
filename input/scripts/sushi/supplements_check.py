#!/usr/bin/env python3
"""Compile this IG's CodeSystems with every per-locale translation supplement, and check them.

The FHIR terms of the six-language translation are CodeSystem supplements, one
file per locale in input/fsh/translations/<locale>.fsh (^content = #supplement,
^supplements = Canonical(X), ^language = #<locale>). The IG build (fhirbuild.yml)
is manual-only, so nothing else compiles them on a pull request.

This builds a throw-away SUSHI project from the CodeSystem definitions in
input/fsh/ and every supplement file, FSHOnly, against FHIR R4 core alone
(laid down by fhir_cache.py), and then checks what SUSHI cannot:

- SUSHI reports 0 errors;
- every supplement names a CodeSystem that exists here;
- every code a supplement designates exists in that CodeSystem;
- every designation's language is the supplement's ^language;
- supplement ids are unique across locales (SUSHI would merge or fail otherwise).

Standard library only. Exit 1 on any finding.
Run: python3 -I input/scripts/sushi/supplements_check.py
"""
import glob
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
SUSHI = HERE / "node_modules" / ".bin" / "sushi"


def config():
    src = (ROOT / "sushi-config.yaml").read_text()
    keep = [m.group(0) for k in ("canonical", "status", "version", "fhirVersion")
            if (m := re.search(rf"^{k}\s*:.*$", src, re.M))]
    return "\n".join(keep + ["FSHOnly: true"]) + "\n"


def codes(cs):
    out = set()

    def walk(items):
        for c in items or []:
            out.add(c["code"])
            walk(c.get("concept"))

    walk(cs.get("concept"))
    return out


def main():
    supplements = sorted(glob.glob(str(ROOT / "input/fsh/translations/*.fsh")))
    if not supplements:
        print("supplements: no input/fsh/translations/*.fsh — nothing to check")
        return 0
    defs = [f for f in glob.glob(str(ROOT / "input/fsh/**/*.fsh"), recursive=True)
            if "/translations/" not in f and re.search(r"^CodeSystem:", pathlib.Path(f).read_text(), re.M)]
    work = pathlib.Path(tempfile.mkdtemp(prefix="supplements-"))
    try:
        (work / "input/fsh").mkdir(parents=True)
        for f in defs + supplements:
            shutil.copy(f, work / "input/fsh" / f"{pathlib.Path(f).parent.name}--{pathlib.Path(f).name}")
        (work / "sushi-config.yaml").write_text(config())
        run = subprocess.run([str(SUSHI), "build", str(work)], capture_output=True, text=True)
        tail = run.stdout.strip().splitlines()[-12:]
        m = re.search(r"(\d+) Errors?", run.stdout)
        errors = int(m.group(1)) if m else -1
        if errors != 0:
            print("\n".join(run.stdout.splitlines()[-40:]))
            print(f"✗ SUSHI: {errors if errors >= 0 else 'no result line'} error(s)")
            return 1
        out = [json.loads(pathlib.Path(p).read_text())
               for p in glob.glob(str(work / "fsh-generated/resources/CodeSystem-*.json"))]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    base = {c["url"]: c for c in out if c.get("content") != "supplement"}
    sup = [c for c in out if c.get("content") == "supplement"]
    problems, per, ids = [], {}, {}
    for s in sup:
        ids.setdefault(s["id"], 0)
        ids[s["id"]] += 1
        lang = s.get("language", "?")
        per[lang] = per.get(lang, 0) + 1
        b = base.get(s.get("supplements", "").split("|")[0])
        if not b:
            problems.append(f"{s['id']}: supplements {s.get('supplements')}, which is not a CodeSystem here")
            continue
        extra = codes(s) - codes(b)
        if extra:
            problems.append(f"{s['id']}: codes not in {b['id']}: {sorted(extra)[:5]}")
        for c in s.get("concept", []):
            for d in c.get("designation", []):
                if d.get("language") and d["language"] != lang:
                    problems.append(f"{s['id']}: {c['code']} designation in {d['language']}, supplement is {lang}")
    problems += [f"{i}: id used by {n} supplements" for i, n in ids.items() if n > 1]
    print(f"SUSHI 0 errors; {len(base)} CodeSystem(s), {len(sup)} supplement(s): "
          + ", ".join(f"{k} {v}" for k, v in sorted(per.items())))
    for p in problems:
        print(f"  ✗ {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
