# /// script
# requires-python = ">=3.13"
# dependencies = ["ocx-mirror-sdk~=0.6.0"]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 The OCX Authors

"""Generate url_index JSON for protoc.

WHY THIS EXISTS — the native `github_release` source cannot mirror protobuf.

protobuf tags its compiler releases with a TWO-component version (`v33.0`,
`v34.2`, `v35.1`); there is no three-component release tag anywhere in the
supported range. ocx-mirror's version parser requires full `X.Y.Z`, and the
failure is SILENT — every version is warned past and the run exits 0:

    $ ocx-mirror package check --dry-run protoc/mirror.yml
    WARN [protoc] Skipping version 35.1: version '35.1' needs full X.Y.Z format
    …  (once per release, 80 of them)
    INFO [protoc] Nothing to mirror
    $ echo $?
    0

A `github_release` spec would therefore have gone green in CI forever while
publishing nothing. `tag_pattern` is a regex and cannot synthesize the missing
component, so the normalization has to happen here.

`v<MAJOR>.<MINOR>` becomes `<MAJOR>.<MINOR>.0` — the standard semver completion
of a partial version. The invented `.0` is visible only in the leaf tag; the
cascade aliases it publishes are `35.1`, `35` and `latest`, so
`ocx add protocolbuffers/protoc@35.1` resolves under upstream's own spelling.
Fleet precedent for normalizing an upstream version into the pipeline's grammar
is `mirror-amazon/corretto`, which maps Corretto's five-component
`21.0.12.8.1` to `21.0.12_8001` and likewise synthesizes a `0` minor for JDK 8.

Everything else about the mirror is unchanged: the URLs below are GitHub's own
release-asset URLs, so the bytes published are still upstream's release
binaries.
"""

import re
import sys

from ocx_mirror_sdk import IndexBuilder, github

REPO = "protocolbuffers/protobuf"

# Two-component release tags only. Release candidates (`v36.0-rc2`,
# `v34.0-rc1.1`) and the legacy per-language runtime tags (`v6.31.1`) fail this
# pattern and are dropped here as well as by `include_prereleases=False`.
TAG_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)$")

# ocx platform key -> upstream asset token. These tokens do not derive from any
# pattern, which is why they are an explicit map: `aarch_64` carries an
# underscore, macOS is `osx` not `darwin`, and Windows is `win64`.
#
# ocx expresses only amd64 and arm64, so upstream's `linux-x86_32`,
# `linux-ppcle_64`, `linux-s390_64` and `win32` assets have no platform key and
# are deliberately absent. `osx-universal_binary.zip` is skipped in favour of
# the split per-arch zips, matching every other OS's pattern.
PLATFORM_TOKENS = {
    "linux/amd64": "linux-x86_64",
    "linux/arm64": "linux-aarch_64",
    "darwin/amd64": "osx-x86_64",
    "darwin/arm64": "osx-aarch_64",
    "windows/amd64": "win64",
}


def ocx_version(tag: str) -> str | None:
    """Map an upstream release tag to the semver the mirror publishes."""
    match = TAG_RE.match(tag)
    if match is None:
        return None
    return f"{match['major']}.{match['minor']}.0"


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def self_check() -> int:
    """Assert the tag normalization. `uv run scripts/generate.py --self-check`.

    This is the one piece of non-trivial logic in the file: get it wrong and
    the mirror either publishes nothing (unparseable) or publishes under a
    version nobody can resolve.
    """
    assert ocx_version("v35.1") == "35.1.0"
    assert ocx_version("v33.0") == "33.0.0"
    assert ocx_version("v25.9") == "25.9.0"  # LTS train; excluded by versions.min
    assert ocx_version("v36.0-rc2") is None
    assert ocx_version("v34.0-rc1.1") is None
    assert ocx_version("v6.31.1") is None  # legacy per-language runtime tag
    assert ocx_version("35.1") is None  # no leading v
    log("self-check ok")
    return 0


def main() -> int:
    if "--self-check" in sys.argv:
        return self_check()

    index = IndexBuilder()
    skipped_incomplete = 0

    for release in github.list_releases(REPO, include_prereleases=False, include_drafts=False):
        version = ocx_version(release.tag_name)
        if version is None:
            continue

        by_name = {asset.name: asset.browser_download_url for asset in release.assets}
        # Build the expected filename from UPSTREAM's own version string, not
        # from the normalized one — the asset is `protoc-35.1-…`, never
        # `protoc-35.1.0-…`.
        upstream_version = release.tag_name.removeprefix("v")
        assets = {}
        for token in PLATFORM_TOKENS.values():
            filename = f"protoc-{upstream_version}-{token}.zip"
            url = by_name.get(filename)
            if url is not None:
                assets[filename] = url

        # Mirror a version only when it ships EVERY platform this package can
        # declare. A url_index version missing a declared platform leaves that
        # platform's test/push leg with no bundle and reds the run at exit 74;
        # dropping the version is the honest outcome. All 12 releases in range
        # (33.0 … 35.1) ship the full set, so this path is defensive.
        if len(assets) != len(PLATFORM_TOKENS):
            log(f"skip {release.tag_name} (only {len(assets)}/{len(PLATFORM_TOKENS)} platform assets)")
            skipped_incomplete += 1
            continue

        index.add_version(version, assets=assets, prerelease=False)

    log(f"emitting {len(index)} versions ({skipped_incomplete} skipped for incomplete asset sets)")
    index.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
