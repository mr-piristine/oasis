# integrity/hasher.py

import hashlib
import xxhash


class EvidenceHasher:

    @staticmethod
    def generate_row_hash(ts, o, h, l, c, v) -> str:
        raw = f"{ts}|{o}|{h}|{l}|{c}|{v}"
        return xxhash.xxh128(raw).hexdigest()

    @staticmethod
    def generate_content_hash(payload: str) -> str:
        return xxhash.xxh128(payload).hexdigest()

    @staticmethod
    def generate_dv2_hash_key(*keys: str) -> str:
        base = "|".join(str(k).strip().lower() for k in keys)
        return hashlib.md5(base.encode()).hexdigest()