from dataclasses import dataclass, field
import pygame as pg

@dataclass
class PGXElement:
	surf: pg.Surface
	rect: pg.Rect
	id: str | None
	type: str
	children: list['PGXElement'] = field(default_factory=list)