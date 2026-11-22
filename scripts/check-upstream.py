#!/usr/bin/env python3
"""Check the packaged verifier source against the pinned upstream release."""

import argparse
import hashlib
from pathlib import Path
import tarfile
import tomllib


UPSTREAM = "risc0-circuit-recursion-4.0.4"
UPSTREAM_SHA256 = "2347e909c6b2a65584b5898f3802eec5b8c1b4b45329edfdd8587b6a04dd3357"
PACKAGE_NAME = "kaspa-r0-recursion-legacy"
SOURCES = {
    "src/control_id.rs",
    "src/info.rs",
    "src/layout.rs",
    "src/layout.rs.inc",
    "src/lib.rs",
    "src/poly_ext.rs",
    "src/taps.rs",
}
METADATA = {"Cargo.lock", "Cargo.toml", "LICENSE", "README.md"}
GENERATED_METADATA = {".cargo_vcs_info.json", "Cargo.toml.orig"}
DEPENDENCIES = {
    "risc0-core": {"version": "=3.0.1", "default-features": False},
    "risc0-zkp": {"version": "=3.0.4", "default-features": False},
    "risc0-zkvm-platform": {"version": "=2.2.2", "default-features": False},
}


def check(upstream_path: Path, package_path: Path) -> None:
    digest = hashlib.sha256(upstream_path.read_bytes()).hexdigest()
    if digest != UPSTREAM_SHA256:
        raise ValueError(f"{UPSTREAM} checksum mismatch: got {digest}")

    with tarfile.open(upstream_path) as upstream, tarfile.open(package_path) as package:
        root = set()
        files = {}
        for member in package.getmembers():
            folder, _, path = member.name.partition("/")
            if not member.isfile() or not path or path in files:
                raise ValueError(f"Invalid package member: {member.name}")
            root.add(folder)
            files[path] = member

        required = SOURCES | METADATA
        missing = required - files.keys()
        extra = files.keys() - required - GENERATED_METADATA
        if missing or extra:
            raise ValueError(f"Package files differ: missing {sorted(missing)}, extra {sorted(extra)}")

        manifest = tomllib.load(package.extractfile(files["Cargo.toml"]))
        metadata = manifest["package"]
        if metadata["name"] != PACKAGE_NAME or root != {f"{PACKAGE_NAME}-{metadata['version']}"}:
            raise ValueError("Unexpected package name or archive root")
        if (
            metadata["edition"] != "2021"
            or metadata.get("build") is not False
            or manifest["lib"] != {"name": "risc0_circuit_recursion", "path": "src/lib.rs"}
            or manifest.get("dependencies") != DEPENDENCIES
            or manifest.keys() - {"package", "lib", "dependencies", "lints"}
        ):
            raise ValueError("Packaged manifest differs from the verifier configuration")

        for path in sorted(SOURCES):
            original = upstream.extractfile(f"{UPSTREAM}/{path}").read()
            if package.extractfile(files[path]).read() != original:
                raise ValueError(f"Source differs from {UPSTREAM}: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream", type=Path, help="Upstream 4.0.4 .crate archive")
    parser.add_argument("package", type=Path, help="Packaged Kaspa verifier .crate archive")
    args = parser.parse_args()
    try:
        check(args.upstream, args.package)
    except (KeyError, OSError, ValueError, tarfile.TarError) as error:
        parser.exit(1, f"Package verification failed: {error}\n")
    print(f"All {len(SOURCES)} packaged sources match {UPSTREAM} byte for byte.")


if __name__ == "__main__":
    main()
