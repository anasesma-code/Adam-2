PY := .venv/bin/python

.PHONY: venv build color nobleed check previews test clean

venv:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

build:
	$(PY) scripts/build_book.py
	$(PY) scripts/preflight.py

color:
	$(PY) scripts/build_book.py --color -o output/libro_navidad_trazos_color.pdf
	$(PY) scripts/preflight.py output/libro_navidad_trazos_color.pdf

nobleed:
	$(PY) scripts/build_book.py --no-bleed -o output/libro_navidad_trazos_sin_sangrado.pdf
	$(PY) scripts/preflight.py --no-bleed output/libro_navidad_trazos_sin_sangrado.pdf

previews:
	$(PY) scripts/preflight.py --previews 1,2,4,8,14,21,29,36,40

test:
	$(PY) -m pytest -q

clean:
	rm -rf output
