# URL Shortener API

This is a Django-based URL shortener application that allows users to create, manage, and track short URLs. It provides a RESTful API for creating, retrieving, updating, and deleting links, as well as tracking analytics for each link.

## Features

*   **URL Shortening:** Create short codes for long URLs.
*   **User Authentication:** User registration and JWT-based authentication.
*   **Link Management:** Create, retrieve, update, and delete short links.
*   **Link Analytics:** Track the number of clicks, as well as clicks by country and device.
*   **Redirection:** Redirects short URLs to their original long URLs and logs the click.
*   **Anonymous Usage:** Allows anonymous users to create short links.

## Technologies Used

*   **Backend:**
    *   Python
    *   Django
    *   Django REST Framework
    *   Simple JWT for authentication
    *   MySQL (or other database supported by Django)
*   **Deployment:**
    *   PythonAnywhere (or any other WSGI-compliant server)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ruldak/django_url_shortener_api.git your_directory
    cd your_directory
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file** in the project root and add the following environment variables:
    ```
    SECRET_KEY=django-insecure-xxxxxxxxxxxxxx
    DEBUG=True
    CORS_ALLOWED_ORIGINS=your-allowed-origins

    SECRET_KEY=your-secret-key
    DB_NAME=your-db-name
    DB_USER=your-db-user
    DB_PASSWORD=your-db-password
    DB_HOST=your-db-host
    DB_PORT=your-db-port
    ```

5.  **Run the database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## API Endpoints

### Authentication

*   `POST /register/`: Register a new user.
*   `POST /api/token/`: Obtain a JWT token pair (access and refresh).
*   `POST /api/token/refresh/`: Refresh an expired access token.

### Links

*   `GET /api/links/`: List all active links for the authenticated user.
*   `POST /api/links/`: Create a new short link.
*   `GET /api/links/<short_code>/`: Retrieve the details of a specific link.
*   `PUT /api/links/<short_code>/`: Update a specific link.
*   `DELETE /api/links/<short_code>/`: Delete a specific link.
*   `GET /api/links/<short_code>/analytics/`: Get analytics for a specific link.

### Redirection

*   `GET /r/<short_code>/`: Redirect to the original long URL.

