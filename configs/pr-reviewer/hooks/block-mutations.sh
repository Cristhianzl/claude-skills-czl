#!/usr/bin/env bash
# Why: permission rules match a command prefix, so a mutation hidden after && or ; in a compound
# line slips past them; this hook inspects the whole command string before it runs.

set -uo pipefail

input="$(cat)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"
[ -z "$cmd" ] && exit 0

normalized="$(printf '%s' "$cmd" | tr '\n' ' ' | tr -s ' ')"

deny() {
  printf 'BLOCKED (reviewer write guard): %s\n' "$1" >&2
  printf 'This config reviews pull requests; its only write is the review itself.\n' >&2
  printf 'Put the change in a review comment (a suggestion block when it fits) and let the author apply it.\n' >&2
  exit 2
}

case "$normalized" in
  *"git commit"*)   deny "git commit — only the human commits" ;;
  *"git add"*)      deny "git add — the reviewer does not stage" ;;
  *"git push"*)     deny "git push" ;;
  *"git merge"*)    deny "git merge" ;;
  *"git rebase"*)   deny "git rebase" ;;
  *"git reset"*)    deny "git reset" ;;
  *"git revert"*)   deny "git revert" ;;
  *"git restore"*)  deny "git restore" ;;
  *"git clean"*)    deny "git clean" ;;
  *"git cherry-pick"*) deny "git cherry-pick" ;;
  *"git tag"*)      deny "git tag" ;;
  *"git branch -d"*|*"git branch -D"*) deny "git branch deletion" ;;
  *"gh pr review"*) deny "gh pr review — post the review through gh api .../pulls/<n>/reviews (see output-format.md)" ;;
  *"gh pr comment"*) deny "gh pr comment — put it in the review summary instead (see output-format.md)" ;;
  *"gh pr merge"*)  deny "gh pr merge" ;;
  *"gh pr close"*)  deny "gh pr close" ;;
  *"gh pr edit"*)   deny "gh pr edit" ;;
  *"gh pr create"*) deny "gh pr create" ;;
  *"gh pr ready"*)  deny "gh pr ready" ;;
  *"gh issue"*)     deny "gh issue — the reviewer does not touch the tracker" ;;
  *"gh release"*)   deny "gh release" ;;
esac

# Why: gh api switches to POST on its own when given -f/-F/--field/--raw-field/--input, so the
# method is resolved per segment; the only write allowed is creating a review on a pull request.
review_endpoint='(^|[[:space:]])/?repos/[^/[:space:]]+/[^/[:space:]]+/pulls/[0-9]+/reviews([[:space:]]|$)'
while IFS= read -r segment; do
  case "$segment" in
    *"gh api"*) ;;
    *) continue ;;
  esac
  method=""
  if printf '%s' "$segment" | grep -Eiq -- '(-X|--method)[[:space:]=]*(POST|PATCH|PUT|DELETE)'; then
    method="$(printf '%s' "$segment" | grep -Eio -- '(-X|--method)[[:space:]=]*(POST|PATCH|PUT|DELETE)' | head -1 | grep -Eio 'POST|PATCH|PUT|DELETE' | tr '[:lower:]' '[:upper:]')"
  elif printf '%s' "$segment" | grep -Eiq -- '(-X|--method)[[:space:]=]*(GET|HEAD)'; then
    method="GET"
  elif printf '%s' "$segment" | grep -Eq -- '(^|[[:space:]])(-f|-F|--field|--raw-field|--input)([[:space:]=]|$)'; then
    method="POST"
  fi
  [ -z "$method" ] || [ "$method" = "GET" ] && continue
  if [ "$method" = "POST" ] && printf '%s' "$segment" | grep -Eq -- "$review_endpoint"; then
    continue
  fi
  deny "gh api $method outside the review endpoint — the reviewer only posts the review (repos/<owner>/<repo>/pulls/<n>/reviews)"
done < <(printf '%s\n' "$normalized" | awk '{gsub(/&&|\|\||;|\|/, "\n"); print}')

exit 0
