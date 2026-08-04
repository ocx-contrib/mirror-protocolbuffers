---
title: protoc
description: The Protocol Buffers compiler — turns .proto schema files into generated code for C++, Java, Python, C#, Kotlin, Objective-C, PHP, Ruby and Rust
keywords: protoc,protobuf,protocol-buffers,serialization,codegen,grpc,idl,schema
---

# protoc

`protoc` is the Protocol Buffers compiler. It reads `.proto` schema files —
Google's language-neutral, platform-neutral interface definition language — and
emits either generated source code for a target language or a binary
`FileDescriptorSet` describing the schema itself. It is the tool gRPC service
definitions, Buf pipelines and most schema-driven build steps invoke.

These are Google's own release binaries from the `protocolbuffers/protobuf`
releases, republished unmodified. Each is statically linked and needs nothing
from the host beyond a kernel — no libc, no runtime, no system libraries.

## What's included

- **protoc** — compile `.proto` files to generated code or a descriptor set

The bundle also ships the **well-known type definitions** —
`include/google/protobuf/*.proto`: `any.proto`, `timestamp.proto`,
`duration.proto`, `struct.proto`, `field_mask.proto`, `descriptor.proto`,
`compiler/plugin.proto` and the rest. `protoc` resolves imports of those paths
against `../include` relative to its own binary, so they are not optional
scaffolding: without them any schema that writes
`import "google/protobuf/timestamp.proto";` fails to compile.

Language plugins that are not built in (`protoc-gen-go`, `protoc-gen-grpc-*`,
…) are separate upstream projects and are not part of this package; `protoc`
finds them on `PATH` as `protoc-gen-<name>`.

## Links

BSD-3-Clause licensed.

- [Protocol Buffers documentation](https://protobuf.dev/)
- [`.proto` language guide](https://protobuf.dev/programming-guides/proto3/)
- [protobuf on GitHub](https://github.com/protocolbuffers/protobuf)
