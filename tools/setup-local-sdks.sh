#!/usr/bin/env bash
# Development only: point the examples at local checkouts of the SDKs instead of the published
# packages. Everything this creates is gitignored (.venv/, node/node_modules/, go.work).
#
#   SDK_DIR=../ tools/setup-local-sdks.sh     # SDK_DIR holds twittrapi-python, -node and -go
#
# Once the packages are published, users just run `pip install twittrapi`,
# `npm install` (in node/) and `go mod tidy` (in go/) and never need this script.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK_DIR="$(cd "${SDK_DIR:-$ROOT/..}" && pwd)"

echo "Python: .venv with editable $SDK_DIR/twittrapi-python"
python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install --quiet --upgrade pip
"$ROOT/.venv/bin/pip" install --quiet -e "$SDK_DIR/twittrapi-python" gspread

echo "Node: node/node_modules/twittrapi -> $SDK_DIR/twittrapi-node"
if [ ! -f "$SDK_DIR/twittrapi-node/dist/esm/index.js" ]; then
  (cd "$SDK_DIR/twittrapi-node" && npm install --silent && npm run build --silent)
fi
mkdir -p "$ROOT/node/node_modules"
ln -sfn "$SDK_DIR/twittrapi-node" "$ROOT/node/node_modules/twittrapi"

echo "Go: go.work using ./go and $SDK_DIR/twittrapi-go"
cat > "$ROOT/go.work" <<GOWORK
// Local development only (gitignored, never committed): builds go/ against a local SDK checkout.
go 1.21

use (
	./go
	$SDK_DIR/twittrapi-go
)
GOWORK
echo "Done."
