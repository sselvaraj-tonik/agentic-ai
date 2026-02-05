import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.tools import get_customer_profile

class TestBankingAgent(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.sample_api_response = {
            "data": {
                "profile": [
                    {
                        "custId": "1029763",
                        "email": "Xhjd@hhd.ndn",
                        "mobileNo": "631234567890",
                        "status": "A",
                        "signUpAccNo": "1239832429384",
                        "deviceUid": "oaisjdoaisjdoaisjd",
                        "userId": "1234abc",
                        "rekycFlagCnt": 0
                    }
                ]
            },
            "meta": {
                "totalPages": 1
            },
            "status": {
                "code": "00",
                "message": "Success"
            }
        }

    @patch('app.tools.requests.get')
    def test_get_customer_profile_tool(self, mock_get):
        """Test that the tool correctly calls the API and returns JSON."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the tool
        result = get_customer_profile.invoke("631234567890")

        # Verify request was made correctly
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("https://bank.com/customer/v1/profileinfo", args[0])
        self.assertEqual(kwargs['params'], {'mobileno': '631234567890'})

        # Verify result
        self.assertEqual(result, self.sample_api_response)

    @patch('app.main.agent_executor.invoke')
    def test_chat_endpoint(self, mock_agent_invoke):
        """Test the FastAPI endpoint with a mocked agent response."""
        # Mock the agent output
        mock_agent_invoke.return_value = {
            "messages": [
                MagicMock(content="The user profile has been retrieved.")
            ]
        }

        response = self.client.post("/chat", json={"query": "Get profile for 631234567890"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "The user profile has been retrieved."})

        # Verify agent was called
        mock_agent_invoke.assert_called_once()

if __name__ == '__main__':
    unittest.main()
