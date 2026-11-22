# Kaspa legacy RISC Zero recursion circuit

> **Unsound circuit.** This crate uses the recursion circuit from the yanked `risc0-circuit-recursion` 4.0.4 release. RISC Zero fixed the circuit soundness flaw in 4.1.0. This port preserves the affected circuit solely for Kaspa STARK consensus compatibility. [RISC Zero security advisory GHSA-g6qg-9j8p-7j87](https://github.com/risc0/risc0/security/advisories/GHSA-g6qg-9j8p-7j87)

This crate packages the recursion circuit and control data used by the Rusty Kaspa `v2.1.0` STARK opcode. The seven files under `src/` are copied byte for byte from the published `risc0-circuit-recursion` 4.0.4 archive. The archive identifies RISC Zero commit `ba889fc` as its source. Rusty Kaspa's lockfile records the archive's SHA-256 as `2347e909c6b2a65584b5898f3802eec5b8c1b4b45329edfdd8587b6a04dd3357`. [Published archive](https://static.crates.io/crates/risc0-circuit-recursion/risc0-circuit-recursion-4.0.4.crate) · [Upstream source](https://github.com/risc0/risc0/tree/ba889fc049830b777de63fddbeea5f9776618d7d/risc0/circuit/recursion) · [Rusty Kaspa lockfile](https://github.com/kaspanet/rusty-kaspa/blob/v2.1.0/Cargo.lock)

The verifier-only library is named `risc0_circuit_recursion`. It uses the same RISC Zero dependency versions as Rusty Kaspa `v2.1.0` (`risc0-zkp` `3.0.4`, `risc0-core` `3.0.1`, and `risc0-zkvm-platform` `2.2.2`).

## Verify the package

To reproduce and verify the package, run these commands from a clean checkout of the source repository. You’ll need Cargo, `curl`, and Python 3.11 or later. [Source repository](https://github.com/kaspanet/kaspa-r0-recursion-legacy)

```sh
cargo package --locked
curl -fL https://static.crates.io/crates/risc0-circuit-recursion/risc0-circuit-recursion-4.0.4.crate \
  -o target/risc0-circuit-recursion-4.0.4.crate
python3 scripts/check-upstream.py target/risc0-circuit-recursion-4.0.4.crate \
  target/package/kaspa-r0-recursion-legacy-0.1.0.crate
```

The checker verifies the upstream archive's SHA-256, compares all seven packaged source files byte for byte, and checks the packaged manifest's library target, disabled build script, and exact dependency pins. To verify a published release, pass its `.crate` file from crates.io as the second argument to the checker.
