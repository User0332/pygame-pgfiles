import pygame as pg
import pgx
import time
import random

def gen_rect_fill():
	return tuple(
		[random.randint(0, 255) for i in range(3)]
	)

def pgx_update(app: pgx.PGXApp):
	print(app.get_surface_by_id("wrapper").get_size())

	time.sleep(1) # make this later controlled by pgx (or maybe not at all -- use time.time() for deltas)
	app.get_surface_by_id("rect").fill(gen_rect_fill())

	app.update()