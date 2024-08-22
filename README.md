# Pygame-PGX

`pygame-pgx` is a Python package designed to simplify the development of PyGame-based UIs in Python. `pygame-pgx` applications are written in an XML-like format, and functionality can be added to them by linking Python scripts to the app. `pygame-pgx` provides APIs for interacting with the different components of the app inside of linked scripts.

To run the example, install the `pygame-pgx` package locally and use the `pgx-start` command followed by the path of the example's main XML file.

E.g
```sh
pip install "./pygame-pgx/"

pgx-start "tests/testproj/main.pgx"
```