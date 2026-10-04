"""Package the count firmware with a release-band boot priority.

Dirty development images normally outrank every stock release. This explicit
packaging step retains the custom version tag while allowing future stock
versions to outrank the image. It changes only the priority and manifest CRC.
"""

import argparse
import importlib.util
import json
import struct
import zipfile
import zlib
from pathlib import Path


def set_boot_priority(image, priority):
    if len(image) < 28:
        raise ValueError("Truncated PBLBOOT header")
    magic, header_len, old_priority, offset, body_len, body_crc = struct.unpack_from(
        "<IIQIII", image
    )
    if magic != 0x96F3B83D or header_len != 28:
        raise ValueError("Invalid PBLBOOT header")
    if offset < header_len or offset + body_len != len(image):
        raise ValueError("Invalid PBLBOOT image bounds")
    if zlib.crc32(image[offset:]) & 0xFFFFFFFF != body_crc:
        raise ValueError("Invalid firmware body CRC")
    if not 0 <= priority < 2**64:
        raise ValueError("Priority must fit in uint64")
    result = bytearray(image)
    struct.pack_into("<Q", result, 8, priority)
    assert result[:8] == image[:8] and result[16:] == image[16:]
    return bytes(result), old_priority


def _load_tool(repo, name):
    spec = importlib.util.spec_from_file_location(name, repo / "tools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def package_firmware(source, target, repo, build_timestamp):
    boot = _load_tool(repo, "pblboot")
    stm32 = _load_tool(repo, "stm32_crc")
    priority = boot.boot_priority("v4.38.4", build_timestamp)
    with zipfile.ZipFile(source) as zin:
        if zin.testzip() is not None:
            raise ValueError("Invalid source archive")
        manifest = json.loads(zin.read("manifest.json"))
        fw = manifest["firmware"]
        base_commit = "450127bd2e4ce39baf2e97e5d87d5e937cdbbfe9"
        matches_base = len(fw["commit"]) >= 7 and base_commit.startswith(fw["commit"])
        if fw["versionTag"] != "v4.38.4-dirty" or not matches_base:
            raise ValueError("Expected the modified, exact v4.38.4 base")
        if fw["hwrev"] not in ("obelix_pvt", "obelix_dvt") or fw["slot"] not in (0, 1):
            raise ValueError("Unexpected Time 2 hardware or slot")
        for section in ("firmware", "resources"):
            entry = manifest[section]
            data = zin.read(entry["name"])
            if len(data) != entry["size"] or stm32.crc32(data) != entry["crc"]:
                raise ValueError("Invalid source payload size or CRC")
        if not boot.boot_priority("v4.38.4", fw["timestamp"]) < priority:
            raise ValueError("Custom image must outrank the existing release timestamp")
        assert priority < boot.boot_priority("v4.38.5", 0)
        original = zin.read(fw["name"])
        patched, old_priority = set_boot_priority(original, priority)
        fw["crc"] = stm32.crc32(patched)
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
            for name in zin.namelist():
                if name == fw["name"]:
                    data = patched
                elif name == "manifest.json":
                    data = (json.dumps(manifest, indent=2) + "\n").encode()
                else:
                    data = zin.read(name)
                zout.writestr(name, data)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert stm32.crc32(z.read(fw["name"])) == fw["crc"]
        assert struct.unpack_from("<Q", z.read(fw["name"]), 8)[0] == priority
    return {
        "file": target.name,
        "hardware": fw["hwrev"],
        "slot": fw["slot"],
        "version": fw["versionTag"],
        "firmware_size": fw["size"],
        "firmware_crc": fw["crc"],
        "resources_crc": manifest["resources"]["crc"],
        "original_priority_hex": hex(old_priority),
        "replacement_priority_hex": hex(priority),
        "priority_timestamp_utc": build_timestamp,
        "priority_policy": "release-band v4.38.4 plus packaging timestamp",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--firmware-repo", type=Path, required=True)
    parser.add_argument("--build-timestamp", type=int, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            package_firmware(
                args.source, args.target, args.firmware_repo, args.build_timestamp
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
