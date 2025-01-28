# PYTHON ENVIRONMENT
venv_create:
	python3 -m venv ./venv; \
	. ./venv/bin/activate && \
	pip3 install -r requirements.txt

venv_create_dev:
	python3 -m venv ./venv; \
	. ./venv/bin/activate && \
	pip3 install -r requirements-dev.txt

# PYTHON
update_packages:
	python3 -m venv ./venv; \
	. ./venv/bin/activate && \
	pip3 install -r requirements-dev.txt && \
	echo "[*] Checking: requirements-dev.txt" && \
	pur -r requirements-dev.txt && \
	echo "[*] Checking: requirements.txt" && \
	pur -r requirements.txt && \
	echo "[*] Checking: examples/python/requirements.txt" && \
	pur -r examples/python/requirements.txt

# MITMPROXY
update_mitmproxy:
	echo "[*] Updating mitmproxy..."; \
	LATEST_VERSION="11.1.0"; \
	TARGET_ARCHIVE="https://downloads.mitmproxy.org/$${LATEST_VERSION}/mitmproxy-$${LATEST_VERSION}-linux-x86_64.tar.gz"; \
	wget -O mitmproxy.tar.gz $${TARGET_ARCHIVE}; \
	tar -xvf mitmproxy.tar.gz

# LINTING
lint: \
	venv_create_dev \
	lint_python

lint_python:
	. ./venv/bin/activate && \
	echo "[*] Linting Python..." && \
	python3 -m flake8 .
