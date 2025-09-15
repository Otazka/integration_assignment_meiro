import os
import sys
import unittest
from unittest.mock import Mock, patch

# Ensure src is on path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from client import ApiClient
from auth import APIToken
from http_handler import RequestHandler
from interface import AuthService


class ApiClientTests(unittest.TestCase):
    def test_request_injects_bearer_and_returns_json(self):
        auth_service = Mock(spec=AuthService)
        auth_service.get_token.return_value = "token-123"

        request_handler = Mock(spec=RequestHandler)
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.text = '{"ok": true}'
        fake_response.json.return_value = {"ok": True}
        request_handler.send.return_value = fake_response

        client = ApiClient("https://api.example.com", auth_service, request_handler)
        result = client.request("POST", "/banners/show", json={"a": 1})

        self.assertEqual(result, {"ok": True})
        request_handler.send.assert_called_once()
        args, kwargs = request_handler.send.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "https://api.example.com/banners/show")
        self.assertIn("headers", kwargs)
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer token-123")

    def test_request_handles_empty_200_response(self):
        auth_service = Mock(spec=AuthService)
        auth_service.get_token.return_value = "token-123"

        request_handler = Mock(spec=RequestHandler)
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.text = ""  # empty body
        request_handler.send.return_value = fake_response

        client = ApiClient("https://api.example.com", auth_service, request_handler)
        result = client.request("POST", "/banners/show/bulk", json={"Data": []})

        self.assertEqual(result["status"], "success")


class APITokenTests(unittest.TestCase):
    @patch("auth.time")
    def test_auth_success_sets_token_and_expiry(self, mock_time):
        mock_time.time.return_value = 1000.0

        request_handler = Mock(spec=RequestHandler)
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = {"AccessToken": "abc-xyz"}
        request_handler.send.return_value = fake_response

        token_service = APIToken("https://api.example.com", "proj-key", request_handler)
        token = token_service.auth()
        self.assertEqual(token, "abc-xyz")
        # Token should be retrievable via public API
        self.assertEqual(token_service.get_token(), "abc-xyz")
        # Request handler should have been called once for auth
        request_handler.send.assert_called_once()

    @patch("auth.time")
    def test_get_token_refreshes_when_expired(self, mock_time):
        request_handler = Mock(spec=RequestHandler)
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = {"AccessToken": "new-token"}
        request_handler.send.return_value = fake_response

        token_service = APIToken("https://api.example.com", "proj-key", request_handler)
        token_service.access_token = "old-token"
        token_service.token_life = 1000.0

        mock_time.time.return_value = 2000.0  # expired
        token = token_service.get_token()

        self.assertEqual(token, "new-token")
        request_handler.send.assert_called()


class RequestHandlerTests(unittest.TestCase):
    @patch("http_handler.requests.request")
    def test_send_success_no_retry(self, mock_request):
        resp = Mock()
        resp.status_code = 200
        resp.text = '{"ok":true}'
        resp.json.return_value = {"ok": True}
        resp.raise_for_status.return_value = None
        mock_request.return_value = resp

        handler = RequestHandler(max_retries=3)
        out = handler.send("GET", "https://api.example.com/ping")

        self.assertEqual(out, resp)
        mock_request.assert_called_once()

    @patch("http_handler.time.sleep")
    @patch("http_handler.random.uniform", return_value=0.0)
    @patch("http_handler.requests.request")
    def test_send_retries_on_500_and_then_succeeds(self, mock_request, _uniform, _sleep):
        resp1 = Mock(); resp1.status_code = 500; resp1.raise_for_status.side_effect = None
        resp2 = Mock(); resp2.status_code = 200; resp2.raise_for_status.return_value = None
        mock_request.side_effect = [resp1, resp2]

        handler = RequestHandler(max_retries=3)
        out = handler.send("GET", "https://api.example.com/ping")

        self.assertEqual(out.status_code, 200)
        self.assertEqual(mock_request.call_count, 2)

    @patch("http_handler.time.sleep")
    @patch("http_handler.random.uniform", return_value=0.0)
    @patch("http_handler.requests.request")
    def test_send_exhausts_retries_and_raises(self, mock_request, _uniform, _sleep):
        resp = Mock(); resp.status_code = 500
        mock_request.return_value = resp
        resp.raise_for_status.side_effect = Exception("server error")

        handler = RequestHandler(max_retries=2)
        with self.assertRaises(Exception):
            handler.send("GET", "https://api.example.com/ping")

        self.assertGreaterEqual(mock_request.call_count, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
