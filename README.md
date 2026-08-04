# mirror-protocolbuffers

OCX mirrors for [Protocol Buffers](https://protobuf.dev) tooling. One
repository, one spec directory per package.

| Package | Spec | Publishes to | Announced as |
|---|---|---|---|
| protoc | [`protoc/mirror.yml`](protoc/mirror.yml) | `ghcr.io/ocx-contrib/protocolbuffers/protoc` | [`ocx.sh/protocolbuffers/protoc`](https://index.ocx.sh/protocolbuffers/protoc) |

Each upstream release is discovered, re-bundled, smoke-tested per
`(version, platform)` and only then pushed with cascade tags, after which the
result is announced into the OCX index.

## Layout

There is no root `mirror-base.yml`: with one package, every key is
package-owned, so the whole spec lives in `protoc/mirror.yml` — the shape
`mirror-astral-sh` ships. A second package would add its own sibling directory;
factoring a base out at that point is a content move that renames no generated
workflow file.

## Why there is a generator

`protoc/mirror.yml` uses `source.type: url_index`, not `github_release`.
protobuf tags its compiler releases with a **two-component** version (`v33.0`,
`v35.1`) and ocx-mirror's version parser requires a full `X.Y.Z` — and it fails
*silently*, warning past every release and exiting 0 with `Nothing to mirror`.
A `github_release` spec here would have been green in CI forever while
publishing nothing.

`protoc/scripts/generate.py` normalizes `vX.Y` to `X.Y.0` — the standard semver
completion of a partial version. The synthesized `.0` appears only in the leaf
tag; the cascade aliases are `35.1`, `35` and `latest`, so
`ocx add protocolbuffers/protoc@35.1` resolves under upstream's own spelling.
The URLs it emits are GitHub's own release-asset URLs, so the published bytes
are still upstream's release binaries.

The script has a self-check covering the normalization:

```bash
cd protoc && uv run scripts/generate.py --self-check
```

## What this package ships

The `protoc` archive is `bin/protoc` **plus** an `include/` tree of well-known
type definitions (`google/protobuf/timestamp.proto`, `any.proto`,
`descriptor.proto`, …). `protoc` resolves those imports against `../include`
relative to its own binary, so both trees are installed — a bundle carrying
only the binary is a compiler that cannot compile any schema importing a
well-known type. `protoc/tests/smoke.star` compiles a `.proto` that imports
`google/protobuf/timestamp.proto` on every `(version, platform)` leg, so that
property is checked rather than assumed.

## Editing

| File | Edit | Regenerate after |
|------|------|------------------|
| `protoc/mirror.yml` | hand | `ocx-mirror package pipeline generate ci --spec protoc/mirror.yml` |
| `protoc/scripts/generate.py` | hand | — (re-run `--self-check`) |
| `protoc/tests/smoke.star` | hand | — |
| `protoc/metadata.json`, `protoc/CATALOG.md`, `protoc/logo.*` | hand | — |
| `.github/workflows/*.yml` | **generated — never hand-edit** | re-run when a spec changes |

`--spec` **appends** rather than replaces, so the command above must name every
spec that exists at the time it runs. `--repo-root` is inferred from the
enclosing git repository and is not needed here.

CI fails on drift via `ocx-mirror package pipeline generate ci --check`. If a
generated workflow is wrong, the spec or the renderer template is wrong — fix
it there and regenerate.

Run `direnv allow` once to put the pinned toolchain on `PATH`; keep the `:0.5`
tags in `ocx.toml` floating and let `ocx update` move `ocx.lock`.

## Required secrets

| Secret | Use |
|--------|-----|
| `OCX_ANNOUNCE_TOKEN` | opens the index PR from the `ocx-contrib/index` fork |
| `OCX_MIRROR_DISCORD_HOOK` | notify-stage Discord webhook URL |

Both are inherited from the `ocx-contrib` organisation with visibility ALL.
GHCR pushes use the run's own `GITHUB_TOKEN` — no registry secret needed.

## License

Apache-2.0 — see [`LICENSE`](LICENSE). Upstream assets are out of scope; see
[`NOTICE.md`](NOTICE.md).
