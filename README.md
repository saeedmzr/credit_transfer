# credit_app

A Django-based credit transfer application with wallet management, charges, transfers, and user authentication. This project leverages Docker, Celery, PostgreSQL, Redis, and a robust test suite to ensure transactional safety and concurrency handling.

---

## Installation

### Clone the repository

    git clone git@github.com:saeedmzr/credit_transfer.git
    cd credit_app

### (Optional) Create and activate a Python virtual environment

    python3.12 -m venv venv
    source venv/bin/activate

### Install Python dependencies

    pip install -r requirements/local.txt

### Environment configuration

Create a `.env` file in the root directory with required environment variables:

- `STAGE=local`
- PostgreSQL credentials (DB name, user, password, host, port)
- `SECRET_KEY` and other Django settings
- Redis / Celery configuration as needed

### Run database migrations

    python manage.py migrate

### Create a superuser

    python manage.py createsuperuser

### Run the development server

    python manage.py runserver

---

## Makefile

The project ships with a `Makefile` to simplify common operations. It reads `STAGE` from `.env` and currently supports `local` using `docker-compose.yml`.

### Key targets

**Build & start services**

    make build

**Recreate containers**

    make recreate

**Start / stop / down / ps**

    make up
    make stop
    make down
    make ps

**Shell into the app container**

    make shell
    make shell_as_root

**Run tests (inside the app container)**

    make test

**Run migrations (inside the app container)**

    make migrate

**Local venv + install (non‑docker)**

    make venv
    make install

**Create superuser (inside the app container)**

    make createsuperuser

---

## Docker Setup

The stack is defined in `docker-compose.yml`:

### db

PostgreSQL 14 instance with persistent volume `postgres_data`.

### pgadmin

PgAdmin4 on port `5050`, useful for inspecting the Postgres database.

### app

Django application container:

- Runs migrations and `collectstatic` on startup.
- Serves the app via `runserver` on `0.0.0.0:8000`.
- Mounts project source at `/app` for live code changes in development.

### celery-worker

Celery worker process:

    celery -A credit_transfer worker --loglevel=info

### celery-beat

Celery beat scheduler:

    celery -A credit_transfer beat --loglevel=info

### flower

Celery monitoring UI on port `5555`:

    celery -A credit_transfer flower --loglevel=info --port=5555

### redis

Redis used as broker / backend for Celery and as a general cache. Data persisted in `redis_data`.

### nginx

Reverse proxy and static asset server:

- HTTP on port `8070`
- HTTPS on port `443`
- Uses config from `docker/nginx/nginx.conf` and TLS files from `docker/nginx/certs`.

All services share the `web_credit_transfer` Docker network.

### Common workflows

    # Start everything
    make build

    # View logs
    docker compose logs -f app
    docker compose logs -f celery
    docker compose logs -f celery-beat
    docker compose logs -f flower

    # Stop & remove
    make down

---

## Architecture

- **Framework:** Django + Django REST Framework.
- **Domain:** Credit transfer system with:
  - Users and profiles
  - Wallets with computed balances based on transactions
  - Charges (top-ups) requiring admin approval/decline
  - Transfers between wallets (sync and async)
- **Services layer:**
  - `approve_charge_service` and `decline_charge_service` encapsulate charge processing logic.
  - `create_transfer_sync` encapsulates transfer logic using `transaction.atomic` and `select_for_update` to prevent race conditions and double spending.
- **Async processing:**
  - Celery workers handle async transfer creation (`create_transfer_async_task`) and can be extended for other background jobs.
- **Permissions / Security:**
  - Custom permissions like `IsAdminOrOwner` and `IsAdminPermission`.
  - Querysets restricted in viewsets so:
    - Admins see all records.
    - Normal users see only their own wallets, transactions, charges, and transfers.
- **Audit / Logging:**
  - `auditlog` integration for tracking changes to `User` (excluding sensitive fields like password).

---

## Tests

The project includes a rich test suite using Django’s `APITestCase` and `TransactionTestCase`:

### Users

Login tests for:

- Admin users
- Normal users
- Invalid credentials

`UserViewSet` tests for:

- Listing users with authentication and role checks
- Retrieving a specific user
- Getting current user (`/me`)
- Creating, updating, deleting users with admin / owner permissions

### Billing – Wallets

`WalletViewSet` tests:

- Authentication required for listing
- Owners and admins can retrieve a wallet
- Other normal users cannot access wallets they do not own
- Wallet responses include computed `balance`

### Billing – Charges

#### Charge visibility and permissions:

- User sees only own charges
- User cannot see other users’ charges
- Charge creation limited to the wallet owner

#### Charge lifecycle:

- Creating a charge does **not** change wallet balance immediately
- Admin approval increases wallet balance by the charge amount
- Admin decline leaves wallet balance unchanged

Approve / decline endpoints:

- Access control for admin vs owner
- Service functions (`approve_charge_service`, `decline_charge_service`) are called correctly

### Billing – Transfers

`TransferViewSet` tests:

- Auth required for creating async transfers
- Owners can create async transfers and receive a `task_id`
- Owners can create sync transfers and receive a `Transfer` object with correct fields

### Transaction tests:

- Users can see their own wallets and transactions
- Users cannot see other users’ transactions
- Sync transfer creation directly changes balances in accordance with business logic

### Concurrency & Double Spending

Using `TransactionTestCase` and threads:

- **Double spending prevention:**
  - Two simultaneous transfer attempts from the same wallet where only one should succeed due to insufficient remaining balance
  - Final balances match exactly one successful transfer and one failure with `"Insufficient balance"`
- **Multiple concurrent transfers:**
  - Several threads perform transfers in parallel
  - Total debits and credits match the number of successful transfers
  - Balances remain consistent thanks to `select_for_update` and atomic transactions
- **Rapid sequential transfers:**
  - Fast loop of synchronous transfers from one wallet to another
  - Stops on first failure and verifies aggregate balance changes are correct

Run tests via Docker:

    make test

Or locally (without Docker):

    python manage.py test