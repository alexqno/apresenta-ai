#!/usr/bin/env python3
"""Check and install presentation skill releases atomically."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from types import SimpleNamespace
from urllib.parse import quote
from urllib.request import urlopen
from zipfile import ZipFile
import io


OWNER = "alexqno"
REPOSITORY = "apresenta-ai"
SKILLS = ("apresenta-ai", "apresenta-design", "apresenta-interacao")
CORE_SKILLS = ("apresenta-ai", "apresenta-design")
REF_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


class UpdateError(RuntimeError):
    pass


def read_version(skill_dir: Path) -> str:
    try:
        version = json.loads((skill_dir / "version.json").read_text(encoding="utf-8"))["version"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        raise UpdateError(f"Versão inválida em {skill_dir}.") from error
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise UpdateError(f"Versão inválida em {skill_dir}.")
    return version


def skill_versions(source_dir: Path) -> dict[str, str]:
    versions = {skill: read_version(source_dir / skill) for skill in SKILLS}
    if len({versions[skill] for skill in CORE_SKILLS}) != 1:
        raise UpdateError("apresenta-ai e apresenta-design precisam usar a mesma versão.")
    for skill in SKILLS:
        if not (source_dir / skill / "SKILL.md").is_file():
            raise UpdateError(f"SKILL.md ausente em {skill}.")
    return versions


def source_version(source_dir: Path) -> dict[str, str]:
    return skill_versions(source_dir)


def installed_version(destination_dir: Path) -> dict[str, str | None] | None:
    present = {skill: (destination_dir / skill).is_dir() for skill in SKILLS}
    if not any(present.values()):
        return None
    if not all(present[skill] for skill in CORE_SKILLS):
        raise UpdateError("apresenta-ai e apresenta-design precisam estar instaladas juntas.")
    versions = {skill: read_version(destination_dir / skill) if present[skill] else None for skill in SKILLS}
    if versions["apresenta-ai"] != versions["apresenta-design"]:
        raise UpdateError("apresenta-ai e apresenta-design instaladas usam versões diferentes.")
    return versions


def version_label(versions: dict[str, str | None] | None) -> str:
    if not versions:
        return "nenhuma"
    return (f"apresenta-ai/apresenta-design: {versions['apresenta-ai']}; "
            f"apresenta-interacao: {versions['apresenta-interacao'] or 'não instalada'}")


def update_from_source(source_dir: Path, destination_dir: Path, check_only: bool) -> SimpleNamespace:
    available = source_version(source_dir)
    installed = installed_version(destination_dir)
    if check_only or installed == available:
        return SimpleNamespace(available=available, installed=installed, updated=False)

    destination_dir.mkdir(parents=True, exist_ok=True)
    transaction_dir = Path(tempfile.mkdtemp(prefix="apresenta-update-", dir=destination_dir.parent))
    staging_dir = transaction_dir / "staging"
    backup_dir = transaction_dir / "backup"
    try:
        for skill in SKILLS:
            shutil.copytree(source_dir / skill, staging_dir / skill)
        skill_versions(staging_dir)

        for skill in SKILLS:
            installed_skill = destination_dir / skill
            if installed_skill.exists():
                shutil.move(str(installed_skill), str(backup_dir / skill))
        for skill in SKILLS:
            shutil.move(str(staging_dir / skill), str(destination_dir / skill))
    except Exception as error:
        for skill in SKILLS:
            installed_skill = destination_dir / skill
            if installed_skill.exists():
                shutil.rmtree(installed_skill)
            backup_skill = backup_dir / skill
            if backup_skill.exists():
                shutil.move(str(backup_skill), str(installed_skill))
        raise UpdateError("Atualização falhou; instalação anterior foi restaurada.") from error
    finally:
        shutil.rmtree(transaction_dir, ignore_errors=True)
    return SimpleNamespace(available=available, installed=installed, updated=True)


def download_source(ref: str, temporary_dir: Path) -> Path:
    if not REF_PATTERN.fullmatch(ref):
        raise UpdateError("Ref inválida.")
    url = f"https://codeload.github.com/{OWNER}/{REPOSITORY}/zip/{quote(ref)}"
    try:
        with urlopen(url, timeout=30) as response:
            archive = ZipFile(io.BytesIO(response.read()))
            top_levels = {name.split("/", 1)[0] for name in archive.namelist() if name}
            if len(top_levels) != 1:
                raise UpdateError("Arquivo remoto tem estrutura inválida.")
            root = temporary_dir / top_levels.pop()
            root_parent = temporary_dir.resolve()
            for member in archive.namelist():
                target = (temporary_dir / member).resolve()
                if target != root_parent and root_parent not in target.parents:
                    raise UpdateError("Arquivo remoto contém caminho inseguro.")
            archive.extractall(temporary_dir)
    except UpdateError:
        raise
    except Exception as error:
        raise UpdateError("Não foi possível baixar atualização.") from error
    return root


def parse_args(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Atualiza as skills de apresentação juntas.")
    parser.add_argument("--check", action="store_true", help="Somente informa a versão disponível.")
    parser.add_argument("--yes", action="store_true", help="Confirma a substituição da instalação.")
    parser.add_argument("--ref", default="master", help="Branch ou tag publicada (padrão: master).")
    parser.add_argument("--source-dir", type=Path, help="Origem local para testes ou instalação offline.")
    parser.add_argument("--dest", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments or sys.argv[1:])
    if args.check and args.yes:
        raise UpdateError("Use somente --check ou --yes.")
    with tempfile.TemporaryDirectory(prefix="apresenta-download-") as temporary_dir:
        source = args.source_dir or download_source(args.ref, Path(temporary_dir))
        result = update_from_source(source, args.dest, check_only=not args.yes)
    if result.updated:
        print(f"Atualizado para {version_label(result.available)}.")
    elif result.installed == result.available:
        print(f"Já está em {version_label(result.available)}.")
    else:
        print(f"Instalada: {version_label(result.installed)}; disponível: {version_label(result.available)}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UpdateError as error:
        print(f"Erro: {error}", file=sys.stderr)
        raise SystemExit(2)
