from dataclasses import dataclass, field
import pygame as pg

@dataclass
class PGXElement:
	surf: pg.Surface
	rect: pg.Rect
	id: str | None
	tag: str
	attributes: dict[str, str]
	children: list['PGXElement'] = field(default_factory=list)

	@property
	def size(self) -> tuple[int, int]:
		return self.surf.get_size()