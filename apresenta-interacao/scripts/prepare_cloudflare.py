#!/usr/bin/env python3
"""Prepara publicação Cloudflare com assets declarados para uma apresentação."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


TEMPLATE = Path(__file__).parents[1] / "assets" / "cloudflare"


class PreparationError(RuntimeError):
    pass


def safe_files(root: Path, values: object, label: str) -> list[str]:
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise PreparationError(f"Lista de assets {label} inválida.")
    output: list[str] = []
    for value in values:
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise PreparationError(f"Caminho de asset inválido: {value}")
        source = (root / relative).resolve()
        if root != source and root not in source.parents:
            raise PreparationError(f"Caminho de asset fora da raiz: {value}")
        if not source.is_file():
            raise PreparationError(f"Asset não encontrado: {value}")
        output.append(relative.as_posix())
    return output


def prepare(presentation: Path, design: Path, worker_name: str, manifest_path: Path, force: bool) -> Path:
    presentation = presentation.resolve()
    design = design.resolve()
    if not presentation.is_dir() or not design.is_dir():
        raise PreparationError("Apresentação ou design não encontrado.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PreparationError("Manifesto de assets inválido.") from error
    if not isinstance(manifest, dict):
        raise PreparationError("Manifesto de assets inválido.")
    assets = {
        "deck": safe_files(presentation, manifest.get("deck"), "do deck"),
        "design": safe_files(design, manifest.get("design"), "do design"),
    }
    target = presentation / "cloudflare"
    if target.exists():
        if not force:
            raise PreparationError("cloudflare/ já existe; use --force após revisar alterações locais.")
        shutil.rmtree(target)
    shutil.copytree(TEMPLATE, target)
    (target / "wrangler.jsonc").write_text(
        (target / "wrangler.jsonc").read_text(encoding="utf-8").replace("__WORKER_NAME__", worker_name), encoding="utf-8"
    )
    (target / "assets-manifest.json").write_text(json.dumps(assets, indent=2) + "\n", encoding="utf-8")
    (target / "deploy-config.json").write_text(json.dumps({
        "deck": presentation.name,
        "design": design.name,
        "presentationRoot": "..",
        "designRoot": str(Path("../..") / "designs" / design.name),
    }, indent=2) + "\n", encoding="utf-8")
    (target / "src" / "config.ts").write_text(f'export const DEFAULT_DECK = "{presentation.name}";\n', encoding="utf-8")
    result = subprocess.run(["node", "build.mjs"], cwd=target, capture_output=True, text=True)
    if result.returncode:
        raise PreparationError(result.stderr.strip() or "Build de assets falhou.")
    return target


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepara Worker Cloudflare para uma apresentação interativa.")
    parser.add_argument("--presentation", required=True, type=Path)
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--worker-name", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(arguments)
    if not args.worker_name.replace("-", "").isalnum() or args.worker_name.startswith("-"):
        raise PreparationError("Nome do Worker inválido.")
    target = prepare(args.presentation, args.design, args.worker_name, args.manifest, args.force)
    print(f"Cloudflare preparado em {target}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PreparationError as error:
        print(f"Erro: {error}", file=sys.stderr)
        raise SystemExit(2)
