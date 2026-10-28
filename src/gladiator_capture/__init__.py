"""GLADIATOR P02 capture: raw preservation, normalization, integrity checks and replay.

Implements the P02 event contract (docs/evidence/P02/event-contract.md) for files
that are already held. No network access, no live capture (DEC-058).
"""

SCHEMA_VERSION = "p02-1"
