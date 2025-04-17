import os
import sys
from .run import run

def main():
	if len(sys.argv) < 2:
		print("No pgx file specified!", file=sys.stderr)
		exit(1)

	if not os.path.isfile(sys.argv[1]):
		print(f"'{sys.argv[1]}' is not a file!", file=sys.stderr)
		exit(1)

	run(sys.argv[1])

if __name__ == "__main__":
	main()