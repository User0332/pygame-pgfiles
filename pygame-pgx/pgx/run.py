from pgx.api.scriptctx import ScriptContext
from .exceptions import ChildrenNotPermittedException, InvalidAppException, InvalidAttributeException
from .parseval import parse_size, parse_pos
from .api import PGXApp, PGXElement
from domapi import Element
import os
import textwrap
import pygame as pg
import lxml.etree as etree

def run(filename: str):
	os.chdir(os.path.dirname(filename))
	
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

	try: framerate = int(doc.getAttribute("framerate"))
	except TypeError: framerate = 60
	except ValueError: raise InvalidAttributeException("Invalid value for framerate (must be int)")

	app = PGXApp(parse_size(doc), framerate)
	deferred_scripts: list[tuple[str, ScriptContext]] = []

	screen = pg.display.set_mode(app.size)

	def recurse_pgx(parent: Element) -> tuple[list[PGXElement], tuple[int, int]]:
		elements: list[PGXElement] = []

		fallback_x = 0
		fallback_y = 0

		for elem in parent.children:
			if elem._root.tag == "surface":
				children, fallback_size = recurse_pgx(elem)
				
				size = parse_size(elem, fallback_size)

				fallback_x+=size[0]
				fallback_y+=size[1]

				surf = pg.Surface(size)
				rect = surf.get_rect(**{ attr.removeprefix("pos-"): parse_pos(elem.getAttribute(attr)) for attr in elem.attributes._map if attr.startswith("pos-") })
				surf.fill(elem.getAttribute("color") or "black")

				pgelem = PGXElement(surf, rect, elem.getAttribute("id"), children)

				app.add_element(pgelem)
				elements.append(pgelem)
			if elem._root.tag == "img":
				children, _ = recurse_pgx(elem)

				if children: raise ChildrenNotPermittedException(
					"<img> elements may not have children"
				)

				src = elem.getAttribute("src")
				surf = pg.image.load(src)

				size = parse_size(elem, surf.get_size())

				fallback_x+=size[0] # need to fix, this doesnt account for pos at all
				fallback_y+=size[1]

				scaled = pg.transform.scale(surf, size)

				rect = scaled.get_rect(**{ attr.removeprefix("pos-"): parse_pos(elem.getAttribute(attr)) for attr in elem.attributes._map if attr.startswith("pos-") })

				pgelem = PGXElement(scaled, rect, elem.getAttribute("id"))

				app.add_element(pgelem)
				elements.append(pgelem)
			if elem._root.tag == "script":
				children, _ = recurse_pgx(elem)
				
				if children: raise ChildrenNotPermittedException(
					"<script> elements may not have children"
				)

				src = elem.getAttribute("src")
				script_type = elem.getAttribute("type") or "text/python"

				if script_type != "text/python":
					raise InvalidAppException("script/python is currently the only supported script type!")

				if not src:
					script_text = textwrap.dedent(''.join(elem._root.itertext()))
					ctx = ScriptContext(script_type, "<inline>", script_text, app.global_namespace)
				else:
					script_text = open(src, 'r').read()
					ctx = ScriptContext(script_type, os.path.relpath(src).replace('\\', '/'), script_text, app.global_namespace)


				schedule = elem.getAttribute("schedule") or "instant"

				if schedule == "onload":
					ctx.execution_scheduling = "onload"

					deferred_scripts.append(
						(script_text, ctx)
					)
				elif schedule == "instant":
					exec(
						script_text,
						{ **app.global_namespace, "current_script": ctx },
					)
				else: raise InvalidAttributeException("Script scheduling must either be 'instant' or 'onload'")

		return elements, (fallback_x, fallback_y)

	app.root_elements, _ = recurse_pgx(doc)

	for (script_text, context) in deferred_scripts:
		exec(script_text, { **app.global_namespace, "current_script": context })	

	print(vars(app.global_namespace["exports"]))
	app.app_update = getattr(app.global_namespace["exports"], "pgx_update", lambda: None)

	while 1:
		for event in pg.event.get(): # TODO: have a separate event thread that calls event handlers
			if event.type == pg.QUIT:
				pg.quit()
				exit(0)

		app.render_to(screen)

		app.update()
				
		pg.display.update()

if __name__ == "__main__":
	run()