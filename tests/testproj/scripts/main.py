from pgx.api.annotations import *
import pygame as pg
import random

def gen_rect_fill():
	return tuple(
		[random.randint(0, 255) for i in range(3)]
	)

def pgx_update():
	# print(app.get_element_by_id("wrapper").surf.get_size())


	app.get_element_by_id("rect").surf.fill(gen_rect_fill())

print(current_script)

exportfn(pgx_update)