# Output format — a GitHub review, written like a person

When the user asks you to review a pull request **someone else opened**, the review is **posted on the PR**: one GitHub review made of short inline comments on the exact lines they're about, plus one short summary comment. That's how experienced reviewers work — the author fixes each point where it lives, resolves the thread, and sees at a glance what's left. A long document at the end makes the author hunt for every `file:line`.

When the PR is the **user's own** — its author is the account `gh` is logged in as — never post anything on it, not a review and not a single comment: give the same shape in the chat. Check before writing the payload (`gh pr view <n> --json author --jq .author.login` against `gh api user --jq .login`); `hooks/check-own-pr-review.py` blocks the call anyway. When there's no PR (a local diff, a branch, a self-review before pushing), use the same shape in the chat too: the summary first, then each inline comment headed by its `path:line`.

## How a comment reads

Write the way a good senior engineer talks to a colleague: plain words, short sentences, one idea per comment. Explain what happens and why it matters in words anyone on the team can follow — no jargon walls, no lecture. The aim is that the author understands the problem the first time they read it and knows exactly what to change.

Every inline comment has the same shape:

1. **The severity, first, in bold:** `**Blocker:**`, `**Important:**`, `**Recommended:**`, or `**Nit:**`.
2. **What happens**, in one or two sentences — the cause and the consequence, concretely ("an email like `' OR '1'='1` matches every row and returns someone else's account").
3. **What to do about it** — the fix in a sentence, and a ` ```suggestion ` block when the fix fits in the commented lines, so the author can apply it with one click.
4. **Evidence when you have it** — what you ran or measured, or the other file that makes this a problem (`login.py:70 updates the same row`).

Most comments are two to five sentences. If a comment needs more, the point is probably two points.

A real example of the shape (a maintainer's comment on a lock held too long), adapted:

> **Blocker:** this lock stays on every user row until the whole sweep commits, because both callers run the sweep in one transaction (`main.py:552`, `preload.py:282`). Logins write `last_login_at` on that same row, so a login on another pod waits for the entire sweep — I measured 4.7 s with 1,000 users, against 0.01 s before. Committing after each user (and rolling back in the per-user `except`) keeps each lock to one user, like `initialize_all_user_variables` already does.

## The severity labels

| Label | Use it when | It means for the author |
|---|---|---|
| `**Blocker:**` | It meets the Blocker bar in `SKILL.md` (security defect, data loss/PII, broken build or tests, untested high-risk path, a regression that makes user requests wait or fail) | Must change before merge |
| `**Important:**` | A real defect or risk below that bar | Should be fixed in this PR |
| `**Recommended:**` | Worth doing; fine as a follow-up | Author's call on timing |
| `**Nit:**` | Polish: naming, a simpler idiom, a leftover import | Take it or leave it |

The label is the only label. No finding IDs (`B1`, `I2`), no emoji, no `**File:**` / `**Issue:**` / `**Fix:**` lines — the rest is prose. When in doubt between two labels, pick the lower one.

## The summary comment

The review's top-level body is short — usually three to six sentences, like a colleague's note:

- **What you did:** what you read, traced, ran, or measured ("I ran the new test file against PostgreSQL 16 and SQLite; on the base it fails 3/3, on the PR it passes").
- **The verdict in plain words:** "Looks good to merge", "Good to merge — a couple of things worth fixing", or "One thing needs to change before merge: …". It follows the verdict rule in `SKILL.md`.
- **Findings that have no line to point at:** a missing test, a file that should be in a CI workflow the PR didn't touch, a problem in code outside the diff. Each gets a sentence or two with its severity label in bold at the start, exactly like an inline comment.

Don't repeat the inline comments in the summary. If everything is inline, the summary is just what you did and the verdict.

## What goes inline and what goes in the summary

GitHub only accepts inline comments on lines that are part of the PR's diff (the changed lines and the context lines around them, on the new side). Put a finding inline when you can point at a line in the diff that the author would change to fix it. Otherwise it goes in the summary, citing where the problem is ("`migration-validation.yml` lists test files explicitly, and this one isn't there").

A finding about code outside the diff that the PR makes dangerous — a caller, another writer of the same row — goes **inline on the changed line that creates the danger**, and the comment names the other file.

## Posting the review

Post **one** review per pass, so the author gets one notification and the comments arrive together.

1. **List the lines you can comment on.** A comment on a line outside the diff makes GitHub reject the **entire** review with `422` (`Path could not be resolved` for a file not in the PR, `Line could not be resolved` for a line outside the hunks), and nothing is posted. List the commentable lines first:

   ```bash
   python3 - <owner/repo> <number> <<'PY'
   import json, re, subprocess, sys
   repo, number = sys.argv[1], sys.argv[2]
   raw = subprocess.run(["gh", "api", "--paginate", f"repos/{repo}/pulls/{number}/files"], capture_output=True, text=True, check=True).stdout
   for f in json.loads(raw.replace("][", ",")):
       spans = [(int(m.group(1)), int(m.group(1)) + int(m.group(2) or 1) - 1) for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", f.get("patch", ""), re.M)]
       print(f["filename"], ", ".join(f"{a}-{b}" for a, b in spans) or "(no commentable lines)")
   PY
   ```

   Move any finding whose line isn't listed to the summary.

2. **Write the payload** to a temporary file (outside the repository): the head commit, the event, the summary body, and the comments. Line numbers are the new file's lines (`"side": "RIGHT"`); a range uses `start_line` and `line`.

   ```json
   {
     "commit_id": "<head sha from gh pr view <n> --json headRefOid>",
     "event": "COMMENT",
     "body": "<summary>",
     "comments": [
       {"path": "src/users.py", "line": 5, "side": "RIGHT", "body": "**Blocker:** …"},
       {"path": "src/users.py", "start_line": 14, "start_side": "RIGHT", "line": 15, "side": "RIGHT", "body": "**Important:** …"}
     ]
   }
   ```

3. **Post it:**

   ```bash
   gh api -X POST repos/<owner>/<repo>/pulls/<number>/reviews --input <payload.json>
   ```

   Then report the review's URL (`html_url` in the response) to the user.

**The event is `COMMENT` by default.** The verdict lives in the summary's words. Use `APPROVE` or `REQUEST_CHANGES` only when the user asks for it — they carry the user's name into the merge rules — and never `REQUEST_CHANGES` on a PR the user authored (GitHub refuses it with `422`).

**Before posting, read what's already on the PR** (`gh api repos/<owner>/<repo>/pulls/<number>/comments` and the reviews). Don't repeat a point someone already made — a maintainer, a teammate, or a bot. Agree or disagree with it in a sentence of the summary if it matters. On a second pass over the same PR, comment only on what's new or still unresolved.

## Mechanics that keep it clean

- Write in the PR's language (its title, description, and discussion decide): a pt-BR PR gets a pt-BR review, an English PR gets English; mixed or unclear defaults to English. Code identifiers, paths, and quoted code stay verbatim.
- Never `#N` in prose (GitHub links it to an unrelated issue or PR), never `Fixes/Closes/Resolves #N` (it closes issues on merge), never `@mentions` unless the user asks.
- Never absolute local paths; repo-relative paths only.
- Never hard-wrap prose: a paragraph is one line; Enter only between paragraphs, list items, and code fences.
- Quote at most a few lines of code; the inline anchor already shows the code.
- `suggestion` blocks replace exactly the commented lines — include every line of the range, with the original indentation.

## Before posting — the checklist

- [ ] Each inline comment opens with its bold severity label, then says what happens and what to do, in plain words.
- [ ] Every inline line is in the commentable-lines list; everything else is in the summary.
- [ ] The summary says what you did and the verdict, and doesn't repeat the inline comments.
- [ ] The verdict isn't inflated: only true Blockers are labeled `**Blocker:**`.
- [ ] No duplicate of a point already on the PR.
- [ ] The event is `COMMENT` unless the user asked otherwise.
- [ ] No `#N`, `@mentions`, local paths, or hard-wrapped lines.
