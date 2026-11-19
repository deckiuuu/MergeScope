PYTHON ?= python3
NODE ?= node

.PHONY: test verify check package

test:
	$(PYTHON) cutofflab.py test
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
	$(NODE) --test tests/test_viewer.cjs

verify:
	$(PYTHON) cutofflab.py verify
	$(PYTHON) tools/repository_check.py check

check: test verify

package:
	$(PYTHON) tools/package_submission.py
