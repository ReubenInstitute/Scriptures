.PHONY: pip

pip:
	rm -rf dist
	for cfg in pip/pyproject-base.toml pip/pyproject-web.toml pip/pyproject-dev.toml; do \
		ln -sf "$$cfg" pyproject.toml; \
		rm -rf build *.egg-info; \
		python3 -m build || { rm -f pyproject.toml; exit 1; }; \
		rm -f pyproject.toml; \
	done
	rm -rf build *.egg-info
