import pprint
from .element import PGXElement
from typing import Any, Callable
import pygame as pg
import secrets

class ExportableNamespace: pass

class PGXApp:
	def __init__(self, size: tuple[int, int], framerate: int):
		self.size = size
		self.exportable_namespace = ExportableNamespace()
		self.global_namespace = { "app": self, "exports": self.exportable_namespace, "exportfn": self._exportfn, "export": self._export }
		self.app_update: Callable[[], None] = lambda: None
		self.framerate = framerate
		self.clock = pg.time.Clock()
		self.root_elements: list[PGXElement] = []

	def _export(self, name: str, value: Any) -> None:
		setattr(self.global_namespace["exports"], name, value)

	def _exportfn(self, func: Callable) -> None:
		self._export(func.__name__, func)

	def get_element_by_id(self, elem_id: str, children: list[PGXElement] | None=None) -> PGXElement | None: # TODO: optimize
		if children is None: children = self.root_elements

		for elem in children:
			if elem.id == elem_id: return elem

			return self.get_element_by_id(elem_id, elem.children)
			
		return None
	
	def update(self):
		self.app_update()
		self.clock.tick(self.framerate)

	def render_to(self, screen: pg.Surface, elements: list[PGXElement] | None=None):
		if elements is None:
			screen.fill("black")
			elements = self.root_elements

		for element in elements:
			blit_to = element.surf.copy()

			self.render_to(blit_to, element.children)
			
			screen.blit(blit_to, element.rect)

	def __repr__(self) -> str:
		return pprint.pformat(self.root_elements)