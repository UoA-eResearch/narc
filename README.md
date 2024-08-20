# narc

The Nectar Access Rules Creator, or `narc`, is a tool to help construct OpenStack Access Rules for Application Credentials.

## What

- "Application Credentials" are used to allow software to talk to OpenStack, similar to users who have passwords
- "Access Rules" are a type of access control within AppCreds that grant access specific resources
- Trying to determine what access rules are needed is quite difficult, resulting in using the "Unrestricted" option
- This tools helps analyse OpenStack API calls and generating an access rules JSON file automatically

### Similar Tool/Inspiration

The [`iamlive`](https://github.com/iann0036/iamlive) is an amazing tool that helps AWS developers/admins run AWS CLI commands from their workstation and see the exact permissions used. They take the results, and use it to make "IAM" policies (permissions) in the AWS cloud. This results in very fine-grained and accurate policies.

## Quickstart

- Start `mitmdump` with `narc` script: `./mitmpdump -s narc.py`
- In another terminal, configure environment variables for `mitmproxy`:
  - Set `https_proxy` to the default `https://127.0.0.1:8080`
- Run any OpenStack CLI command, Terraform apply, or any tools that makes API calls
- When done, use `Ctrl + C` to stop `mitmdump`
- Review `access_rules.json` and `narc.py.log` for results

OpenStack CLI example:

```
./mitmpdump -s narc.py
# Open new terminal
https_proxy=https://127.0.0.1:8080 \
openstack \
--os-cacert ~/.mitmproxy/mitmproxy-ca-cert.pem \
project list
```

Example result:

```
[
    {
        "service": "identity",
        "method": "POST",
        "path": "/v3/auth/tokens"
    },
    {
        "service": "identity",
        "method": "GET",
        "path": "/v3/projects"
    }
]
```

## Getting Started

### Requirements

- mitmproxy

### Install `mitmproxy`

On macOS use `brew`:

```
brew install mitmproxy
```

On Linux, [download binaries](https://mitmproxy.org/), extract binaries, and put in this folder or another folder on your `PATH`:

```
wget https://downloads.mitmproxy.org/10.4.2/mitmproxy-10.4.2-linux-x86_64.tar.gz
tar zvf mitmproxy-10.4.2-linux-x86_64.tar.gz
```

### Start `mitmproxy`

Run the `mitmdump` binary, specifying the `narc.py` script:

```
./mitmdump -s narc.py
```

Perform OpenStack API calls, using either:

- The OpenStack CLI
- The OpenStack Python packages
- Other IaC tools such as Terraform or Heat

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

### Use Proxy With OpenStack CLI

You will need two things:

- Trust the `mitmproxy` CA to avoid TLS errors: Use `--os-cacert` build into `openstack` command
- Tell your application to use the proxy: Use `https_proxy` env var to use the proxy

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

### Use With Terraform

You will need two things:

- Trust the `mitmproxy` CA to avoid TLS errors: Use `SSL_CERT_FILE` env var to trust the CA
- Tell your application to use the proxy: Use `https_proxy` env var to use the proxy


```
https_proxy=https://127.0.0.1:8080 SSL_CERT_FILE=~/.mitmproxy/mitmproxy-ca-cert.pem terraform apply
```

## Access Rules Examples

```
[
  {
    "service": "compute",
    "method": "POST",
    "path": "/v2.1/servers"
  }
]
```

```
- service: compute
  method: POST
  path: /v2.1/servers
```
