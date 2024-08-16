import json
from typing import Optional
from uuid import UUID

from mitmproxy import http
from mitmproxy import ctx


endpoints = {
    "accelerator": "https://accelerator.rc.nectar.org.au/",
    "account": "https://accounts.rc.nectar.org.au/api/",
    "alarming": "https://alarming.rc.nectar.org.au/",
    "allocations": "https://allocations.rc.nectar.org.au/rest_api/",
    "application_catalog": "https://murano.rc.nectar.org.au:8082/",
    "cloudformation": "https://heat.rc.nectar.org.au:8000/",
    "compute": "https://nova.rc.nectar.org.au:8774/",
    "container_infra": "https://magnum.rc.nectar.org.au:9511/",
    "database": "https://dbaas.rc.nectar.org.au/",
    "dns": "https://designate.rc.nectar.org.au:9001/",
    "ec2": "https://nova.rc.nectar.org.au:8773/services/cloud",
    "identity": "https://keystone.rc.nectar.org.au:5000/",
    "image": "https://image.rc.nectar.org.au/",
    "key_manager": "https://key-manager.rc.nectar.org.au/",
    "load_balancer": "https://lbaas.rc.nectar.org.au:9876/",
    "message": "https://taynac.rc.nectar.org.au/",
    "metric": "https://gnocchi.rc.nectar.org.au:8041/",
    "nectar ops": "https://status.rc.nectar.org.au/api/",
    "nectar_reservation": "https://warre.rc.nectar.org.au/",
    "network": "https://neutron.rc.nectar.org.au:9696/",
    "object_store": "https://object-store.rc.nectar.org.au/",
    "orchestration": "https://heat.rc.nectar.org.au:8004/",
    "outage": "https://status.rc.nectar.org.au/api/",
    "placement": "https://placement.rc.nectar.org.au/placement/",
    "rating": "https://rating.rc.nectar.org.au/",
    "reservation": "https://reservation.rc.nectar.org.au/",
    "s3": "https://swift.rc.nectar.org.au/",
    "share": "https://manila.rc.nectar.org.au:8786/",
    "sharev2": "https://manila.rc.nectar.org.au:8786/",
    "volumev3": "https://cinder.rc.nectar.org.au:8776/",
}


class NARC:
    def __init__(self):
        """Run first, before load."""
        # Addon defaults
        self.url_filter = "nectar.org.au"
        # Addon options
        self.output_filename = "access_rules"
        self.output_format = "yaml"
        self.remove_uuid_from_path = True
        # Addon data structures
        self.access_rules = list()

        # Load configuration options
        self.endpoints = endpoints.endpoints

    def load(self, loader):
        """Run when addon is loaded, adds optional arguments."""
        loader.add_option(
            name="output",
            typespec=Optional[str],
            default="access_rules",
            help="Specify a custom output file name",
        )
        loader.add_option(
            name="format",
            typespec=Optional[str],
            default="yaml",
            help="Specify JSON or YAML output file format",
        )
        loader.add_option(
            name="uuid",
            typespec=Optional[bool],
            default=True,
            help="Remove UUIDs from end of API path",
        )
        loader.add_option(
            name="wildcard",
            typespec=Optional[bool],
            default=True,
            help="Use wildcard (bare) API paths (less secure, more simple)."
        )

    def configure(self, updated):
        """Run when configuration is updated."""
        if "output" in updated:
            self.output_filename = ctx.options.output
        if "format" in updated:
            self.output_format = ctx.options.format

    def request(self, flow: http.HTTPFlow) -> None:
        """Handle all HTTP/S requests from mitmdump."""
        url = flow.request.url
        method = flow.request.method

        # Skip anything that is not a request to nectar.org.au domain
        if self.url_filter not in url:
            return

        print("[+] Potentially interesting HTTP request...")

        # Skip anything that does not match documented Nectar API endpoints
        matching_endpoint_name = None
        matched = False

        while not matched:
            for endpoint_name, endpoint_path in self.endpoints.items():
                if not url.startswith(endpoint_path):
                    continue
                else:
                    matching_endpoint_name = endpoint_name
                    matched = True

        # Remove parameters from URL
        endpoint_path = url.split("?")[0]

        # Remove UUID from end of path, if request (on by default)
        if self.remove_uuid_from_path:
            is_uuid = False
            endpoint_path_list = endpoint_path.split("/")
            potential_uuid = endpoint_path_list[-1]
            try:
                _ = UUID(potential_uuid)
                is_uuid = True
            except ValueError:
                pass

            if is_uuid:
                del endpoint_path_list[-1]
                endpoint_path = ("/").join(endpoint_path_list)

        tmp_access_rule = {
            "service": matching_endpoint_name,
            "method": method,
            "path": endpoint_path,
        }

        self.access_rules.append(tmp_access_rule)

    def done(self):
        """Run when exiting mitmproxy."""
        # Create a dict of unique keys (method + | + path)
        unique_access_rules = {
            f"{access_rule['method']}|{access_rule['path']}": access_rule for access_rule in self.access_rules
        }
        # Remove the keys to get a list of values
        unique_access_rules = list(unique_access_rules.values())

        # Save output to a file
        with open(f"{self.output_filename}.json", "w") as f:
            json.dump(unique_access_rules, f, indent=4)


addons = [NARC()]
