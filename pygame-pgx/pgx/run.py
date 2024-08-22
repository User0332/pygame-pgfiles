from .api.scriptctx import ScriptContext
from .parsemodule import recurse_pgx
from .exceptions import InvalidAppException, InvalidAttributeException
from .parseval import parse_size
from .api import PGXApp
from domapi import Element
import os
import pygame as pg
import lxml.etree as etree

def run(filename: str):
	os.chdir(os.path.dirname(filename))
	
	document: etree._ElementTree = etree.parse(os.path.basename(filename))

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

	app = PGXApp(parse_size(doc.getAttribute("size")), framerate)
	deferred_scripts: list[tuple[str, ScriptContext]] = []

	screen = pg.display.set_mode(app.size)

	app.root_elements, _ = recurse_pgx(app, deferred_scripts, doc)

	for (script_text, context) in deferred_scripts:
		exec(script_text, { **app.global_namespace, "current_script": context })	

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