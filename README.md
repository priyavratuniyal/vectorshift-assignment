# VectorShift Integration API

This project implements OAuth integrations with various services (HubSpot, Notion, and Airtable) with a FastAPI backend and React frontend.

## Project Structure

```
.
├── backend/
│   ├── integrations/
│   │   ├── airtable.py
│   │   ├── notion.py
│   │   ├── hubspot.py
│   │   └── integration_item.py
│   ├── routes/
│   │   └── logs.py
│   ├── config.py
│   ├── logger.py
│   ├── main.py
│   ├── redis_client.py
│   └── requirements.txt
└── frontend/
    ├── public/
    └── src/
        ├── integrations/
        │   ├── airtable.js
        │   ├── notion.js
        │   └── hubspot.js
        ├── services/
        │   └── logger.js
        ├── App.js
        ├── data-form.js
        └── integration-form.js
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server
- HubSpot Developer Account (for testing)

## Setup

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python3 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Redis server:
```bash
redis-server
```

4. Start the backend server:
```bash
uvicorn main:app --reload
```

The backend server will be running at http://localhost:8000

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will be running at http://localhost:3000

## Features

- OAuth 2.0 integration with HubSpot, Notion, and Airtable
- Centralized logging system for both frontend and backend
- Redis-based state management for OAuth flow
- Error handling and monitoring
- Performance tracking for API calls
- User interaction logging

## API Documentation

The API documentation is available at http://localhost:8000/docs when the backend server is running.

### Main Endpoints

- `POST /integrations/{service}/authorize`: Start OAuth flow
- `GET /integrations/{service}/oauth2callback`: OAuth callback handler
- `POST /integrations/{service}/credentials`: Get stored credentials
- `POST /integrations/{service}/load`: Load data from the service

## Logging

The application includes comprehensive logging for both frontend and backend:

### Backend Logs
- Location: `backend/logs/`
- Categories:
  - `app.log`: General application logs
  - `error.log`: Error-level logs
  - `integrations/`: Integration-specific logs

### Frontend Logs
- Development: Console logging
- Production: Sent to backend logging endpoint

## Error Handling

- Frontend: Error boundaries and axios error interceptors
- Backend: Exception handlers and detailed error logging
- OAuth: State validation and token management

## Security

- CORS configuration for frontend-backend communication
- OAuth state validation
- Redis-based token storage with expiration
- Environment variable based configuration

## Development

1. Backend development:
   - Follow FastAPI best practices
   - Use type hints
   - Add logging for new features
   - Update API documentation

2. Frontend development:
   - Follow React best practices
   - Use functional components and hooks
   - Add logging for user interactions
   - Handle loading and error states

## Testing

1. Backend testing:
```bash
cd backend
pytest
```

2. Frontend testing:
```bash
cd frontend
npm test
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add appropriate logging
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
