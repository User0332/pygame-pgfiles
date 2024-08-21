from sys import argv
from .exceptions import ChildrenNotPermittedException, InvalidAppException
from domapi import Element
from .parseval import parse_size, parse_pos
from .api import PGXApp
import pygame as pg
import lxml.etree as etree

def run(filename: str):
	document: etree._ElementTree = etree.parse(filename)

	doctype: str = document.docinfo.internalDTD.name

	if doctype != "pygame-pgx":
		raise InvalidAppException(
			"Invalid doctype (must be pygame-pgx)!"
		)
		
	root: etree._Element = document.getroot()

	if root.tag != "app":
		raise InvalidAppException(
			"Root element is not <app>"
		)

	doc = Element(root)

	if doc.getAttribute("size") is None:
		raise InvalidAppException(
			"No size specified on <app>"
		)

	pg.init()

	app = PGXApp(parse_size(doc))

	screen = pg.display.set_mode(app.size)

	def recurse_pgx(parent: Element) -> tuple[list[pg.Surface], list[pg.Rect], tuple[int, int]]:
		surfs: list[pg.Surface] = []
		rects: list[pg.Rect] = []

		fallback_x = 0
		fallback_y = 0

		for elem in parent.children:
			if elem._root.tag == "surface":
				*children, fallback_size = recurse_pgx(elem)
				
				size = parse_size(elem, fallback_size)

				fallback_x+=size[0]
				fallback_y+=size[1]

				surf = pg.Surface(size)
				app._add_element(elem.getAttribute("id"), surf)
				surf.fill(elem.getAttribute("color") or "black")

				for (child, rect) in zip(*children):
					surf.blit(child, rect)

				surfs.append(surf)
				rects.append(surf.get_rect(**{ attr.removeprefix("pos-"): parse_pos(elem.getAttribute(attr)) for attr in elem.attributes._map if attr.startswith("pos-") })) # TODO: get an actual pos
			if elem._root.tag == "img":
				*children, _ = recurse_pgx(elem)

				if children[0]: raise ChildrenNotPermittedException(
					"<img> elements may not have children"
				)

				src = elem.getAttribute("src")
				surf = pg.image.load(src)

				size = parse_size(elem, surf.get_size())

				fallback_x+=size[0] # need to fix, this doesnt account for pos at all
				fallback_y+=size[1]

				surf = pg.transform.scale(surf, size)

				surfs.append(surf)
				rects.append(surf.get_rect(**{ attr.removeprefix("pos-"): parse_pos(elem.getAttribute(attr)) for attr in elem.attributes._map if attr.startswith("pos-") })) # TODO: get an actual pos

		return surfs, rects, (fallback_x, fallback_y)

	*app_surfs, _ = recurse_pgx(doc)

	for (surf, rect) in zip(*app_surfs):
		screen.blit(surf, rect)

	while 1:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				exit(0)

		app.update()
				
		pg.display.update()

if __name__ == "__main__":
	run()