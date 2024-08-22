from .element import PGXElement
from typing import Any, Callable
import pygame as pg
import secrets

class ExportableNamespace: pass

class PGXApp:
	def __init__(self, size: tuple[int, int], framerate: int):
		self.id_to_elem: dict[str, PGXElement] = {}
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

	def add_element(self, elem: PGXElement):
		if elem.id == None:
			elem.id = secrets.token_urlsafe(10)
			if elem.id in self.id_to_elem: return self.add_element(elem)
			
		self.id_to_elem[elem.id] = elem

	def get_element_by_id(self, elem_id: str):
		return self.id_to_elem[elem_id]
	
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