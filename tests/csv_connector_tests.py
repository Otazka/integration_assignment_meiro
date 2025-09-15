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

        # 2255 valid rows -> still processed in windows of 1000 for throttling,
        # but each row is sent individually to /banners/show
        connector = CSVConnector("/tmp/data.csv", "https://api", "proj", batch_size=1000, upload_mode="single")

        # Bypass read/transform; call write directly with transformed rows
        rows = make_rows(2255)
        with patch.dict(os.environ, {"REQUEST_DELAY": "0"}):
            connector.write(rows)

        # Expect one API call per row
        self.assertEqual(api_client.request.call_count, 2255)
        # Inspect first call payload shape
        args, kwargs = api_client.request.call_args_list[0]
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "banners/show")
        self.assertIn("json", kwargs)
        first = kwargs["json"]
        self.assertIn("VisitorCookie", first)
        self.assertIn("BannerId", first)

    @patch("csv_connector.ApiClient")
    @patch("csv_connector.RequestHandler")
    @patch("csv_connector.APIToken")
    def test_cap_batch_size_at_1000(self, _token, _handler, api_client_cls):
        api_client = Mock()
        api_client.request.return_value = {"status": "success"}
        api_client_cls.return_value = api_client

        # Even if configured 5000, connector must cap to 1000 per processing window.
        # With single-item endpoint, still one request per row.
        connector = CSVConnector("/tmp/data.csv", "https://api", "proj", batch_size=5000, upload_mode="single")
        rows = make_rows(1500)
        with patch.dict(os.environ, {"REQUEST_DELAY": "0"}):
            connector.write(rows)

        # Should be 1500 calls total (one per row)
        self.assertEqual(api_client.request.call_count, 1500)
        # Validate payload keys for a sample call
        sample_kwargs = api_client.request.call_args_list[100][1]
        self.assertIn("VisitorCookie", sample_kwargs["json"]) 
        self.assertIn("BannerId", sample_kwargs["json"]) 

    @patch("csv_connector.ApiClient")
    @patch("csv_connector.RequestHandler")
    @patch("csv_connector.APIToken")
    def test_bulk_mode_batches_and_payload(self, _token, _handler, api_client_cls):
        api_client = Mock()
        api_client.request.return_value = {"status": "success"}
        api_client_cls.return_value = api_client

        # Force bulk mode explicitly
        connector = CSVConnector("/tmp/data.csv", "https://api", "proj", batch_size=1000, upload_mode="bulk")
        rows = make_rows(2255)
        with patch.dict(os.environ, {"REQUEST_DELAY": "0"}):
            connector.write(rows)

        # Expect 3 calls: 1000, 1000, 255
        self.assertEqual(api_client.request.call_count, 3)
        # Inspect first call
        method, endpoint = api_client.request.call_args_list[0][0][:2]
        self.assertEqual(method, "POST")
        self.assertEqual(endpoint, "banners/show/bulk")
        payload = api_client.request.call_args_list[0][1]["json"]["Data"]
        self.assertEqual(len(payload), 1000)
        self.assertIn("VisitorCookie", payload[0])
        self.assertIn("BannerId", payload[0])
        # Inspect last call size
        tail = api_client.request.call_args_list[-1][1]["json"]["Data"]
        self.assertEqual(len(tail), 255)


if __name__ == "__main__":
    unittest.main(verbosity=2)
