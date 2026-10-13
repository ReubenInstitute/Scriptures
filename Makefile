PYPI_TOKEN ?= ~/pypi.txt

.PHONY: pip install-pip upload clean

pip:
	rm -rf build
	mkdir -p build/base/scriptures build/web build/dev
	cp scriptures.py bible.py mishnah.py talmudbavli.py talmudyerushalmi.py zohar.py zoharchadash.py zohartikkunim.py build/base/scriptures/
	cp GPL-3 build/base/
	cp -r csv build/base/scriptures/csv
	cp -r json build/base/scriptures/json
	cp __init__.py build/base/scriptures/__init__.py
	cp pip/pyproject-base.toml build/base/pyproject.toml
	( cd build/base && python3 -m build --outdir .. )
	cp scriptures-web.py GPL-3 build/web/
	cp pip/pyproject-web.toml build/web/pyproject.toml
	( cd build/web && python3 -m build --outdir .. )
	cp Source.py GPL-3 build/dev/
	cp pip/pyproject-dev.toml build/dev/pyproject.toml
	( cd build/dev && python3 -m build --outdir .. )

install-pip:
	python3 -m pip install build/*.whl

upload:
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$(cat $(PYPI_TOKEN)) twine upload build/*.whl build/*.tar.gz

clean:
	rm -rf build
