# Survey API Backend

Secure FastAPI backend for the Club/Event Survey application.

## Features

- **Rate Limiting**: 5 requests per minute per IP address
- **CORS Protection**: Configurable allowed origins
- **Input Validation**: Length limits and type checking on all inputs
- **Error Handling**: Graceful handling of duplicate submissions and database errors
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, CSP, HSTS
- **Logging**: Comprehensive logging of all requests and errors
- **Environment Variables**: Secure configuration management

## Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Update the values as needed for your environment

5. **Run the development server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Environment Variables

See `.env.example` for all available configuration options.

### Key Variables:

- `DATABASE_URL`: Database connection string
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `ENVIRONMENT`: Set to 'production' in production
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Production Deployment

### Important Steps:

1. **Switch to PostgreSQL**:
   - SQLite is not recommended for production
   - Update `DATABASE_URL` to use PostgreSQL or MySQL

2. **Update CORS origins**:
   - Set `ALLOWED_ORIGINS` to your production domain(s)
   - Remove localhost/127.0.0.1 from allowed origins

3. **Enable HTTPS**:
   - Use a reverse proxy (Nginx, Caddy) with SSL/TLS
   - The API includes HSTS headers for HTTPS enforcement

4. **Set up monitoring**:
   - Monitor logs for errors and suspicious activity
   - Set up alerts for rate limit violations

5. **Database backups**:
   - Implement automated backup strategy
   - Test restoration procedures

## API Endpoints

### POST /submit
Submit a survey response.

**Rate Limit**: 5 requests per minute per IP

**Request Body**: See Pydantic models in `main.py`

**Responses**:
- 200: Survey submitted successfully
- 400: Validation error or duplicate submission
- 429: Rate limit exceeded
- 500: Server error

### GET /
API information and available endpoints.

### GET /health
Health check endpoint for monitoring.

## Security Features

### Rate Limiting
- Backend enforces 5 submissions per minute per IP address
- Returns 429 status code when limit exceeded

### Input Validation
- All text fields have maximum length constraints
- Numeric fields have min/max value validation
- Email addresses are validated and must be unique

### Error Handling
- Database errors are caught and logged
- Duplicate email submissions return user-friendly error
- Stack traces are never exposed to clients

### Security Headers
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `Content-Security-Policy` - Restricts resource loading
- `Strict-Transport-Security` - Enforces HTTPS

### Logging
- All submissions are logged with IP address
- Errors are logged with full stack traces
- Duplicate submission attempts are logged

## Development

### Running Tests
```bash
# Add tests using pytest
pytest
```

### Code Quality
```bash
# Format code
black main.py

# Lint code
flake8 main.py
pylint main.py
```

## Troubleshooting

### Database locked error
If using SQLite in development and you get "database is locked" errors, ensure:
- Only one process is accessing the database
- Close any database browser tools
- Consider using PostgreSQL instead

### CORS errors
If the frontend can't connect:
- Check `ALLOWED_ORIGINS` includes your frontend URL
- Verify the frontend is making requests to the correct API URL
- Check browser console for specific CORS error messages

### Rate limit issues
If legitimate users are being rate limited:
- Adjust the rate limit in `main.py` (currently 5/minute)
- Consider implementing user-based rate limiting instead of IP-based
- Check if you're behind a proxy that masks real IP addresses
