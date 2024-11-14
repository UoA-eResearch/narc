# narc > examples > python

Ensure you meet the project requirements:

- `mitmproxy` binary on your path, or in project root folder
- Python >= 3.10

And useful requirements:

- Virtual environment (e.g., `python3-venv`)

In a terminal start the proxy:

```
./mitmdump -s narc.py
```

Open another terminal, get the project ready to run:

```
cd examples/python
python -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Go back to original terminal and run the app:

```
python3 app.py <INSTANCE_ID>
```

Use `Ctrl + C` to stop `mitmproxy` and view the resultant access rules file:

```
cat access_rules.json 
[
    {
        "service": "identity",
        "method": "POST",
        "path": "/v3/auth/tokens"
    },
    {
        "service": "compute",
        "method": "GET",
        "path": "/v2.1/servers/**"
    }
]
```
