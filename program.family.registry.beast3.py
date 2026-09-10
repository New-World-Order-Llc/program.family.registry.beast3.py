# program.family.registry.beast3.py
# Beast System 3.0 — Deterministic Master Registry Module

from dataclasses import dataclass, field
import time
import hashlib

@dataclass
class RegistryEntry:
    family_id: str
    modules: dict
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    hash: str = ""

    def finalize(self):
        serialized = f"{self.family_id}{self.modules}{self.created_at}{self.updated_at}".encode("utf-8")
        self.hash = hashlib.sha256(serialized).hexdigest()

class FamilyRegistry:
    def __init__(self, kernel):
        self.kernel = kernel
        self.registry = {}

    def register_family(self, family_id: str):
        entry = RegistryEntry(family_id, modules={})
        entry.finalize()
        self.registry[family_id] = entry

        return self.kernel.dispatch(
            module="family.registry",
            action="register_family",
            payload={"family_id": family_id, "hash": entry.hash}
        )

    def bind_module(self, family_id: str, module_name: str, reference_id: str):
        if family_id not in self.registry:
            raise ValueError("Family not registered")

        entry = self.registry[family_id]
        entry.modules[module_name] = {
            "ref": reference_id,
            "ts": time.time()
        }
        entry.updated_at = time.time()
        entry.finalize()

        return self.kernel.dispatch(
            module="family.registry",
            action="bind_module",
            payload={
                "family_id": family_id,
                "module": module_name,
                "reference_id": reference_id,
                "hash": entry.hash
            }
        )

    def lookup(self, family_id: str):
        return self.registry.get(family_id, None)

    def lookup_module(self, family_id: str, module_name: str):
        entry = self.registry.get(family_id)
        if not entry:
            return None
        return entry.modules.get(module_name, None)
