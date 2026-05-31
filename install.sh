#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/OKEUNSOO/ai-analyst-pipeline"

# curl | bash 여부 판단: BASH_SOURCE[0]가 실제 파일이면 로컬 실행
_SCRIPT="${BASH_SOURCE[0]:-}"
if [ -f "$_SCRIPT" ] && [ -d "$(dirname "$_SCRIPT")/platforms" ]; then
  REPO_DIR="$(cd "$(dirname "$_SCRIPT")" && pwd)"
else
  TMPDIR_CLONE="$(mktemp -d)"
  echo "원격 실행 감지 — 파일 다운로드 중..."
  curl -sL "$REPO_URL/archive/refs/heads/main.tar.gz" | tar xz -C "$TMPDIR_CLONE" --strip-components=1
  REPO_DIR="$TMPDIR_CLONE"
  CLEANUP=1
fi

SHARED="$REPO_DIR/shared"

link_shared() {
  local dest="$1"
  ln -sfn "$SHARED/scripts"    "$dest/scripts"
  ln -sfn "$SHARED/references" "$dest/references"
  ln -sfn "$SHARED/assets"     "$dest/assets"
}

installed=()

install_claude() {
  CLAUDE_SKILLS="$HOME/.claude/plugins/ai-pipeline-kit/skills"
  mkdir -p "$CLAUDE_SKILLS"
  for skill in ai-pipeline-kit run-pipeline visualize dashboard-design; do
    mkdir -p "$CLAUDE_SKILLS/$skill"
    cp "$REPO_DIR/platforms/claude/skills/$skill/SKILL.md" "$CLAUDE_SKILLS/$skill/SKILL.md"
    link_shared "$CLAUDE_SKILLS/$skill"
  done
  installed+=("Claude Code → $CLAUDE_SKILLS")
}

install_codex() {
  CODEX_PLUGIN="$HOME/.codex/plugins/ai-pipeline-kit"
  mkdir -p "$CODEX_PLUGIN"
  cp -r "$REPO_DIR/platforms/codex/." "$CODEX_PLUGIN/"
  link_shared "$CODEX_PLUGIN"
  installed+=("Codex → $CODEX_PLUGIN")
}

install_hermes() {
  HERMES_SKILL="$HOME/.hermes/skills/ai-pipeline-kit"
  mkdir -p "$HERMES_SKILL"
  cp "$REPO_DIR/platforms/hermes/ai-pipeline-kit/SKILL.md" "$HERMES_SKILL/SKILL.md"
  link_shared "$HERMES_SKILL"
  installed+=("Hermes → $HERMES_SKILL")
}

install_openclaw() {
  OPENCLAW_SKILL="$HOME/.openclaw/skills/ai-pipeline-kit"
  mkdir -p "$OPENCLAW_SKILL"
  cp "$REPO_DIR/platforms/openclaw/ai-pipeline-kit/SKILL.md" "$OPENCLAW_SKILL/SKILL.md"
  link_shared "$OPENCLAW_SKILL"
  installed+=("OpenClaw → $OPENCLAW_SKILL")
}

install_gemini() {
  GEMINI_SKILL="$HOME/.gemini/skills/ai-pipeline-kit"
  mkdir -p "$GEMINI_SKILL"
  cp "$REPO_DIR/platforms/gemini/ai-pipeline-kit/SKILL.md" "$GEMINI_SKILL/SKILL.md"
  link_shared "$GEMINI_SKILL"
  installed+=("Gemini CLI → $GEMINI_SKILL")
}

# 인자 파싱
TARGETS=("$@")

if [ ${#TARGETS[@]} -eq 0 ]; then
  # 인자 없으면 자동 감지
  command -v claude   &>/dev/null || [ -d "$HOME/.claude" ]   && TARGETS+=(claude)
  command -v codex    &>/dev/null || [ -d "$HOME/.codex" ]    && TARGETS+=(codex)
  command -v hermes   &>/dev/null || [ -d "$HOME/.hermes" ]   && TARGETS+=(hermes)
  command -v openclaw &>/dev/null || [ -d "$HOME/.openclaw" ] && TARGETS+=(openclaw)
  command -v gemini   &>/dev/null || [ -d "$HOME/.gemini" ]   && TARGETS+=(gemini)
fi

for target in "${TARGETS[@]}"; do
  case "$target" in
    all)      install_claude; install_codex; install_hermes; install_openclaw; install_gemini ;;
    claude)   install_claude ;;
    codex)    install_codex ;;
    hermes)   install_hermes ;;
    openclaw) install_openclaw ;;
    gemini)   install_gemini ;;
    *)        echo "알 수 없는 플랫폼: $target (claude | codex | hermes | openclaw | gemini | all)" ;;
  esac
done

echo ""
if [ ${#installed[@]} -eq 0 ]; then
  echo "설치된 플랫폼을 찾지 못했습니다."
  echo "사용법: ./install.sh [claude|codex|hermes|openclaw|gemini|all]"
else
  echo "설치 완료:"
  for p in "${installed[@]}"; do
    echo "  ✓ $p"
  done
fi

[ "${CLEANUP:-0}" = "1" ] && rm -rf "$TMPDIR_CLONE"
