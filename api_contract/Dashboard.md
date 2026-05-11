# Dashboard API

Base URL:

`/api/v1/dashboard/`

---

## Get Dashboard Data

`GET /api/v1/dashboard/`

### Description

Retrieves dashboard data for the currently logged-in user, including basic user information and role-specific statistics.

### Authentication

Authentication required.

### Request Body

No request body.

### Success Response

#### Tenant Response

Status: `200 OK`

```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "tenant",
    "display_name": "John Smith",
    "avatar_url": "https://cdn.example.com/avatars/xxx.jpg",
    "phone_number": "0412 345 678",
    "status": "active",
    "is_email_verified": true,
    "created_at": "2026-05-01T10:00:00Z"
  },
  "stats": {
    "saved_listings_count": 5,
    "reports_count": 2
  }
}
```

#### Landlord Response

Status: `200 OK`

```json
{
  "user": {
    "id": "uuid",
    "email": "landlord@example.com",
    "role": "landlord",
    "display_name": "Jane Property",
    "avatar_url": "https://cdn.example.com/avatars/xxx.jpg",
    "phone_number": "0413 456 789",
    "status": "active",
    "is_email_verified": true,
    "created_at": "2026-05-01T10:00:00Z"
  },
  "stats": {
    "total_listings": 3,
    "published_listings": 2,
    "pending_review_listings": 1,
    "archived_listings": 4
  }
}
```

#### Admin Response

Status: `200 OK`

```json
{
  "user": {
    "id": "uuid",
    "email": "admin@example.com",
    "role": "admin",
    "display_name": "Administrator",
    "avatar_url": "https://cdn.example.com/avatars/admin.jpg",
    "phone_number": null,
    "status": "active",
    "is_email_verified": true,
    "created_at": "2026-05-01T10:00:00Z"
  },
  "stats": {
    "total_users": 128,
    "total_listings": 45,
    "pending_review_listings": 5,
    "pending_reports": 3
  }
}
```

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Business Rules

- Returns information for the currently logged-in user (joined from `users` table and `profile` table)
- `display_name`, `avatar_url`, and `phone_number` return `null` if not set
- Returns different statistics structures based on `role`

**Tenant statistics:**
- `saved_listings_count`: Number of saved/favourited listings
- `reports_count`: Number of reports submitted

**Landlord statistics:**
- `total_listings`: Total number of listings created
- `published_listings`: Number of published listings (`status = 'published'`)
- `pending_review_listings`: Number of listings pending review (`status = 'pending_review'`)
- `archived_listings`: Number of archived listings (`status = 'archived'`)

**Admin statistics:**
- `total_users`: Total number of users on the platform
- `total_listings`: Total number of listings on the platform
- `pending_review_listings`: Number of listings pending review
- `pending_reports`: Number of pending reports

### Side Effects / Data Changes

No side effects; this is a read-only endpoint.