def is_number(s: str) -> bool:
	try:
		_ = int(s)
		return True
	except ValueError:
		return False