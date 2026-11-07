# SUSHI for the translation-supplement check

The FHIR terms of the six-language translation are CodeSystem supplements,
one file per locale in `input/fsh/translations/<locale>.fsh`. The IG build
(`fhirbuild.yml`) is manual-only (owner, 2026-11-01, card Q-VC-8), so this
directory holds what CI needs to compile them on every pull request:
`supplements_check.py`, run by the `supplements` job of
`.github/workflows/translations.yml` (owner, 2026-11-07: "add the SUSHI check
to smart-ips-pilgrimage CI").

## Dependencies

| dependency | pinned by | why |
|---|---|---|
| SUSHI (`fsh-sushi` 3.20.1, 2026-08-18) and its npm graph | `package-lock.json` integrity, installed with `npm ci --ignore-scripts`; the same graph as smart-trust-demo's `tools/ig-gen` | Compiles the CodeSystems and every translation supplement (FSHOnly). The HL7 tool every FHIR IG is built with; not reimplementable. |
| FHIR package `hl7.fhir.r4.core` 4.0.1 | sha512 in `fhir-packages.lock.json`, checked by `fhir_cache.py` before unpacking | The only package the check compiles against, from the registry.npmjs.org mirror of the FHIR package registry, so SUSHI downloads nothing at run time. |

## What the check asserts

SUSHI 0 errors; every supplement names a CodeSystem defined here; every code it
designates exists in that CodeSystem; every designation's language is the
supplement's `^language`; supplement ids are unique across locales.

```sh
npm ci --ignore-scripts --no-audit --no-fund --prefix input/scripts/sushi
python3 -I input/scripts/sushi/fhir_cache.py
python3 -I input/scripts/sushi/supplements_check.py
```
