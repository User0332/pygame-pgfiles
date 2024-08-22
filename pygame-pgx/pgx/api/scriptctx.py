from dataclasses import dataclass, field
from typing import Literal

@dataclass
class ScriptContext:
	type: str
	location: str | Literal["<inline>"]
	text: str = field(repr=False)
	global_namespace: dict[str] = field(repr=False)
	execution_scheduling: Literal["instant"] | Literal["onload"] = "instant"