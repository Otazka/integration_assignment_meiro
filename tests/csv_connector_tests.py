import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from csv_connector import CSVConnector


def make_rows(n):
    rows = []
    for i in range(n):
        rows.append({
            "customer_name": f"User {i}",
            "customer_age": 25,
            "customer_cookies": f"cookie-{i}",
            "customer_banner_id": 15,
        })
    return rows


class CSVConnectorTests(unittest.TestCase):
    @patch("csv_connector.ApiClient")
    @patch("csv_connector.RequestHandler")
    @patch("csv_connector.APIToken")
    def test_batching_and_payload_shape(self, _token, _handler, api_client_cls):
        api_client = Mock()
        api_client.request.return_value = {"status": "success"}
        api_client_cls.return_value = api_client

        # 2255 valid rows -> expect 3 batches: 1000, 1000, 255
        connector = CSVConnector("/tmp/data.csv", "https://api", "proj", batch_size=1000)

        # Bypass read/transform; call write directly with transformed rows
        rows = make_rows(2255)
        connector.write(rows)

        self.assertEqual(api_client.request.call_count, 3)
        # Inspect first call
        args, kwargs = api_client.request.call_args_list[0]
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "banners/show/bulk")
        self.assertIn("json", kwargs)
        data = kwargs["json"]["Data"]
        self.assertEqual(len(data), 1000)
        self.assertIn("VisitorCookie", data[0])
        self.assertIn("BannerId", data[0])

        # Inspect last call size
        last_args, last_kwargs = api_client.request.call_args_list[-1]
        tail = last_kwargs["json"]["Data"]
        self.assertEqual(len(tail), 255)

    @patch("csv_connector.ApiClient")
    @patch("csv_connector.RequestHandler")
    @patch("csv_connector.APIToken")
    def test_cap_batch_size_at_1000(self, _token, _handler, api_client_cls):
        api_client = Mock()
        api_client.request.return_value = {"status": "success"}
        api_client_cls.return_value = api_client

        # Even if configured 5000, connector must cap to 1000
        connector = CSVConnector("/tmp/data.csv", "https://api", "proj", batch_size=5000)
        rows = make_rows(1500)
        connector.write(rows)

        # Should be 2 calls: 1000 + 500
        self.assertEqual(api_client.request.call_count, 2)

        first = api_client.request.call_args_list[0][1]["json"]["Data"]
        second = api_client.request.call_args_list[1][1]["json"]["Data"]
        self.assertEqual(len(first), 1000)
        self.assertEqual(len(second), 500)


if __name__ == "__main__":
    unittest.main(verbosity=2)
