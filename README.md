# Flask + MongoDB User Management API

A scalable, production-ready REST API for user management, built with Flask, MongoDB, JWT authentication, and Docker. Includes interactive Swagger (OpenAPI) documentation.

---

## Features
- User CRUD (Create, Read, Update, Delete) via RESTful endpoints
- JWT authentication for protected routes
- MongoDB for persistent storage
- Dockerized for easy local development
- Interactive API docs with Swagger UI (`/apidocs`)

---

## Requirements
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/)

---

## Getting Started

### 1. Clone the Repository
```sh
git clone <your-repo-url>
cd flask_assignment
```

### 2. Build and Start the Containers
```sh
docker-compose up --build
```
- The Flask API will be available at [http://localhost:5000](http://localhost:5000)
- The Swagger UI will be available at [http://localhost:5000/apidocs](http://localhost:5000/apidocs)

### 3. Stopping the Containers
```sh
docker-compose down
```

---

## API Endpoints

### **Authentication**
- `POST /auth/login` — Log in and receive a JWT access token

### **User Management**
- `POST /users` — Register a new user (open)
- `GET /users` — Get all users (**JWT required**)
- `GET /users/<id>` — Get user by ID (**JWT required**)
- `PUT /users/<id>` — Update user by ID (**JWT required**)
- `DELETE /users/<id>` — Delete user by ID (**JWT required**)

---

## Using the API

### 1. Register a User
```json
POST /users
{
  "name": "Alice",
  "email": "alice@example.com",
  "password": "securepassword"
}
```

### 2. Log In
```json
POST /auth/login
{
  "email": "alice@example.com",
  "password": "securepassword"
}
```
- Copy the `access_token` from the response.

### 3. Authorize in Swagger UI
- Click the **Authorize** button in `/apidocs` and enter:
  ```
  Bearer <access_token>
  ```
- Now you can use protected endpoints directly from the Swagger UI.

---

## Database Access
- MongoDB is available on `localhost:27018` (default Docker mapping).
- Connect with MongoDB Compass or `mongosh`:
  ```
  mongodb://root:pass@localhost:27018/intern?authSource=admin
  ```

---

## Data Persistence
- MongoDB data is stored in a Docker volume (`mongo_data`) and will persist across container restarts.

---

## Troubleshooting
- If you see `ServerSelectionTimeoutError`, ensure both `app` and `db` containers are running (`docker ps`).
- If MongoDB fails to start after an upgrade, remove the volume with `docker volume rm flask_assignment_mongo_data` and restart.

---

## License
MIT 