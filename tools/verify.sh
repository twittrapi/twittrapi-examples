#!/usr/bin/env bash
# Static checks for every example. Run tools/setup-local-sdks.sh first.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Python: py_compile + import"
.venv/bin/python -m py_compile python/_shared/extract.py python/*/*.py tools/mock_server.py
for f in python/*/*.py; do
  # Import each script as a module (runs its imports, not main()).
  .venv/bin/python -W ignore -c "import importlib.util as u, sys; s=u.spec_from_file_location('ex', sys.argv[1]); m=u.module_from_spec(s); s.loader.exec_module(m)" "$f"
  echo "  ok $f"
done

echo "== Node: node --check + import resolution"
for f in node/_shared/*.mjs node/[!_]*/*.mjs; do
  node --check "$f"
  echo "  ok $f"
done
(cd node && node -e "import('twittrapi').then(m => { if (!m.TwittrAPI) process.exit(1); console.log('  twittrapi resolves, version', m.VERSION); })")

echo "== Node: type-check the JS against the SDK's .d.ts files (checkJs)"
SDK_NODE="$(cd node/node_modules/twittrapi && pwd -P)"
(cd node && "$SDK_NODE/node_modules/.bin/tsc" -p jsconfig.json --typeRoots "$SDK_NODE/node_modules/@types" && echo "  ok")

echo "== Go: vet + build"
(cd go && go vet ./... && go build ./... && echo "  ok")

echo "== Shell: bash -n"
for f in shell/_shared/*.sh shell/[!_]*/*.sh; do bash -n "$f" && echo "  ok $f"; done
echo "All checks passed."
