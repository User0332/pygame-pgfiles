from .exceptions import InvalidAttributeException

def parse_size(size: str, fallback: tuple[int, int] | None=None) -> tuple[int, int]:
	try: return tuple(int(num) for num in size.split('x'))
	except ValueError:
		raise InvalidAttributeException(f"Size '{size}' is not parseable!")
	except AttributeError:
		if fallback: return fallback

		raise InvalidAttributeException(f"No size given!")
	
def parse_pos(pos: str, fallback: tuple[int, int] | None=None) -> tuple[int, int]:
	try: return tuple(int(num) for num in pos.split(','))
	except ValueError:
		raise InvalidAttributeException(f"Position '{pos}' is not parseable!")
	except AttributeError:
		if fallback: return fallback

		raise InvalidAttributeException(f"No position given!")