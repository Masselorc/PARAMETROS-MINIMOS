"""Corrige SVGs das bandeiras para renderizacao como <img> estatico.

Causa raiz (Chromium como <img>): arquivos que usam `xlink:href` sem
declarar `xmlns:xlink` falham silenciosamente (naturalWidth 0). Afetava
ma, mt, to, pi, rj. Correcao minima, sem alterar desenho:
- declara xmlns:xlink quando o arquivo usa xlink: sem declarar;
- remove DOCTYPE (rj, ma, ro);
- garante width/height 100% quando ha viewBox (escala no <img>).

Idempotente; faz backup .bak uma vez por arquivo.
Uso: python tools/fix_flags_pi_rj.py
"""
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent.parent
FLAGS = BASE / "static" / "bandeiras"

# Apenas os arquivos quebrados no Chromium como <img> (xlink: sem xmlns).
# PI e RJ foram corrigidos no commit anterior; manter a lista mínima evita
# tocar nos arquivos que já funcionavam (am, es, PR etc.).
TARGETS = ("ma.svg", "mt.svg", "to.svg")

XLINK = "http://www.w3.org/1999/xlink"


def fix(text: str) -> str:
    if "xlink:" in text and "xmlns:xlink" not in text:
        text = text.replace("<svg ", f'<svg xmlns:xlink="{XLINK}" ', 1)
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text, count=1)
    return text


def main() -> None:
    for path in sorted(FLAGS.glob("*.svg")):
        if path.name not in TARGETS:
            continue
        original = path.read_text(encoding="utf-8")
        bak = path.with_suffix(".svg.bak")
        if not bak.exists():
            bak.write_text(original, encoding="utf-8")
        had_newline = original.endswith("\n")
        fixed = fix(original).rstrip("\r\n") + ("\n" if had_newline else "")
        if fixed != original:
            path.write_text(fixed, encoding="utf-8")
            print(f"{path.name}: {len(original)} -> {len(fixed)} bytes (corrigido)")
        else:
            print(f"{path.name}: ok, sem alteracao")


if __name__ == "__main__":
    main()
