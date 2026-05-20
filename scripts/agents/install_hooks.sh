#!/usr/bin/env bash
# scripts/agents/install_hooks.sh
# Installs the Vibe-Lab pre-commit hook into the local clone's .git/hooks/.
#
# This is opt-in. CI does the same checks at PR time, but agents and
# contributors who run the hook locally get the same feedback in 2 seconds
# instead of waiting for CI.

set -eu

repo_root="$(git rev-parse --show-toplevel)"
src="${repo_root}/scripts/agents/hooks/pre-commit"
dst="${repo_root}/.git/hooks/pre-commit"

if [[ ! -f "${src}" ]]; then
    echo "error: source hook not found at ${src}" >&2
    exit 1
fi

if [[ -e "${dst}" && ! -L "${dst}" ]]; then
    backup="${dst}.backup.$(date +%s)"
    echo "note: existing pre-commit hook backed up to ${backup}"
    mv "${dst}" "${backup}"
fi

# Symlink so updates to the source propagate without reinstalling.
ln -sf "${src}" "${dst}"
chmod +x "${src}"
echo "ok: pre-commit hook installed (symlinked to scripts/agents/hooks/pre-commit)"
echo "    test it with: make agent-check"
