# NOTICE

This repository packages and redistributes upstream
[Protocol Buffers](https://github.com/protocolbuffers/protobuf).

The Apache-2.0 license covers the OCX pipeline files authored here. It does
**not** cover upstream-derived assets — the `protoc` binaries and the
well-known-type `.proto` definitions published to
`ghcr.io/ocx-contrib/protocolbuffers/protoc` (**BSD-3-Clause**, © 2008 Google
Inc. and contributors).

BSD-3-Clause is permissive: binary redistribution is granted provided the
copyright notice, the list of conditions and the disclaimer are retained, and
neither Google's name nor its contributors' names are used to endorse this
mirror. The upstream license text is at
<https://github.com/protocolbuffers/protobuf/blob/main/LICENSE>.

> **On the SPDX id.** GitHub's license API reports this repository as
> `NOASSERTION`:
>
> ```
> $ gh api repos/protocolbuffers/protobuf/license --jq '{spdx: .license.spdx_id, key: .license.key}'
> {"key":"other","spdx":"NOASSERTION"}
> ```
>
> That is a **classifier false negative**, not an unresolved licensing
> question. protobuf is a monorepo carrying additional per-directory notices,
> and GitHub's detector declines to classify the root rather than reporting the
> root file. The root `LICENSE` was fetched and read directly and is verbatim
> three-clause BSD — "Copyright 2008 Google Inc. All rights reserved.", the
> source and binary redistribution clauses, and the "Neither the name of Google
> Inc. nor the names of its contributors may be used to endorse or promote
> products derived from this software" non-endorsement clause. **BSD-3-Clause**
> is therefore the SPDX id recorded here and in
> `org.opencontainers.image.licenses`, on the evidence of the file rather than
> the API.

**Not affiliated with or endorsed by Google LLC.** This mirror republishes
upstream's own release binaries byte-for-byte; it does not build, patch or
modify Protocol Buffers.
