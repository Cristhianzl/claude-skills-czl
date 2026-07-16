# Langflow frontend i18n — mechanics

Langflow-specific i18n knowledge, owned by this config. The two rules are in `CLAUDE.md` (mandatory): every user-facing string goes through the translation system, and **every new key lands in ALL locale files in the same PR**.

## How it works here

- **Stack:** i18next + react-i18next. Config: `src/frontend/src/i18n.ts` (custom instance).
- **Locales:** `src/frontend/src/locales/` — `en`, `de`, `es`, `fr`, `ja`, `pt`, `zh-Hans`. `en` is bundled statically; the others are **lazy-loaded** by `loadLanguage()` via dynamic import. Preference comes from `localStorage.getItem("languagePreference")`, normalized (`zh-CN` → `zh-Hans`, unknown → `en`).
- **Keys are flat, dot-namespaced by feature**: `deleteModal.title`, `errors.fileTooLarge`. Follow the existing namespace of the area; new prefix only for a genuinely new surface.
- **The trap:** `fallbackLng: "en"` means a key missing from another locale **silently shows English** — it never crashes, which is exactly why review must catch it.

## The pattern

```tsx
import { useTranslation } from "react-i18next";

const { t } = useTranslation();

<span>{t("deleteModal.title")}</span>
<p>{t("errors.fileTooLarge", { maxSizeMB: "10MB" })}</p>
```

Add the key to `locales/en.json` **and every other locale file**. Write a real translation when confident; otherwise add the key with the English value and flag it in the PR — present-but-untranslated is visible and searchable, missing is invisible.

## Rules that prevent real bugs

- **Never concatenate translated fragments** (`t("a") + name + t("b")`) — word order differs per language. One key with interpolation: `t("greeting", { name })`.
- **No JSX/HTML inside translation strings** — compose in JSX around `t()` calls (see how `crash.descriptionBefore` / `crash.githubIssues` / `crash.descriptionAfter` split around a link).
- **Plurals** via i18next forms (`_one` / `_other`), not `count === 1 ? ... : ...`.
- **Keys are code:** rename/delete = update **all seven** locale files. An orphan in one file is dead weight; a rename missed in one is a regression.
- Dates/numbers/currency: `Intl.*` with the active locale, never hardcoded formats.

## Review one-liner

Lists the locale files where a key is **missing** (should print nothing):

```bash
for f in src/frontend/src/locales/*.json; do grep -L '"my.new.key"' "$f"; done
```
