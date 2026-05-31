#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/OKEUNSOO/ai-analyst-pipeline"

# stdin이 TTY면 로컬 실행, 아니면 curl | bash 원격 실행
if [ -t 0 ]; then
  REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  TMPDIR_CLONE="$(mktemp -d)"
  echo "파일 다운로드 중..."
  curl -sL "$REPO_URL/archive/refs/heads/main.tar.gz" | tar xz -C "$TMPDIR_CLONE" --strip-components=1
  REPO_DIR="$TMPDIR_CLONE"
  trap 'rm -rf "$TMPDIR_CLONE"' EXIT
fi

SHARED="$REPO_DIR/shared"

link_shared() {
  local dest="$1"
  cp -r "$SHARED/scripts"    "$dest/scripts"
  cp -r "$SHARED/references" "$dest/references"
  cp -r "$SHARED/assets"     "$dest/assets"
}

# ── uninstall ────────────────────────────────────────────

uninstall_claude() {
  rm -rf "$HOME/.claude/plugins/ai-analyst-pipeline"
}

uninstall_codex() {
  if command -v codex &>/dev/null; then
    codex plugin remove ai-analyst-pipeline@ai-analyst-local 2>/dev/null || true
  fi
  rm -rf "$HOME/.codex/plugins/ai-analyst-pipeline"
}

uninstall_hermes()   { rm -rf "$HOME/.hermes/skills/ai-analyst-pipeline"; }
uninstall_openclaw() { rm -rf "$HOME/.openclaw/skills/ai-analyst-pipeline"; }
uninstall_gemini()   { rm -rf "$HOME/.gemini/skills/ai-analyst-pipeline"; }

# ── install ──────────────────────────────────────────────

installed=()

install_claude() {
  CLAUDE_SKILLS="$HOME/.claude/plugins/ai-analyst-pipeline/skills"
  mkdir -p "$CLAUDE_SKILLS"
  for skill in ai-analyst-pipeline run-pipeline visualize dashboard-design; do
    mkdir -p "$CLAUDE_SKILLS/$skill"
    cp "$REPO_DIR/platforms/claude/skills/$skill/SKILL.md" "$CLAUDE_SKILLS/$skill/SKILL.md"
    link_shared "$CLAUDE_SKILLS/$skill"
  done
  installed+=("Claude Code → $CLAUDE_SKILLS")
}

install_codex() {
  CODEX_PLUGIN="$HOME/.codex/plugins/ai-analyst-pipeline"
  mkdir -p "$CODEX_PLUGIN"
  cp -r "$REPO_DIR/platforms/codex/." "$CODEX_PLUGIN/"
  link_shared "$CODEX_PLUGIN"

  # marketplace.json 생성 (Codex 0.135.0+ 스키마)
  MARKETPLACE="$HOME/.agents/plugins/marketplace.json"
  mkdir -p "$(dirname "$MARKETPLACE")"
  python3 - "$MARKETPLACE" <<'PYEOF'
import sys, json, os

marketplace_path = sys.argv[1]

data = {
    "name": "ai-analyst-local",
    "interface": {
        "displayName": "AI Pipeline Local"
    },
    "plugins": [
        {
            "name": "ai-analyst-pipeline",
            "source": {
                "source": "local",
                "path": "./.codex/plugins/ai-analyst-pipeline"
            },
            "policy": {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL"
            },
            "category": "Productivity"
        }
    ]
}

with open(marketplace_path, "w") as f:
    json.dump(data, f, indent=2)
PYEOF

  if command -v codex &>/dev/null; then
    codex plugin add ai-analyst-pipeline --marketplace ai-analyst-local 2>/dev/null && \
      echo "  → codex plugin 등록 완료" || \
      echo "  → codex plugin add 실패 — 수동 실행: codex plugin add ai-analyst-pipeline --marketplace ai-analyst-local"
  else
    echo "  → codex 명령어 없음 — Codex 실행 후 수동 등록: codex plugin add ai-analyst-pipeline --marketplace ai-analyst-local"
  fi

  installed+=("Codex → $CODEX_PLUGIN")
}

install_hermes() {
  HERMES_SKILL="$HOME/.hermes/skills/ai-analyst-pipeline"
  mkdir -p "$HERMES_SKILL"
  cp "$REPO_DIR/platforms/hermes/ai-analyst-pipeline/SKILL.md" "$HERMES_SKILL/SKILL.md"
  link_shared "$HERMES_SKILL"
  installed+=("Hermes → $HERMES_SKILL")
}

install_openclaw() {
  OPENCLAW_SKILL="$HOME/.openclaw/skills/ai-analyst-pipeline"
  mkdir -p "$OPENCLAW_SKILL"
  cp "$REPO_DIR/platforms/openclaw/ai-analyst-pipeline/SKILL.md" "$OPENCLAW_SKILL/SKILL.md"
  link_shared "$OPENCLAW_SKILL"
  installed+=("OpenClaw → $OPENCLAW_SKILL")
}

install_gemini() {
  GEMINI_SKILL="$HOME/.gemini/skills/ai-analyst-pipeline"
  mkdir -p "$GEMINI_SKILL"
  cp "$REPO_DIR/platforms/gemini/ai-analyst-pipeline/SKILL.md" "$GEMINI_SKILL/SKILL.md"
  link_shared "$GEMINI_SKILL"
  installed+=("Gemini CLI → $GEMINI_SKILL")
}

# ── 인자 파싱 ─────────────────────────────────────────────

MODE="install"
PLATFORMS=()

for arg in "$@"; do
  case "$arg" in
    update)                               MODE="update" ;;
    all) PLATFORMS+=(claude codex hermes openclaw gemini) ;;
    claude|codex|hermes|openclaw|gemini)  PLATFORMS+=("$arg") ;;
    *) echo "알 수 없는 인자: $arg (update | claude | codex | hermes | openclaw | gemini | all)" ;;
  esac
done

# 플랫폼 미지정 시 자동 감지
if [ ${#PLATFORMS[@]} -eq 0 ]; then
  command -v claude   &>/dev/null || [ -d "$HOME/.claude" ]   && PLATFORMS+=(claude)
  command -v codex    &>/dev/null || [ -d "$HOME/.codex" ]    && PLATFORMS+=(codex)
  command -v hermes   &>/dev/null || [ -d "$HOME/.hermes" ]   && PLATFORMS+=(hermes)
  command -v openclaw &>/dev/null || [ -d "$HOME/.openclaw" ] && PLATFORMS+=(openclaw)
  command -v gemini   &>/dev/null || [ -d "$HOME/.gemini" ]   && PLATFORMS+=(gemini)
fi

# ── 실행 ─────────────────────────────────────────────────

for platform in "${PLATFORMS[@]}"; do
  if [ "$MODE" = "update" ]; then
    echo "업데이트 중: $platform"
    "uninstall_$platform"
  fi
  "install_$platform"
done

echo ""
if [ ${#installed[@]} -eq 0 ]; then
  echo "설치된 플랫폼을 찾지 못했습니다."
  echo "사용법: ./install.sh [update] [claude|codex|hermes|openclaw|gemini|all]"
else
  echo "${MODE} 완료:"
  for p in "${installed[@]}"; do
    echo "  ✓ $p"
  done
fi
