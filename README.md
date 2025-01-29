# narc

The Nectar Access Rules Creator, or `narc`, is a tool to help construct OpenStack Access Rules for Application Credentials.

## What?

- "Application Credentials" are used to allow software to talk to OpenStack, similar to users who have passwords
- "Access Rules" are a type of access control within AppCreds that grant access specific resources
- Trying to determine what access rules are needed is quite difficult, resulting in using the "Unrestricted" option
- This tools helps analyse OpenStack API calls and generates an access rules JSON file automatically

## How?

- Start proxy to intercept traffic
- Run usual OpenStack tooling (e.g., CLI, Python packages, Terraform)
- Listen to OpenStack API calls
- "Tidy" OpenStack API calls and create a JSON output
- Use output to create AppCers

## Inspiration

The [`iamlive`](https://github.com/iann0036/iamlive) is an amazing tool that helps AWS developers/admins run AWS CLI commands from their workstation and see the exact permissions used. They take the results, and use it to make "IAM" policies (permissions) in the AWS cloud. This results in very fine-grained and accurate policies.

## Quickstart

- Start `mitmdump` with `narc` script:
- `./mitmdump -s narc.py`
- In another terminal, configure environment variables for `mitmproxy`:
  - Set `https_proxy` to the default `https://127.0.0.1:8080`
  - Configure your tooling to use the `mitmproxy` certificate (if needed)
- Run any OpenStack CLI command, Terraform apply, or any tools that makes API calls
- When done, use `Ctrl + C` to stop `mitmdump`
- Review `access_rules.json` and `narc.py.log` for results

### OpenStack CLI example

```
./mitmdump -s narc.py
# Open new terminal
https_proxy=https://127.0.0.1:8080 \
openstack \
--os-cacert ~/.mitmproxy/mitmproxy-ca-cert.pem \
project list
```

### Terraform Example

```
./mitmdump -s narc.py
# Open new terminal
https_proxy=https://127.0.0.1:8080 \
SSL_CERT_FILE=~/.mitmproxy/mitmproxy-ca-cert.pem \
terraform apply
```

### Python Script Example

```
./mitmdump -s narc.py
# Add this to your Python project
import os
home_directory = os.path.expanduser("~")
mitmproxy_ca_cert = f"{home_directory}/.mitmproxy/mitmproxy-ca-cert.pem"
os.environ["REQUESTS_CA_BUNDLE"] = mitmproxy_ca_cert
os.environ["https_proxy"] = "https://127.0.0.1:8080"
```

### Results Example

```
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

## Getting Started

### Requirements

- mitmproxy
- Python >= 3.10

### Install `mitmproxy`

On Linux, [download binaries](https://mitmproxy.org/), extract binaries, and put in the project root folder, or another folder on your `PATH`:

```
VERSION="11.1.0"
URL="https://downloads.mitmproxy.org/$${VERSION}/mitmproxy-$${VERSION}-linux-x86_64.tar.gz"
wget -O mitmproxy.tar.gz ${URL}
tar -xvf mitmproxy.tar.gz
```

On macOS use `brew`:

```
brew install mitmproxy
```

### Start `mitmproxy`

Run the `mitmdump` binary, specifying the `narc.py` script:

```
./mitmdump -s narc.py
```

Perform OpenStack API calls, using either:

- The OpenStack CLI
- The OpenStack Python packages
- Other IaC tools, such as Terraform

To stop recording API calls, exit with `Ctrl + C`.

Results are stored, by default, in:

- `access_rules.json`

A log of all HTTP requests is stored in:

- `narc.py.log`

### Configure Application to use `mitmproxy`

You will need two things:

- Trust the `mitmproxy` CA to avoid TLS errors
- Tell your application to use the proxy

There are various ways to accomplish both of these.

### Use With OpenStack CLI

An example command:

```
https_proxy=https://127.0.0.1:8080 openstack --os-cacert ~/.mitmproxy/mitmproxy-ca-cert.pem project list
```

Or, you can set an alias in `~/.bashrc`:

```
alias openstack_proxy="https_proxy=https://127.0.0.1:8080 openstack --os-cacert ~/.mitmproxy/mitmproxy-ca-cert.pem"
```

Then run the command:

```
openstack_proxy project list
```

### Use With Python

Place the following in to your Python code:

```
home_directory = os.path.expanduser("~")
mitmproxy_ca_cert = f"{home_directory}/.mitmproxy/mitmproxy-ca-cert.pem"
os.environ["REQUESTS_CA_BUNDLE"] = mitmproxy_ca_cert
os.environ["https_proxy"] = "https://127.0.0.1:8080"
```

Instead of using the `REQUESTS_CA_BUNDLE`, you could use 

```
home_directory = os.path.expanduser("~")
os.environ["SSL_CERT_FILE"] = f"{home_directory}/.mitmproxy/mitmproxy-ca-cert.pem"
```

However, using this method... when you create a session with Keystone, specify the SSL certificate in the `verify` parameter:

```
import keystoneclient.client as keystone_client
from keystoneauth1 import session

...
sess = session.Session(auth=auth, verify=os.environ.get("SSL_CERT_FILE"))
keystone_c = keystone_client.Client(session=sess)
```

### Use With Terraform

An example command:

```
https_proxy=https://127.0.0.1:8080 SSL_CERT_FILE=~/.mitmproxy/mitmproxy-ca-cert.pem terraform apply
```
