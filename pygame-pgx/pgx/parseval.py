from domapi import Element

def parse_size(element: Element, fallback: tuple[int, int]=(0, 0)) -> tuple[int, int]:
	try: return tuple(int(num) for num in element.getAttribute("size").split('x'))
	except AttributeError: return fallback

def parse_pos(pos: str, fallback: tuple[int, int]=(0, 0)) -> tuple[int, int]:
	try: return tuple(int(num) for num in pos.split(','))
	except AttributeError: return fallback