## Create Listing Report

`POST /api/v1/listings/{listing_id}/reports/`

### Description

Allow authenticated tenant users to report suspicious or misleading property listings for admin review.

### Authentication

Required.

Authentication method:

- JWT
- Secure HttpOnly Cookie
- CSRF protection required

### Path Parameters

| Parameter  | Type | Required | Description                      |
| ---------- | ---- | -------- | -------------------------------- |
| listing_id | uuid | Yes      | ID of the listing being reported |

### Request Body

```json
{
  "reason": "wrong_price",
  "description": "The listed rent looks much lower than similar properties in this area."
}
```

### Success Response

Status: `201 Created`

```json
{
  "id": "report_uuid",
  "listing_id": "listing_uuid",
  "reporter_id": "user_uuid",
  "reason": "wrong_price",
  "description": "The listed rent looks much lower than similar properties in this area.",
  "status": "pending",
  "reviewed_by_id": null,
  "reviewed_at": null,
  "admin_note": null,
  "created_at": "2026-05-09T17:40:00Z",
  "updated_at": "2026-05-09T17:40:00Z"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "description": ["Description is required when reason is other."]
}
```

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden

```json
{
  "detail": "Only tenant users can report listings."
}
```

#### 404 Not Found

```json
{
  "detail": "Listing not found."
}
```

#### 409 Conflict

```json
{
  "detail": "You already have a pending report for this listing."
}
```

### Business Rules

- Only authenticated tenant users can report listings
- Only published listings can be reported
- User cannot create duplicate pending reports for the same listing
- Users may submit another report after previous reports are resolved or dismissed
- `description` is required if `reason=other`
- Reports require admin review before moderation actions are taken
- Allowed report reasons:
  - `scam_suspected`
  - `fake_photos`
  - `wrong_price`
  - `unsafe_contact`
  - `other`

### Side Effects / Data Changes

- Create one record in `listing_reports`
- Set `listing_id` from path parameter
- Set `reporter_id` from authenticated user
- Set `status = pending`
- Set `created_at`
- Set `updated_at`

## Create Listing Report

`POST /api/v1/listings/{listing_id}/reports/`

### Description

Allow authenticated tenant users to report suspicious or misleading property listings for admin review.

### Authentication

Required.

Authentication method:

- JWT
- Secure HttpOnly Cookie
- CSRF protection required

### Path Parameters

| Parameter  | Type | Required | Description                      |
| ---------- | ---- | -------- | -------------------------------- |
| listing_id | uuid | Yes      | ID of the listing being reported |

### Request Body

```json
{
  "reason": "wrong_price",
  "description": "The listed rent looks much lower than similar properties in this area."
}
```

### Success Response

Status: `201 Created`

```json
{
  "id": "report_uuid",
  "listing_id": "listing_uuid",
  "reporter_id": "user_uuid",
  "reason": "wrong_price",
  "description": "The listed rent looks much lower than similar properties in this area.",
  "status": "pending",
  "reviewed_by_id": null,
  "reviewed_at": null,
  "admin_note": null,
  "created_at": "2026-05-09T17:40:00Z",
  "updated_at": "2026-05-09T17:40:00Z"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "description": ["Description is required when reason is other."]
}
```

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden

```json
{
  "detail": "Only tenant users can report listings."
}
```

#### 404 Not Found

```json
{
  "detail": "Listing not found."
}
```

#### 409 Conflict

```json
{
  "detail": "You already have a pending report for this listing."
}
```

### Business Rules

- Only authenticated tenant users can report listings
- Only published listings can be reported
- User cannot create duplicate pending reports for the same listing
- Users may submit another report after previous reports are resolved or dismissed
- `description` is required if `reason=other`
- Reports require admin review before moderation actions are taken
- Allowed report reasons:
  - `scam_suspected`
  - `fake_photos`
  - `wrong_price`
  - `unsafe_contact`
  - `other`

### Side Effects / Data Changes

- Create one record in `listing_reports`
- Set `listing_id` from path parameter
- Set `reporter_id` from authenticated user
- Set `status = pending`
- Set `created_at`
- Set `updated_at`
