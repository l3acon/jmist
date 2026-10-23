"""Offline regression coverage for the survey-driven WxTag demo jobs."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ansible.errors import AnsibleFilterError


ROOT = Path(__file__).resolve().parents[1]
FILTER_PATH = (
    ROOT / "build/collections/ansible_collections/l3acon/jmist/plugins/filter/mist.py"
)
SPEC = importlib.util.spec_from_file_location("mist_filters", FILTER_PATH)
FILTERS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FILTERS)

MAC_A = "a8:53:7d:89:7e:7d"
MAC_B = "d4:dc:09:2a:7b:4d"
ID_A = "00000000-0000-0000-1000-a8537d897e7d"
ID_B = "00000000-0000-0000-1000-d4dc092a7b4d"
ID_OTHER = "00000000-0000-0000-1000-001122334455"


class BatchFilterTests(unittest.TestCase):
    def test_text_separators_formats_and_duplicates(self):
        self.assertEqual(
            FILTERS.macs_to_ap_ids(
                "\r\n A8:53:7D:89:7E:7D, d4-dc-09-2a-7b-4d\n"
                "a853.7d89.7e7d\tD4DC092A7B4D, \n"
            ),
            [ID_A, ID_B],
        )

    def test_yaml_list_and_single_device(self):
        self.assertEqual(FILTERS.macs_to_ap_ids([MAC_A, MAC_B]), [ID_A, ID_B])
        self.assertEqual(FILTERS.macs_to_ap_ids(MAC_A), [ID_A])

    def test_reject_empty_or_invalid_input(self):
        for value in (None, 123, {}, [], "", " \n, ", [None], [123], [""],
                      [MAC_A, "invalid"], "a8:53:7d:89:7e:zz"):
            with self.subTest(value=value), self.assertRaises(AnsibleFilterError):
                FILTERS.macs_to_ap_ids(value)


class FakeMistHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, body):
        encoded = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        self.server.requests.append(("GET", self.path))
        if self.path == "/api/v1/self":
            self.respond({"privileges": [{"scope": "org", "org_id": "test-org"}]})
        elif self.path == "/api/v1/orgs/test-org/wxtags":
            self.respond([self.server.label])
        elif self.path == "/api/v1/orgs/test-org/wxtags/test-tag":
            self.respond(self.server.label)
        else:
            self.send_error(404)

    def do_PUT(self):
        self.server.requests.append(("PUT", self.path))
        if self.path != "/api/v1/orgs/test-org/wxtags/test-tag":
            self.send_error(404)
            return
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.updates.append(payload)
        self.server.label.update(payload)
        self.respond(self.server.label)


@unittest.skipUnless(shutil.which("ansible-playbook"), "ansible-playbook is required")
class DemoPlaybookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeMistHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.server.label = {
            "id": "test-tag", "name": "demo-label", "type": "match",
            "match": "ap_id", "op": "in", "values": [ID_OTHER],
        }
        self.server.requests = []
        self.server.updates = []

    def launch(self, operation, inputs, *, check=False, success=True):
        variables = {
            "org_id": "test-org", "tag_name": "demo-label",
            "mist_token": "offline-test-token",
            "mist_base_url": "http://127.0.0.1:{0}".format(self.server.server_port),
            **inputs,
        }
        with tempfile.TemporaryDirectory() as directory:
            extra_vars = Path(directory) / "vars.json"
            extra_vars.write_text(json.dumps(variables))
            command = [
                "ansible-playbook", "-i", "localhost,",
                "playbooks/mist_wxtag_{0}_ap.yaml".format(operation),
                "-e", "@{0}".format(extra_vars),
            ]
            if check:
                command.append("--check")
            result = subprocess.run(
                command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, timeout=60,
            )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stdout

    def test_assign_batch_preserves_existing_members_and_is_idempotent(self):
        inputs = {"ap_macs": MAC_A + ",\n" + MAC_B + " " + MAC_A.upper()}
        self.launch("assign", inputs)
        self.assertEqual(self.server.label["values"], [ID_OTHER, ID_A, ID_B])
        self.assertEqual(len(self.server.updates), 1)
        output = self.launch("assign", inputs)
        self.assertIn("changed=0", output)
        self.assertEqual(len(self.server.updates), 1)

    def test_remove_batch_preserves_other_members_and_is_idempotent(self):
        self.server.label["values"] = [ID_A, ID_OTHER, ID_B]
        inputs = {"ap_macs": [MAC_A, MAC_B, MAC_A]}
        self.launch("remove", inputs)
        self.assertEqual(self.server.label["values"], [ID_OTHER])
        self.assertEqual(len(self.server.updates), 1)
        output = self.launch("remove", inputs)
        self.assertIn("changed=0", output)
        self.assertEqual(len(self.server.updates), 1)

    def test_remove_all_members_leaves_the_label(self):
        self.server.label["values"] = [ID_A, ID_B]
        self.launch("remove", {"ap_macs": [MAC_A, MAC_B]})
        self.assertEqual(self.server.label["values"], [])
        self.assertEqual(self.server.label["id"], "test-tag")

    def test_check_mode_previews_both_operations_without_writes(self):
        for operation in ("assign", "remove"):
            with self.subTest(operation=operation):
                self.setUp()
                self.server.label["values"] = [ID_OTHER, ID_A]
                output = self.launch(operation, {"ap_macs": [MAC_A, MAC_B]}, check=True)
                self.assertIn("changed=1", output)
                self.assertTrue(self.server.requests)
                self.assertEqual(self.server.updates, [])
                self.assertEqual(self.server.label["values"], [ID_OTHER, ID_A])

    def test_legacy_single_device_launches(self):
        self.launch("assign", {"ap_mac": MAC_A})
        self.assertEqual(self.server.label["values"], [ID_OTHER, ID_A])
        self.launch("remove", {"ap_mac": MAC_A})
        self.assertEqual(self.server.label["values"], [ID_OTHER])

    def test_batch_variable_takes_precedence(self):
        self.launch("assign", {"ap_mac": "invalid", "ap_macs": [MAC_A, MAC_B]})
        self.assertEqual(self.server.label["values"], [ID_OTHER, ID_A, ID_B])

    def test_invalid_batch_fails_before_any_api_calls(self):
        for operation in ("assign", "remove"):
            with self.subTest(operation=operation):
                output = self.launch(
                    operation, {"ap_macs": [MAC_A, "invalid"]}, success=False,
                )
                self.assertIn("Invalid MAC address at position 2", output)
                self.assertEqual(self.server.requests, [])

    def test_missing_or_empty_batch_fails_before_any_api_calls(self):
        for inputs in ({}, {"ap_macs": " \n, "}, {"ap_macs": [], "ap_mac": MAC_A}):
            with self.subTest(inputs=inputs):
                output = self.launch("assign", inputs, success=False)
                self.assertIn("at least one MAC address", output)
                self.assertEqual(self.server.requests, [])


if __name__ == "__main__":
    unittest.main()
