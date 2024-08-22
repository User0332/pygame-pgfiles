from domapi import Element
from .exceptions import InvalidAttributeException

def parse_size(element: Element, fallback: tuple[int, int] | None=None) -> tuple[int, int]:
	try: return tuple(int(num) for num in element.getAttribute("size").split('x'))
	except AttributeError:
		if fallback: return fallback

		raise InvalidAttributeException(f"Size '{element.getAttribute('size')}' is not parseable!")

def parse_pos(pos: str, fallback: tuple[int, int] | None=None) -> tuple[int, int]:
	try: return tuple(int(num) for num in pos.split(','))
	except AttributeError:
		if fallback: return fallback

		raise InvalidAttributeException(f"Position '{pos}' is not parseable!")