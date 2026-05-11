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

## List Listing Reports

`GET /api/v1/admin/listing-reports/`

### Description

Allow admin users to view listing reports with filtering, searching, sorting, and pagination support.

### Authentication

Required.

Authentication method:

- JWT
- Secure HttpOnly Cookie
- CSRF protection required

### Authorization

Admin only.

### Query Parameters

| Parameter      | Type    | Required | Description                                                                   |
| -------------- | ------- | -------- | ----------------------------------------------------------------------------- |
| status         | string  | No       | Filter by report status: `pending`, `resolved`, `dismissed`                   |
| reason         | string  | No       | Filter by report reason                                                       |
| listing_id     | uuid    | No       | Filter reports for a specific listing                                         |
| reporter_id    | uuid    | No       | Filter reports submitted by a specific user                                   |
| reviewed_by_id | uuid    | No       | Filter reports reviewed by a specific admin                                   |
| search         | string  | No       | Search report description, admin note, or related listing title               |
| ordering       | string  | No       | Sort results, e.g. `created_at`, `-created_at`, `reviewed_at`, `-reviewed_at` |
| page           | integer | No       | Page number                                                                   |
| page_size      | integer | No       | Number of results per page                                                    |

### Success Response

Status: `200 OK`

```json
{
  "count": 120,
  "next": "/api/v1/admin/listing-reports/?page=2",
  "previous": null,
  "results": [
    {
      "id": "report_uuid",
      "listing_id": "listing_uuid",
      "listing_title": "Modern studio near UNSW",
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
  ]
}
```

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden

```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 400 Bad Request

```json
{
  "detail": "Invalid query parameter."
}
```

### Business Rules

- Only admin users can view listing reports
- Reports are returned using pagination
- Default ordering is newest first
- Filtering, searching, sorting, and pagination are handled by the backend
- Query parameters must be validated before applying filters
- Admin users can filter reports by:
  - report status
  - report reason
  - listing
  - reporter
  - reviewer
- Admin users can search:
  - report description
  - admin note
  - related listing title
- Pending reports should be easy to retrieve for moderation workflows
- Maximum page size may be restricted by the backend

### Side Effects / Data Changes

- No database records are created, updated, or deleted
- This is a read-only API
- Backend may log admin access activity for auditing and security monitoring
