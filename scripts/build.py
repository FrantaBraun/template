#!/usr/bin/env python3
"""
Build and upload script for backend, frontend and deployment scripts.

Usage:
    python scripts/build.py --mode STABLE --target backend [--tag B-1.2.3]
    python scripts/build.py --mode STABLE --target frontend [--tag F-1.2.3]
    python scripts/build.py --mode STABLE --target scripts
    python scripts/build.py --mode STABLE --target all
    python scripts/build.py --mode SNAPSHOT --target all
    python scripts/build.py --mode SNAPSHOT --target backend --no-upload

Tags must follow the convention:  B-x.y.z  (backend)  /  F-x.y.z  (frontend)
The 'scripts' target has no tag — it always bundles the current filesystem state.
Configuration is read from scripts/build.config.toml (see build.config.toml.example).
"""

import argparse
import ftplib
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPTS_DIR / "build.config.toml"


# ─── Config ───────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        sys.exit(
            f"Config file not found: {CONFIG_FILE}\n"
            "Copy scripts/build.config.toml.example and fill in your values."
        )
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


# ─── Git helpers ──────────────────────────────────────────────────────────────

def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def latest_tag(prefix: str) -> str:
    """Return the highest semver tag matching  PREFIX-x.y.z."""
    tags = git("tag", "--list", f"{prefix}-*").splitlines()
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)\.(\d+)\.(\d+)$")
    versioned = []
    for tag in tags:
        m = pattern.match(tag)
        if m:
            versioned.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), tag))
    if not versioned:
        sys.exit(f"No tags found matching {prefix}-x.y.z")
    return sorted(versioned)[-1][3]


def short_hash() -> str:
    return git("rev-parse", "--short", "HEAD")


def git_archive_bytes(ref: str, subtree: str) -> bytes:
    """Return raw zip bytes of  ref:subtree  (files at archive root, no prefix)."""
    proc = subprocess.run(
        ["git", "archive", "--format=zip", f"{ref}:{subtree}"],
        cwd=ROOT, capture_output=True,
    )
    if proc.returncode != 0:
        sys.exit(f"git archive {ref}:{subtree} failed:\n{proc.stderr.decode().strip()}")
    return proc.stdout


# ─── Build: backend ───────────────────────────────────────────────────────────

def build_backend(ref: str, output_path: Path) -> None:
    print(f"  Archiving backend/ from {ref} …")
    output_path.write_bytes(git_archive_bytes(ref, "backend"))
    size_kb = output_path.stat().st_size // 1024
    print(f"  Created {output_path.name}  ({size_kb} KB)")


# ─── Build: scripts ───────────────────────────────────────────────────────────

_DEPLOY_CONFIG         = SCRIPTS_DIR / "deploy.config.sh"
_DEPLOY_CONFIG_EXAMPLE = SCRIPTS_DIR / "deploy.config.sh.example"
_SCRIPT_FILES          = ["install.sh", "upgrade.sh", "./../backend/.env"]


def build_scripts(output_path: Path) -> None:
    if _DEPLOY_CONFIG.exists():
        config_src = _DEPLOY_CONFIG
        config_label = "deploy.config.sh"
    else:
        config_src = _DEPLOY_CONFIG_EXAMPLE
        config_label = "deploy.config.sh.example → deploy.config.sh"
        print("  WARNING: deploy.config.sh not found — bundling example as placeholder.")

    print("  Bundling deployment scripts …")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in _SCRIPT_FILES:
            src = (SCRIPTS_DIR / name).resolve()
            arcname = src.name   # store as bare filename, no path traversal
            if not src.exists():
                sys.exit(f"File not found: {src}")
            z.write(src, arcname)
            print(f"    + {arcname}")
        z.write(config_src, "deploy.config.sh")
        print(f"    + deploy.config.sh  (from {config_label})")

    size_kb = output_path.stat().st_size // 1024
    print(f"  Created {output_path.name}  ({size_kb} KB)")


# ─── Build: frontend ──────────────────────────────────────────────────────────

def build_frontend(ref: str, output_path: Path, cfg: dict) -> None:
    npm = shutil.which("npm") or cfg.get("build", {}).get("npm_command", "npm")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        src = tmp / "src"
        src.mkdir()

        print(f"  Extracting frontend/ from {ref} …")
        zip_data = git_archive_bytes(ref, "frontend")
        archive = tmp / "src.zip"
        archive.write_bytes(zip_data)
        with zipfile.ZipFile(archive) as z:
            z.extractall(src)

        with open(src / ".env", "w") as f:
            f.write("""# Base URL of the auth service API (no trailing slash)
VITE_API_URL=https://auth.withfbraun.com

# Base URL of this frontend app (used for OAuth callbacks, email links)
VITE_APP_URL=https://auth.withfbraun.com""")
        print(src, src / ".env")
        print("  npm install …")
        subprocess.run([npm, "install", "--prefer-offline"], cwd=src, check=True)

        print("  npm run build …")
        subprocess.run([npm, "run", "build"], cwd=src, check=True)

        dist = src / "dist"
        if not dist.exists():
            sys.exit("Frontend build did not produce a dist/ directory.")

        print(f"  Zipping dist/ → {output_path.name} …")
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
            for file in sorted(dist.rglob("*")):
                if file.is_file():
                    z.write(file, file.relative_to(dist))

    size_kb = output_path.stat().st_size // 1024
    print(f"  Created {output_path.name}  ({size_kb} KB)")


# ─── FTP upload ───────────────────────────────────────────────────────────────

def _ftp_mkdirs(ftp: ftplib.FTP, remote_dir: str) -> None:
    parts = remote_dir.strip("/").split("/")
    current = ""
    for part in parts:
        current += f"/{part}"
        try:
            ftp.cwd(current)
        except ftplib.error_perm:
            ftp.mkd(current)
            ftp.cwd(current)


def upload_ftp(local_path: Path, remote_dir: str, cfg: dict) -> None:
    fc = cfg["ftp"]
    host, port = fc["host"], fc.get("port", 21)
    use_tls = fc.get("tls", False)

    print(f"  Uploading → ftp{'s' if use_tls else ''}://{host}{remote_dir}/{local_path.name} …")

    FTPClass = ftplib.FTP_TLS if use_tls else ftplib.FTP
    with FTPClass() as ftp:
        ftp.connect(host, port, timeout=30)
        ftp.login(fc["user"], fc["password"])
        if use_tls:
            ftp.prot_p()
        ftp.set_pasv(fc.get("passive", True))

        _ftp_mkdirs(ftp, remote_dir)

        with open(local_path, "rb") as f:
            ftp.storbinary(f"STOR {local_path.name}", f)

    print(f"  Upload complete.")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def resolve_ref(mode: str, target: str, tag: str | None) -> str:
    if mode == "SNAPSHOT" or target == "scripts":
        return "HEAD"
    if tag:
        return tag
    prefix = "B" if target == "backend" else "F"
    ref = latest_tag(prefix)
    print(f"  Latest tag: {ref}")
    return ref


def zip_name(mode: str, target: str, ref: str) -> str:
    date = datetime.now().strftime("%Y%m%d")
    if target == "scripts":
        if mode == "STABLE":
            return f"auth-scripts-{date}.zip"
        return f"auth-scripts-snapshot-{date}-{short_hash()}.zip"
    if mode == "STABLE":
        return f"{target}-{ref}.zip"
    return f"{target}-snapshot-{date}-{short_hash()}.zip"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and upload backend/frontend packages.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--mode", choices=["STABLE", "SNAPSHOT"], required=True,
                        help="STABLE builds from a git tag; SNAPSHOT from HEAD.")
    parser.add_argument("--target", choices=["backend", "frontend", "scripts", "all"], required=True)
    parser.add_argument("--tag",
                        help="Specific tag (e.g. B-1.2.3 or F-1.2.3). "
                             "Only for STABLE backend/frontend; incompatible with scripts and all.")
    parser.add_argument("--no-upload", action="store_true",
                        help="Build locally without FTP upload.")
    parser.add_argument("--output-dir", type=Path, metavar="DIR",
                        help="Override output directory from config.")
    args = parser.parse_args()

    if args.tag and args.target in ("all", "scripts"):
        parser.error("--tag cannot be combined with --target all or scripts "
                     "(tags are per-component; run backend and frontend separately).")
    if args.tag and args.mode == "SNAPSHOT":
        parser.error("--tag is only valid in STABLE mode.")

    cfg = load_config()
    out_dir_cfg = cfg.get("build", {}).get("output_dir", "dist")
    output_dir = args.output_dir or Path(out_dir_cfg)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = ["backend", "frontend", "scripts"] if args.target == "all" else [args.target]

    for target in targets:
        print(f"\n{'='*55}")
        print(f"  {target.upper()}  |  {args.mode}")
        print(f"{'='*55}")

        ref = resolve_ref(args.mode, target, args.tag)
        zname = zip_name(args.mode, target, ref)
        zip_path = output_dir / zname

        if target == "backend":
            build_backend(ref, zip_path)
            remote_dir = cfg["ftp"]["paths"]["backend"]
        elif target == "frontend":
            build_frontend(ref, zip_path, cfg)
            remote_dir = cfg["ftp"]["paths"]["frontend"]
        else:  # scripts
            build_scripts(zip_path)
            remote_dir = cfg["ftp"]["paths"]["scripts"]

        if not args.no_upload:
            upload_ftp(zip_path, remote_dir, cfg)
        else:
            print(f"  Upload skipped (--no-upload).")

    print(f"\nDone. Output: {output_dir}")


if __name__ == "__main__":
    main()
