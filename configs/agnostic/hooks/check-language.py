#!/usr/bin/env python3
# Why: the conversation language leaks into generated files when the user prompts in another language; the baseline rule alone does not stop it, so the delta of every write is checked mechanically.
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _hooklib import changed_lines, get_path, read_payload  # noqa: E402

TEXT_EXTS = {
    ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".java", ".kt", ".cs",
    ".rs", ".rb", ".swift", ".php", ".sql", ".sh", ".bash", ".md", ".mdx", ".rst", ".txt",
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".html", ".vue", ".svelte",
}
SKIP_PARTS = {"node_modules", ".venv", "venv", "__pycache__", "build", "dist", "target", ".next"}
# Why: product UI copy legitimately ships in the product's language; only translation catalogs are exempt.
I18N_PARTS = {"locale", "locales", "i18n", "intl", "lang", "langs", "translation", "translations", "messages"}
I18N_EXTS = {".po", ".pot", ".xliff", ".xlf", ".properties", ".arb"}
I18N_NAME_RE = re.compile(r"^[a-z]{2}([_-][A-Za-z]{2,4})?\.(json|ya?ml|ts|js)$")
# Why: this file's own marker tables are data, not prose, and would otherwise trip the rule they define.
SELF_NAME = "check-language.py"
ESCAPE_RE = re.compile(r"\b(i18n-ok|lang-ok)\b", re.IGNORECASE)

STRONG = {
    "não", "você", "vocês", "então", "também", "está", "estão", "são", "será", "já", "após", "até",
    "função", "funções", "configuração", "configurações", "usuário", "usuários", "endereço",
    "título", "descrição", "botão", "início", "número", "código", "página", "versão", "opção",
    "opções", "padrão", "válido", "inválido", "único", "próximo", "último", "mês", "análise",
    "referência", "parâmetro", "parâmetros", "obrigatório", "automático", "público", "permissão",
    "alteração", "criação", "exclusão", "atualização", "execução", "validação", "aplicação",
    "informação", "informações", "operação", "transação", "autenticação", "autorização",
    "implementação", "documentação", "integração", "serviço", "serviços", "negócio", "memória",
    "histórico", "relatório", "útil", "disponível", "possível", "necessário", "específico",
    "método", "módulo", "cálculo", "período", "critério", "domínio", "mínimo", "máximo",
    "contraseña", "señal", "año", "niño", "español", "aquí", "sí", "más", "días",
}
WEAK = {
    "arquivo", "arquivos", "senha", "cadastro", "quando", "porque", "pela", "pelo", "isso", "esse",
    "essa", "aquele", "seja", "deve", "sendo", "tabela", "consulta", "retorna", "dados", "campos",
    "nome", "nomes", "criar", "excluir", "atualizar", "buscar", "salvar", "enviar", "receber",
    "lista", "valores", "usuario", "archivo", "aunque", "pero", "aplicacion", "aqui",
}
WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]+")
MAX_REPORTED = 5
# Why: one accented marker is decisive on its own; unaccented ones overlap other languages, so several must agree.
STRONG_WEIGHT = 3
WEAK_WEIGHT = 1
BLOCK_SCORE = 3


def should_skip(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_EXTS:
        return True
    if path.name == SELF_NAME:
        return True
    lowered = {part.lower() for part in path.parts}
    if lowered & SKIP_PARTS or lowered & I18N_PARTS:
        return True
    if path.suffix.lower() in I18N_EXTS or I18N_NAME_RE.match(path.name):
        return True
    return False


def scan(content: str, targets: set[int] | None) -> tuple[int, list[str]]:
    score = 0
    hits: list[str] = []
    for lineno, raw in enumerate(content.splitlines(), start=1):
        if targets is not None and lineno not in targets:
            continue
        if ESCAPE_RE.search(raw):
            continue
        words = {word.lower() for word in WORD_RE.findall(raw)}
        found_strong = sorted(words & STRONG)
        found_weak = sorted(words & WEAK)
        if not found_strong and not found_weak:
            continue
        score += STRONG_WEIGHT * len(found_strong) + WEAK_WEIGHT * len(found_weak)
        marked = ", ".join((found_strong + found_weak)[:3])
        hits.append(f"{lineno}: {raw.strip()[:110]}  ->  {marked}")
    return score, hits


def main() -> None:
    data = read_payload()
    if data.get("tool_name") not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)
    path = get_path(data)
    if path is None or not path.exists() or should_skip(path):
        sys.exit(0)
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        sys.exit(0)

    score, hits = scan(content, changed_lines(data, content))
    if score < BLOCK_SCORE:
        sys.exit(0)

    print(f"Language violation: {path} contains non-English text.", file=sys.stderr)
    for hit in hits[:MAX_REPORTED]:
        print(f"  - {hit}", file=sys.stderr)
    if len(hits) > MAX_REPORTED:
        print(f"  - ... and {len(hits) - MAX_REPORTED} more line(s)", file=sys.stderr)
    print(
        "\nRule: the conversation language never sets the output language. Code, comments, identifiers, "
        "docs, and commit messages are always English, even when the user prompts in another language. "
        "Rewrite the lines above in English.\n"
        "Exception: product UI copy in an i18n catalog (locales/, i18n/, *.po, pt-BR.json) — move the string "
        "there, or mark a deliberate line with 'i18n-ok'.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
