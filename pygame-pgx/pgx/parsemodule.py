import os
import textwrap
import pygame as pg
import lxml.etree as etree
from domapi import Element
from .exceptions import ChildrenNotPermittedException, InvalidAppException, InvalidAttributeException
from .api import PGXApp, PGXElement, ScriptContext
from .parseval import parse_pos, parse_size

def get_attrs_dict(elem: Element):
	return {
		name: attr.value
		for name, attr in elem.attributes._map.items()
	}

def recurse_pgx(app: PGXApp, deferred_scripts: list[tuple[str, ScriptContext]], parent: Element) -> tuple[list[PGXElement], tuple[int, int]]:
	elements: list[PGXElement] = []

	fallback_x = 0
	fallback_y = 0

	for elem in parent.children:
		if elem._root.tag == "surface":
			children, fallback_size = recurse_pgx(app, deferred_scripts, elem)
			
			size = parse_size(elem.getAttribute("size"), fallback_size)

			surf = pg.Surface(size)
			rect = surf.get_rect(**{ attr.removeprefix("pos-"): parse_pos(elem.getAttribute(attr)) for attr in elem.attributes._map if attr.startswith("pos-") })
			surf.fill(elem.getAttribute("color") or "black")

			pgelem = PGXElement(surf, rect, elem.getAttribute("id"), "surface", get_attrs_dict(elem), children)

			elements.append(pgelem)

			fallback_x+=rect.left+size[0]
			fallback_y+=rect.top+size[1]
		elif elem._root.tag == "img":
			children, _ = recurse_pgx(app, deferred_scripts, elem)

			if children: raise ChildrenNotPermittedException(
				"<img> elements may not have children"
			)

			src = elem.getAttribute("src")
			surf = pg.image.load(src)


			size = parse_size(elem.getAttribute("size"), surf.get_size())

			scaled = pg.transform.scale(surf, size)
			rect = scaled.get_rect(**{ attr.removeprefix("pos-"): parse_pos(elem.getAttribute(attr)) for attr in elem.attributes._map if attr.startswith("pos-") })

			pgelem = PGXElement(scaled, rect, elem.getAttribute("id"), "img", get_attrs_dict(elem))

			elements.append(pgelem)

			fallback_x+=rect.left+size[0]
			fallback_y+=rect.top+size[1]
		elif elem._root.tag == "embed":
			children, _ = recurse_pgx(app, deferred_scripts, elem)

			if children: raise ChildrenNotPermittedException(
				"<embed> elements may not have children"
			)

			src = elem.getAttribute("src")

			pgelem =  parse_module(app, deferred_scripts, src, elem.getAttribute("id"), { attr.removeprefix("pos-"): parse_pos(elem.getAttribute(attr)) for attr in elem.attributes._map if attr.startswith("pos-") })

			elements.append(pgelem)

			fallback_x+=pgelem.rect.left+pgelem.size[0]
			fallback_y+=pgelem.rect.top+pgelem.size[1]	
		elif elem._root.tag == "script":
			children, _ = recurse_pgx(app, deferred_scripts, elem)
			
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

def parse_module(app: PGXApp, deferred_scripts: list[tuple[str, ScriptContext]], filename: str,  _id: str, posargs: dict[str, tuple[int, int]]) -> PGXElement:
	if not posargs: raise InvalidAppException("Cannot embed module without a position!")

	orig_dir = os.getcwd()
	
	os.chdir(os.path.dirname(filename))
	
	document: etree._ElementTree = etree.parse(os.path.basename(filename))

	doctype: str = document.docinfo.internalDTD.name

	if doctype != "pygame-pgx-module":
		raise InvalidAppException(
			"Invalid doctype (must be pygame-pgx-module)!"
		)
		
	root: etree._Element = document.getroot()

	if root.tag != "module":
		raise InvalidAppException(
			"Root element is not <module>"
		)

	doc = Element(root)

	if doc.getAttribute("size") is None:
		raise InvalidAppException(
			"No size specified on <module>"
		)
	
	surf = pg.Surface(parse_size(doc.getAttribute("size")))
	rect = surf.get_rect(**posargs)
	
	elem = PGXElement(
		surf, rect, 
		_id, "module", get_attrs_dict(doc)
	)

	elem.children, _ = recurse_pgx(app, deferred_scripts, doc)
	
	os.chdir(orig_dir)

	return elem