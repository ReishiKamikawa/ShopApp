# ShopApp - E-Commerce Mini Backend System

A fully functional e-commerce backend API built with FastAPI, MongoDB, and Redis.

## 🚀 Quick Start

### Run on Docker
```bash
docker-compose up -d
```

### Seed Test Data
```bash
docker exec shopapp-api python seed_data.py
```

### Access API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📋 Test Credentials

Use these to test authenticated endpoints in Swagger UI:

```
User 1:
  Email: user1@example.com
  Password: password123

User 2:
  Email: user2@example.com
  Password: password456
```

---

## 🧪 All API Endpoints - Ready for Testing

### Authentication
- ✅ `POST /auth/register` - Register new user
- ✅ `POST /auth/login` - Login & get JWT token

### Products
- ✅ `GET /products` - List all products (paginated)
- ✅ `GET /products/{id}` - Get single product
- ✅ `POST /products` - Create new product
- ✅ `PATCH /products/{id}` - Update product
- ✅ `DELETE /products/{id}` - Delete product

### Cart (Requires Auth)
- ✅ `GET /cart` - View your cart
- ✅ `POST /cart/add` - Add item to cart
- ✅ `POST /cart/remove` - Remove item from cart

### Orders (Requires Auth)
- ✅ `GET /orders` - List your orders
- ✅ `GET /orders/{id}` - Get order details
- ✅ `POST /orders` - Create order from cart

### Reviews
- ✅ `GET /reviews` - List all reviews
- ✅ `GET /reviews/{id}` - Get review details
- ✅ `GET /reviews/product/{product_id}` - Get product reviews
- ✅ `POST /reviews` - Create review (Requires Auth)
- ✅ `DELETE /reviews/{id}` - Delete review

---

## 📊 Seeded Test Data

**5 Products:**
1. Laptop Pro - $1,499.99
2. Wireless Mouse - $29.99
3. USB-C Hub - $49.99
4. Mechanical Keyboard - $149.99
5. 4K Monitor - $599.99

**Pre-created Resources:**
- 2 test users with carts
- 2 sample orders
- 5 product reviews

---

## 🧑‍💻 Testing Examples

### 1. Login & Get Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "password": "password123"
  }'
```

### 2. Add to Cart
```bash
curl -X POST http://localhost:8000/cart/add \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PRODUCT_ID",
    "quantity": 2
  }'
```

### 3. Create Order
```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

### 4. Leave Review
```bash
curl -X POST http://localhost:8000/reviews \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PRODUCT_ID",
    "rating": 5,
    "comment": "Great product!"
  }'
```

---

## 📖 Detailed Documentation

See [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) for:
- ✅ Successful test cases
- ❌ Failure test cases
- 🔑 Authentication flows
- 🧪 Complete testing scenarios
- 📋 Expected status codes

---

## 🐳 Docker Services

| Service | Port | Status |
|---------|------|--------|
| FastAPI | 8000 | ✅ Running |
| MongoDB | 27017 | ✅ Running |
| Redis | 6379 | ✅ Running |
| Worker | — | ✅ Running |

---

## 📁 Project Structure

```
ShopApp/
├── app/
│   ├── api/routes/          # API endpoints
│   ├── services/            # Business logic
│   ├── repositories/        # Data access
│   ├── controllers/         # Request handling
│   ├── db/                  # Database connections
│   ├── core/                # Config & security
│   ├── schemas/             # Pydantic models
│   └── main.py              # FastAPI app
├── docker-compose.yml       # Container orchestration
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
├── seed_data.py            # Database seeding script
└── API_TESTING_GUIDE.md    # Comprehensive testing guide
```

---

## 🔧 Development

### Install Locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run Locally (with Docker MongoDB/Redis)
```bash
# Start only MongoDB and Redis
docker-compose up -d mongodb redis

# Run app
uvicorn app.main:app --reload
```

---

## ✨ Features

✅ User authentication with JWT
✅ Product management (CRUD)
✅ Shopping cart functionality
✅ Order creation and tracking
✅ Product reviews and ratings
✅ MongoDB database with async operations
✅ Redis caching
✅ Comprehensive error handling
✅ Full API documentation with Swagger
✅ Input validation with Pydantic
✅ Example data and test cases

---

## 🚦 Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Server Error |

---

## 📞 Support

All endpoints are documented in Swagger UI at http://localhost:8000/docs

Each endpoint includes:
- ✅ Successful examples
- ❌ Failure cases
- 📝 Parameter descriptions
- 📊 Response schemas

---

**Version**: 1.0.0  
**Last Updated**: April 2026
