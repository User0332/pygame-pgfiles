import time
from pgx.api.annotations import *
import random

def gen_rect_fill():
	return tuple(
		[random.randint(0, 255) for i in range(3)]
	)

def pgx_update():
	# print(app.get_element_by_id("wrapper").surf.get_size())

	print(f"Seconds since last update: {time.time()-exports.last_update}")

	app.get_element_by_id("rect").surf.fill(gen_rect_fill())

	export("last_update", time.time())

print(current_script)

print(app)

print(exports.myvar)

exportfn(pgx_update)
export("last_update", time.time())