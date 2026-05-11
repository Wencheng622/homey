# Admin API

Base URL:

`/api/v1/admin/`

---

## List Listings for Review

`GET /api/v1/admin/listings/`

### Description

Admin retrieves a list of listings, with optional filtering by status. By default, shows listings with `pending_review` status.

### Authentication

Authentication required.

Role: `admin`

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status. Options: `pending_review`, `published`, `rejected`, `archived`. Defaults to `pending_review` if not provided. |
| `page` | integer | No | Page number, defaults to 1 |
| `page_size` | integer | No | Number of items per page, defaults to 20, maximum 100 |

### Request Body

No request body.

### Success Response

Status: `200 OK`

```json
{
  "count": 5,
  "next": "http://api.example.com/api/v1/admin/listings/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "landlord_id": "uuid",
      "landlord_name": "John Smith",
      "landlord_email": "landlord@example.com",
      "title": "Cosy private room in Fitzroy",
      "price": 350.00,
      "location": {
        "city": "Melbourne",
        "administrative_area": "VIC",
        "suburb": "Fitzroy"
      },
      "room_type": "private_room",
      "property_type": "apartment",
      "is_pet_friendly": true,
      "description": "North-facing room with good natural light...",
      "images": [
        "https://cdn.example.com/images/xxx.jpg"
      ],
      "status": "pending_review",
      "submitted_at": "2026-05-12T14:30:00Z",
      "created_at": "2026-05-10T12:00:00Z",
      "updated_at": "2026-05-12T14:30:00Z"
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

Logged in but role is not admin.

```json
{
  "detail": "Only admin users can access this endpoint."
}
```

### Business Rules

- Only users with `role = "admin"` can access
- If `status` parameter is not provided, returns listings with `pending_review` status by default
- Supports pagination. Results are sorted by `submitted_at` or `created_at` in descending order (newest first)
- Response should include basic landlord information (name, email) for admin contact purposes

### Side Effects / Data Changes

No side effects; this is a read-only endpoint.

---

## Get Listing Details for Review

`GET /api/v1/admin/listings/{id}/`

### Description

Admin retrieves detailed information for a single listing for review purposes.

### Authentication

Authentication required.

Role: `admin`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing |

### Request Body

No request body.

### Success Response

Status: `200 OK`

```json
{
  "id": "uuid",
  "landlord_id": "uuid",
  "landlord": {
    "display_name": "John Smith",
    "email": "landlord@example.com",
    "avatar": "https://cdn.example.com/avatars/xxx.jpg",
    "phone": "0412****34"
  },
  "title": "Cosy private room in Fitzroy",
  "price": 350.00,
  "location": {
    "country": "Australia",
    "administrative_area": "VIC",
    "city": "Melbourne",
    "suburb": "Fitzroy",
    "postcode": "3065",
    "street_address": "123 Brunswick Street",
    "latitude": -37.798,
    "longitude": 144.978
  },
  "room_type": "private_room",
  "property_type": "apartment",
  "is_pet_friendly": true,
  "description": "North-facing room with good natural light, close to tram stop...",
  "bedrooms": {
    "count": 1,
    "area_sqm": 20.5,
    "beds": 1,
    "bed_size": "double"
  },
  "bathrooms": {
    "type": "shared",
    "count": 1
  },
  "indoor_amenities": ["wifi", "ac", "heating", "washer", "kitchen"],
  "roommate_preference": "no_preference",
  "lease": {
    "min_term_months": 6,
    "available_from": "2026-06-01"
  },
  "nearby_amenities": ["supermarket", "train_station", "cafe"],
  "images": [
    {
      "id": "uuid",
      "url": "https://cdn.example.com/images/xxx.jpg",
      "thumbnail_url": "https://cdn.example.com/images/xxx_thumb.jpg"
    }
  ],
  "status": "pending_review",
  "submitted_at": "2026-05-12T14:30:00Z",
  "created_at": "2026-05-10T12:00:00Z",
  "updated_at": "2026-05-12T14:30:00Z"
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

Logged in but role is not admin.

```json
{
  "detail": "Only admin users can access this endpoint."
}
```

#### 404 Not Found

Listing does not exist.

```json
{
  "detail": "Listing not found."
}
```

### Business Rules

- Only admin users can access
- Returns complete listing information, including landlord contact details
- Landlord phone number should be masked (e.g., `0412****34`)

### Side Effects / Data Changes

No side effects; this is a read-only endpoint.

---

## Approve Listing

`POST /api/v1/admin/listings/{id}/approve/`

### Description

Admin approves a pending listing. After approval, the listing status changes from `pending_review` to `published`, and the listing becomes visible to regular users.

### Authentication

Authentication required.

Role: `admin`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing |

### Request Body

```json
{
  "note": "Listing approved. Complete information provided."
}
```

### Success Response

Status: `200 OK`

```json
{
  "id": "uuid",
  "status": "published",
  "reviewed_by": "uuid",
  "reviewed_at": "2026-05-13T10:00:00Z",
  "detail": "Listing has been approved and published."
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

Logged in but role is not admin.

```json
{
  "detail": "Only admin users can approve listings."
}
```

#### 404 Not Found

Listing does not exist.

```json
{
  "detail": "Listing not found."
}
```

#### 409 Conflict

Listing status is not `pending_review`.

```json
{
  "detail": "Only pending_review listings can be approved. Current status: draft"
}
```

### Business Rules

- Only admin users can approve listings
- Only listings with `status = "pending_review"` can be approved
- After approval, status changes to `published`
- Approved listings become visible to regular users
- Optional note can be provided (stored but not shown to users)
- After approval, automatically records `reviewed_by` (reviewer ID) and `reviewed_at` (timestamp)

### Side Effects / Data Changes

- Updates `property_listings.status` to `published`
- Updates `property_listings.updated_at`
- Optionally records `reviewed_by` and `reviewed_at`
- Optionally sends notification to the landlord (listing approved)

---

## Reject Listing

`POST /api/v1/admin/listings/{id}/reject/`

### Description

Admin rejects a pending listing. After rejection, the listing status changes from `pending_review` to `rejected`. The listing is not visible to the public, and the landlord can modify and resubmit it.

### Authentication

Authentication required.

Role: `admin`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing |

### Request Body

```json
{
  "reason": "Photos are blurry. Please upload clear images of the property."
}
```

### Success Response

Status: `200 OK`

```json
{
  "id": "uuid",
  "status": "rejected",
  "reviewed_by": "uuid",
  "reviewed_at": "2026-05-13T10:30:00Z",
  "rejection_reason": "Photos are blurry. Please upload clear images of the property.",
  "detail": "Listing has been rejected."
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

Logged in but role is not admin.

```json
{
  "detail": "Only admin users can reject listings."
}
```

#### 404 Not Found

Listing does not exist.

```json
{
  "detail": "Listing not found."
}
```

#### 409 Conflict

Listing status is not `pending_review`.

```json
{
  "detail": "Only pending_review listings can be rejected. Current status: published"
}
```

#### 400 Bad Request

Rejection reason is missing.

```json
{
  "reason": ["A rejection reason is required."]
}
```

### Business Rules

- Only admin users can reject listings
- Only listings with `status = "pending_review"` can be rejected
- After rejection, status changes to `rejected`
- `reason` (rejection reason) is required so the landlord understands the issue and can make corrections
- Rejected listings are not visible to regular users
- Landlord can modify the rejected listing and resubmit for review
- After rejection, automatically records `reviewed_by`, `reviewed_at`, and `rejection_reason`

### Side Effects / Data Changes

- Updates `property_listings.status` to `rejected`
- Updates `property_listings.updated_at`
- Optionally records `reviewed_by`, `reviewed_at`, `rejection_reason`
- Optionally sends notification to the landlord (with rejection reason attached)