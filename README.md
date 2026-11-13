# Upstream patches for smart-ips-pilgrimage#66 (transfer branch, not for merge)

`git format-patch` output for three other repositories, prepared from this
repository's #66 investigation because that session cannot push to them.
Apply each with `git am` on the base named in its section; delete this branch
once they are applied.

| repository | base (main) | patch |
|---|---|---|
| litlfred/cat-harness-tools | 5bbc634c903162ea00c6386fca1e589f36aa900a | `cat-harness-tools/0001-…patch` |
| litlfred/folio-assistant-core | b0a2389d744bd92d905078ba8ffd6c77bcf31769 | `folio-assistant-core/0001-…patch` |
| litlfred/smart-trust-tools | 3275867e993e (main) | `smart-trust-tools/0001-…patch` |
