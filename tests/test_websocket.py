import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestWebSocket:
    """Test WebSocket connections and real-time updates"""

    def test_websocket_connection_with_valid_token(self, test_user, auth_token):
        """Test WebSocket connection with valid authentication"""
        client = TestClient(app)
        
        with client.websocket_connect(f"/api/v1/ws?token={auth_token}") as websocket:
            # Receive welcome message
            data = websocket.receive_json()
            
            assert data["type"] == "connection"
            assert data["status"] == "connected"
            assert "Welcome" in data["message"]
            assert "user_id" in data

    def test_websocket_connection_without_token(self):
        """Test WebSocket connection fails without token"""
        client = TestClient(app)
        
        with pytest.raises(Exception):
            with client.websocket_connect("/api/v1/ws"):
                pass

    def test_websocket_connection_with_invalid_token(self):
        """Test WebSocket connection fails with invalid token"""
        client = TestClient(app)
        
        with pytest.raises(Exception):
            with client.websocket_connect("/api/v1/ws?token=invalid_token_here"):
                pass

    def test_websocket_ping_pong(self, auth_token):
        """Test ping/pong mechanism"""
        client = TestClient(app)
        
        with client.websocket_connect(f"/api/v1/ws?token={auth_token}") as websocket:
            # Skip welcome message
            websocket.receive_json()
            
            # Send ping
            websocket.send_text("ping")
            
            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert "alive" in data["message"].lower()

    def test_websocket_echo(self, auth_token):
        """Test echo functionality"""
        client = TestClient(app)
        
        with client.websocket_connect(f"/api/v1/ws?token={auth_token}") as websocket:
            # Skip welcome message
            websocket.receive_json()
            
            # Send message
            websocket.send_text("hello")
            
            # Receive echo
            data = websocket.receive_json()
            assert data["type"] == "echo"
            assert "hello" in data["message"]

    def test_public_websocket_connection(self):
        """Test public WebSocket connection without authentication"""
        client = TestClient(app)
        
        with client.websocket_connect("/api/v1/ws/public") as websocket:
            # Receive welcome message
            data = websocket.receive_json()
            
            assert data["type"] == "connection"
            assert data["status"] == "connected"
            assert "public" in data["message"].lower()


class TestWebSocketNotifications:
    """Test real-time notifications via WebSocket"""

    def test_transaction_notification(self, client, auth_headers, test_account, auth_token):
        """Test that creating a transaction sends WebSocket notification"""
        test_client = TestClient(app)
        
        with test_client.websocket_connect(f"/api/v1/ws?token={auth_token}") as websocket:
            # Skip welcome message
            websocket.receive_json()
            
            # Create a transaction via HTTP
            transaction_data = {
                "transaction_type": "deposit",
                "amount": 500.00,
                "description": "WebSocket test deposit"
            }
            response = client.post(
                "/api/v1/transactions/",
                json=transaction_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            
            # Receive WebSocket notification
            notification = websocket.receive_json()
            
            assert notification["type"] == "transaction"
            assert notification["event"] == "transaction_created"
            assert notification["transaction"]["type"] == "deposit"
            assert float(notification["transaction"]["amount"]) == 500.00
            assert "account" in notification
            assert notification["account"]["new_balance"] == 500.00

    def test_large_transaction_notification(self, client, auth_headers, test_account, auth_token):
        """Test that large transactions trigger additional notification"""
        test_client = TestClient(app)
        
        with test_client.websocket_connect(f"/api/v1/ws?token={auth_token}") as websocket:
            # Skip welcome message
            websocket.receive_json()
            
            # Create a large transaction
            transaction_data = {
                "transaction_type": "deposit",
                "amount": 15000.00,
                "description": "Large transaction test"
            }
            response = client.post(
                "/api/v1/transactions/",
                json=transaction_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            
            # Receive transaction notification
            transaction_notification = websocket.receive_json()
            assert transaction_notification["type"] == "transaction"
            
            # Receive large transaction processing notification
            processing_notification = websocket.receive_json()
            assert processing_notification["type"] == "notification"
            assert processing_notification["event"] == "large_transaction_processing"
            assert "compliance" in processing_notification["message"].lower()

    def test_account_creation_notification(self, client, auth_headers, auth_token):
        """Test that creating an account sends WebSocket notification"""
        test_client = TestClient(app)
        
        with test_client.websocket_connect(f"/api/v1/ws?token={auth_token}") as websocket:
            # Skip welcome message
            websocket.receive_json()
            
            # Create account via HTTP
            account_data = {
                "account_type": "checking",
                "currency": "USD"
            }
            response = client.post(
                "/api/v1/accounts/",
                json=account_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            
            # Receive WebSocket notification
            notification = websocket.receive_json()
            
            assert notification["type"] == "account"
            assert notification["event"] == "account_created"
            assert notification["account"]["account_type"] == "checking"
            assert "successfully" in notification["message"].lower()


class TestConnectionStats:
    """Test WebSocket connection statistics endpoint"""

    def test_get_connection_stats(self, client, auth_headers):
        """Test getting WebSocket connection statistics"""
        response = client.get("/api/v1/ws/connections", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_connections" in data
        assert "users_connected" in data
        assert isinstance(data["total_connections"], int)
        assert isinstance(data["users_connected"], int)
