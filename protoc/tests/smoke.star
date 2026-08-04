# Smoke test for protocolbuffers/protoc.
#
# The thing worth testing here is NOT that a binary exists — it is that the
# compiler can compile. protoc resolves well-known-type imports
# (`google/protobuf/*.proto`) against `../include` RELATIVE TO ITS OWN BINARY,
# so a bundle carrying only `bin/protoc` produces a compiler that cannot build
# any .proto touching a Timestamp, Any, Duration or Struct — which is most real
# ones. A `--version`-only smoke would go green on exactly that bundle.
#
# Measured before this was written (protoc 35.1, bin/protoc copied away from
# its sibling include/):
#
#   $ ./noinc/bin/protoc --cpp_out=out -I. t.proto
#   google/protobuf/timestamp.proto: File not found.
#   t.proto:3:1: Import "google/protobuf/timestamp.proto" was not found …
#   exit 1
#
# So the red below is reachable, which is what makes the green evidence.

# `if`-EXPRESSION, not an `if` statement: a control-flow statement at module
# scope is a parse error in the Bazel .bzl dialect and would red every version
# on every platform at once.
PROTOC = "protoc.exe" if ocx.target_platform.os == ocx.os.Windows else "protoc"

# ── Tier 1 + 2: liveness and version SHAPE ──────────────────────────────────
# `protoc --version` prints `libprotoc <major>.<minor>` — TWO components,
# because protobuf tags are `vX.Y`. Asserting a three-component shape would red
# every release. Shape only: never the vendor word, never the exact version.
r_version = ocx.run(PROTOC, "--version")
expect.ok(r_version)
expect.matches(r_version.stdout, r"\d+\.\d+")

# ── Tier 3: a real compilation that depends on the bundled include/ tree ────
# Hermetic — every file protoc reads is written here first. The one file it
# reads that is NOT written here is `google/protobuf/timestamp.proto`, and that
# is precisely the point.
ocx.write_file("t.proto", """syntax = "proto3";
package ocxsmoke;

import "google/protobuf/timestamp.proto";

message Ping {
  google.protobuf.Timestamp at = 1;
  string note = 2;
}
""")
ocx.mkdir("gen")

r_gen = ocx.run(PROTOC, "--cpp_out=gen", "-I.", "t.proto")
expect.ok(r_gen)

# The generated header must #include the well-known type's own header. That
# line exists ONLY because the import resolved out of the bundled include/
# tree, and its text is derived from our own `import` statement rather than
# from any protoc prose — verified byte-identical at both ends of the range
# (v33.0 and v35.1 each emit it exactly once).
hdr = ocx.read_file("gen/t.pb.h")
expect.eq(hdr.count("#include \"google/protobuf/timestamp.pb.h\""), 1)

# ── Negative control 1: protoc must reject a broken .proto ──────────────────
# Without this, a green `--cpp_out` proves only that protoc ran.
ocx.write_file("bad.proto", """syntax = "proto3";
message Bad { broken
""")
r_bad = ocx.run(PROTOC, "--cpp_out=gen", "-I.", "bad.proto")
expect.ne(r_bad.exit_code, 0)

# ── Negative control 2: an import absent from include/ must fail ────────────
# This is what makes the Tier 3 assertion a test of import RESOLUTION and not
# merely of protoc tolerating whatever it is handed.
ocx.write_file("bogus.proto", """syntax = "proto3";
import "google/protobuf/does_not_exist.proto";
message X { int32 a = 1; }
""")
r_bogus = ocx.run(PROTOC, "--cpp_out=gen", "-I.", "bogus.proto")
expect.ne(r_bogus.exit_code, 0)
