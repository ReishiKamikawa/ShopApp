# ShopApp - Production-Grade E-Commerce Backend

A robust, production-oriented backend for an online store built with **FastAPI**, **MongoDB**, and **Redis**. This system is designed with a focus on **SOLID principles**, **Clean Architecture**, and **High Performance**.

---

## 🚀 Project Goals

The objective of ShopApp is to provide a highly extensible and maintainable e-commerce engine that supports:
- **Async Operations**: 100% non-blocking I/O using FastAPI and Motor.
- **Data Consistency**: ACID transactions for critical flows like order processing.
- **Scalability**: Decoupled background workers and event-driven architecture.
- **Advanced Features**: Caching, Rate Limiting, Pub/Sub, and Audit Logging.

---

## 🏗 System Architecture

The project follows a strict **Layered Separation** pattern to ensure modularity and ease of testing:

```text
Client
  |
  v
FastAPI (Controller Layer)
  | ───> Thin controllers, request validation, response formatting.
  v
Service Layer
  | ───> Business rules, Transaction orchestration, Pub/Sub publishing.
  v
Repository Layer
  | ───> Direct MongoDB access, generic CRUD logic.
  v
Infrastructure Layer
  |
  +--> MongoDB (Replica Set REQUIRED for Transactions)
  |
  +--> Redis (Cache Aside, Pub/Sub, Rate Limiting)
         |
         v
   Worker / Background Jobs (Email, Event processing)
```

### Core Design Principles (SOLID)
- **Single Responsibility**: Each class/function has one job.
- **Open/Closed**: Entities are open for extension but closed for modification.
- **Liskov Substitution**: Derived classes are replaceable by their base classes.
- **Interface Segregation**: Clients don't depend on methods they don't use (e.g., generic Controller Interface).
- **Dependency Inversion**: High-level modules don't depend on low-level modules; both depend on abstractions.

---

## 🛠 Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Language** | Python 3.10+ | Utilizing async/await features. |
| **Framework** | FastAPI | High performance, based on Starlette and Pydantic. |
| **Database** | MongoDB 6.0 | Document-oriented with Replica Set for transactions. |
| **DB Driver** | Motor | Async Python driver for MongoDB. |
| **Cache/Queue**| Redis | Caching, Pub/Sub, and Rate Limiting. |
| **Auth** | JWT / Bcrypt | Secure token-based auth and password hashing. |
| **Deployment** | Docker & Compose | Containerized environment and orchestration. |

---

## 💾 Database Design & Rationale

### Relationship Strategy: Why the Choices?

Our MongoDB design balances **Data Integrity** with **Read Performance**:

1.  **Order → Product (Embedded Snapshot)**:
    - **Choice**: When an order is placed, we embed a snapshot of the product (name, price) into the order document.
    - **Why**: Purchase history must be **immutable**. If a product's price changes or it is deleted in the future, the order record remains an accurate historical "truth" of what was purchased.

2.  **Cart → Product (Referential)**:
    - **Choice**: The cart only stores `product_id` and `quantity`.
    - **Why**: Carts are dynamic and transient. Referencing ensures we always show the current price and stock status until the moment of checkout.

3.  **Review → User/Product (Referential)**:
    - **Choice**: Reviews refer to users and products by ID.
    - **Why**: This minimizes data duplication and provides maximum query flexibility (e.g., "Find all reviews by this user" or "Find all reviews for this product").

### Indexing Strategy
- **Unique**: `users.email`, `carts.user_id`, and a compound unique index `reviews(user_id, product_id)` to ensure one review per user/product.
- **Performance**: Text index on `products.name` for search, and indexes on `created_at` or foreign keys for fast filtering/joins.

---

## ⚙️ Core Business Logic

### 🔐 ACID Transactions (Order Flow)
To prevent data corruption, the order creation process is wrapped in a **MongoDB multi-document transaction**:
1. Validate product existence & stock.
2. **Decrease stock atomically** (using conditional updates).
3. Create Order document with product snapshots.
4. Clear User Cart.
5. *Commit if all steps succeed; rollback otherwise.*

### 🛡 Anti-Oversell Strategy
We use **Atomic Conditional Updates**:
```python
# Pseudo-code
db.products.update_one(
    {"_id": pid, "stock": {"$gte": requested_qty}},
    {"$inc": {"stock": -requested_qty}}
)
```
If the update count is 0, the order is rejected immediately, ensuring we never sell more than we have.

---

## 🌟 Advanced Features

### ⚡ Redis Caching (Cache Aside)
- **Patterns**: `GET /products/{id}` and paginated lists are cached.
- **TTL**: 60 seconds.
- **Invalidation**: On any `update` or `delete` operation, the corresponding cache keys are purged immediately to ensure data freshness.

### 📡 Event-Driven System (Pub/Sub)
We decouple side effects from request handlers:
- **Events**: `order.created`, `user.registered`, `product.updated`.
- **Publisher**: Triggered after successful DB commit.
- **Worker**: A separate process consumes these events to handle non-blocking tasks (e.g., sending emails, updating statistics).

### 🚦 Rate Limiting
Redis-based throttling protects sensitive endpoints:
- **Login**: Strict limits by IP.
- **Write Actions**: Limits per User ID.
- **Error Response**: HTTP 429 when limits are exceeded.

---

## 📋 Audit Logging
Every major data mutation (`create`, `update`, `delete`) is recorded in the `audit_logs` collection:
- **Who**: Actor ID and Role.
- **What**: Action and Resource Type.
- **Changes**: `before` and `after` state snapshots (where applicable).
- **Context**: IP address, Request ID, and User Agent.

---

## 🚀 Quick Start

### 🐳 Using Docker (Recommended)
1. **Launch Environment**:
   ```bash
   docker-compose up -d
   ```
2. **Initiate Replica Set** (Required for Transactions):
   ```bash
   docker exec shopapp-mongo mongosh --eval "rs.initiate()"
   ```
3. **Seed Test Data**:
   ```bash
   docker exec shopapp-api python seed_data.py
   ```

### 💻 Local Development
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Environment**: Copy `.env.example` to `.env` and configure your credentials.
3. **Run**: `uvicorn app.main:app --reload`

---

## 📖 API Documentation

Once running, access the interactive documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints
| Category | Routes |
|----------|--------|
| **Auth** | `POST /auth/register`, `POST /auth/login` |
| **Products** | `GET /products`, `POST /products`, `PATCH /products/{id}` |
| **Cart** | `GET /cart`, `POST /cart/add`, `POST /cart/remove` |
| **Orders** | `POST /orders`, `GET /orders/{id}` |
| **Reviews** | `GET /reviews`, `POST /reviews` |

---

## 🔒 Security Summary
- **JWT Authentication** (HS256)
- **Role-Based Access Control** (Admin, Shop, User)
- **Password Hashing** via Bcrypt
- **Rate Limiting** to prevent brute force
- **Input Validation** via Pydantic models

---

**Version**: 1.0.0  
**Status**: Production-Ready  
**Maintainer**: Reishi Kamikawa 
