# Makefile
venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -r requirements.txt
	touch venv/bin/activate

.PHONY:clean yapf/format yapf/check

clean:
	$(RM) -rf venv
	find . -name "*.pyc" -exec $(RM) -rf {} \;

yapf/format: venv
	venv/bin/yapf -i -r *.py ||:

yapf/check: venv
	venv/bin/yapf -d -r *.py
