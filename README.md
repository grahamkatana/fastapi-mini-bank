# FastAPI Project with JWT Auth, MySQL & Celery

A production-ready FastAPI application with JWT authentication, MySQL database, and Celery for background tasks.

## Features

- ✅ FastAPI with async support
- ✅ JWT Authentication
- ✅ **WebSocket Real-Time Updates** 🔥
- ✅ MySQL Database with SQLAlchemy ORM
- ✅ Celery for background tasks
- ✅ Redis as message broker
- ✅ RESTful API design
- ✅ Auto-generated API documentation (Swagger/ReDoc)
- ✅ Docker support
- ✅ Proper project structure
- ✅ Comprehensive test suite (43+ tests)
- ✅ CI/CD with GitHub Actions

## Project Structure

```
fastapi-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── accounts.py
│   │       └── transactions.py
│   ├── core/                # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py      # Password hashing, JWT
│   │   └── auth.py          # Authentication dependencies
│   └── tasks/               # Celery tasks
│       ├── __init__.py
│       ├── celery_app.py
│       └── celery_tasks.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- username (Unique)
- hashed_password
- is_active
- created_at
- updated_at

### Accounts Table (One-to-One with User)
- id (Primary Key)
- user_id (Foreign Key → Users)
- account_number (Unique)
- account_type
- balance
- currency
- created_at
- updated_at

### Transactions Table (Many-to-One with Account)
- id (Primary Key)
- account_id (Foreign Key → Accounts)
- transaction_type (deposit, withdrawal, transfer)
- amount
- description
- reference_number (Unique)
- created_at

## Setup Instructions

### Option 1: Using Docker (Recommended)

1. **Clone the repository**
```bash
cd fastapi-project
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your settings if needed
```

3. **Start all services with Docker Compose**
```bash
docker-compose up -d
```

This will start:
- MySQL database (port 3306)
- Redis (port 6379)
- FastAPI application (port 8000)
- Celery worker
- Celery beat scheduler

4. **Access the application**
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc

### Option 2: Local Development

1. **Install MySQL and Redis**
```bash
# Install MySQL
# Install Redis

# Start services
mysql.server start
redis-server
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create database**
```bash
mysql -u root -p
CREATE DATABASE fastapi_db;
exit;
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. **Run the application**
```bash
# Terminal 1: FastAPI server
uvicorn app.main:app --reload

# Terminal 2: Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 3: Celery beat (optional, for scheduled tasks)
celery -A app.tasks.celery_app beat --loglevel=info
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users
- `GET /api/v1/users/me` - Get current user info
- `GET /api/v1/users/{user_id}` - Get user by ID

### Accounts
- `POST /api/v1/accounts/` - Create account
- `GET /api/v1/accounts/me` - Get current user's account
- `GET /api/v1/accounts/{account_id}` - Get account by ID

### Transactions
- `POST /api/v1/transactions/` - Create transaction
- `GET /api/v1/transactions/` - Get all transactions (paginated)
- `GET /api/v1/transactions/{transaction_id}` - Get transaction by ID

### WebSocket (Real-Time) 🔥
- `WS /api/v1/ws?token=JWT_TOKEN` - Authenticated real-time updates
- `WS /api/v1/ws/public` - Public announcements
- `GET /api/v1/ws/connections` - WebSocket connection statistics

## Usage Examples

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "secretpassword"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=secretpassword"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Create Account (requires authentication)
```bash
curl -X POST "http://localhost:8000/api/v1/accounts/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "account_type": "savings",
    "currency": "USD"
  }'
```

### 4. Create Transaction
```bash
curl -X POST "http://localhost:8000/api/v1/transactions/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "deposit",
    "amount": 1000.00,
    "description": "Initial deposit"
  }'
```

### 5. Connect to WebSocket for Real-Time Updates

```javascript
const token = "YOUR_JWT_TOKEN";
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws?token=${token}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
    
    if (data.type === 'transaction') {
        console.log(`💰 New ${data.transaction.type}: ${data.account.currency} ${data.transaction.amount}`);
        console.log(`📊 Balance: ${data.account.new_balance}`);
    }
};
```

Or use the included HTML client:
```bash
open websocket_client.html  # Opens interactive WebSocket tester
```

## Celery Tasks

The project includes sample Celery tasks for background processing:

### 1. Process Large Transaction
Automatically triggered when transaction amount > 10,000
```python
process_large_transaction.delay(transaction_id, amount)
```

### 2. Send Monthly Report
```python
from app.tasks import send_monthly_report
send_monthly_report.delay(user_id)
```

### 3. Data Cleanup
```python
from app.tasks import cleanup_old_data
cleanup_old_data.delay()
```

## Testing the API

### Using Swagger UI
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Register a user, login, and use the token
4. Try all endpoints interactively

### Using curl
See the usage examples above

### Using Python requests
```python
import requests

# Register
response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
)

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "testuser", "password": "testpass123"}
)
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers)
print(response.json())
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | MySQL connection string | - |
| SECRET_KEY | JWT secret key | - |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 |
| CELERY_BROKER_URL | Redis URL for Celery | - |
| CELERY_RESULT_BACKEND | Redis URL for results | - |
| APP_NAME | Application name | FastAPI Project |
| DEBUG | Debug mode | False |

## Security Notes

1. **Change the SECRET_KEY** in production
2. **Use strong passwords** for database
3. **Configure CORS** properly for production
4. **Use HTTPS** in production
5. **Implement rate limiting** for API endpoints
6. **Add input validation** for all user inputs

## Development Tips

### Database Migrations (Optional - Alembic)
```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Monitor Celery Tasks
```bash
# Using Flower
pip install flower
celery -A app.tasks.celery_app flower
# Access: http://localhost:5555
```

### Run Tests
```bash
pip install pytest pytest-asyncio httpx
pytest
```

## Troubleshooting

### MySQL Connection Issues
- Ensure MySQL is running
- Check DATABASE_URL in .env
- Verify MySQL user has proper permissions

### Celery Not Processing Tasks
- Ensure Redis is running
- Check CELERY_BROKER_URL
- Verify Celery worker is running

### JWT Token Issues
- Check SECRET_KEY is set
- Ensure token hasn't expired
- Verify Authorization header format: "Bearer <token>"

## License

MIT License

## Contributing

Pull requests are welcome!
