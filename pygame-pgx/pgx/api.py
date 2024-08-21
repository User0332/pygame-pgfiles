import pygame as pg
import secrets

class PGXApp:
	def __init__(self, size: tuple[int, int]):
		self.id_to_elem: dict[str, pg.Surface] = {}
		self.size = size

	def _add_element(self, elem_id: str, surf: pg.Surface):
		if elem_id == None:
			elem_id = secrets.token_urlsafe(10)
			if elem_id in self.id_to_elem: return self._add_element(None, surf)
			
		self.id_to_elem[elem_id] = surf

	def get_surface_by_id(self, elem_id: str) -> pg.Surface:
		return self.id_to_elem[elem_id]
	
	def update(self): pass