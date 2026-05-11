# Property API

Base URL:

`/api/v1/property/`

---

## Browse Listings

`GET /api/v1/property/list/`

### Description

Retrieves a list of all `published` property listings.

### Authentication

No authentication required.

### Request Body

No request body.

### Success Response

Status: `200 OK`

```json
[
  {
    "id": "uuid",
    "title": "Cosy private room in Fitzroy",
    "location": {
      "city": "Melbourne",
      "administrative_area": "VIC",
      "suburb": "Fitzroy"
    },
    "price": 350.00,
    "room_type": "private_room",
    "is_pet_friendly": true,
    "cover_image": "https://cdn.example.com/images/xxx.jpg",
    "updated_at": "2026-05-08T12:00:00Z"
  },
  {
    "id": "uuid",
    "title": "Master bedroom near Central Station",
    "location": {
      "city": "Sydney",
      "administrative_area": "NSW",
      "suburb": "Chippendale"
    },
    "price": 420.00,
    "room_type": "entire_place",
    "is_pet_friendly": false,
    "cover_image": "https://cdn.example.com/images/yyy.jpg",
    "updated_at": "2026-05-07T10:00:00Z"
  }
]
```

### Error Responses

Status: `500 Internal Server Error`

```json
{
  "detail": "An internal server error occurred."
}
```

### Business Rules

- Only returns listings with `status = "published"`
- Listings with status `draft` / `pending_review` / `rejected` / `archived` are not returned
- Results are sorted by creation time in descending order (newest first)
- If no published listings exist, returns an empty array `[]`

### Side Effects / Data Changes

- No side effects; this is a read-only endpoint.

---

## Search and Filter Listings

`GET /api/v1/property/list/`

### Description

Search and filter published listings. Supports keyword matching, location filters, price range, and pet-friendly filter. All filters can be used together.

### Authentication

No authentication required.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | No | Keywords. Matches title, location (city/suburb), and description. |
| `city` | string | No | Filter by city (e.g., Sydney, Melbourne, Brisbane). |
| `administrative_area` | string | No | Filter by state (e.g., NSW, VIC, QLD). |
| `min_price` | decimal | No | Minimum price (AUD). |
| `max_price` | decimal | No | Maximum price (AUD). |
| `is_pet_friendly` | boolean | No | Pet-friendly filter. Options: `true`, `false`. |

### Request Body

No request body.

### Success Response

Status: `200 OK`

```json
[
  {
    "id": "uuid",
    "title": "Cosy private room in Fitzroy",
    "description": "Close to tram stop, convenient transport, shops nearby",
    "location": {
      "city": "Melbourne",
      "administrative_area": "VIC",
      "suburb": "Fitzroy"
    },
    "price": 350.00,
    "room_type": "private_room",
    "is_pet_friendly": true,
    "cover_image": "https://cdn.example.com/images/xxx.jpg",
    "updated_at": "2026-05-08T12:00:00Z"
  }
]
```

### Example Requests

- Example 1: Keyword search  
`GET /api/v1/property/list/?search=Fitzroy`

- Example 2: City + price range  
`GET /api/v1/property/list/?city=Sydney&min_price=300&max_price=500`

- Example 3: Combined filters (pet-friendly + state)  
`GET /api/v1/property/list/?administrative_area=VIC&is_pet_friendly=true`

- Example 4: Keyword + price range + pet-friendly  
`GET /api/v1/property/list/?search=tram&min_price=250&max_price=400&is_pet_friendly=true`

### Error Responses

Status: `400 Bad Request`  
Invalid parameter format (e.g., `min_price` is not a number).

```json
{
  "detail": "Invalid query parameters."
}
```

Status: `500 Internal Server Error`

```json
{
  "detail": "An internal server error occurred."
}
```

### Business Rules

- Only returns listings with `status = "published"`
- Keyword `search` matches: `title`, `city`, `administrative_area` (state), `suburb`, `description`
- `search` uses partial (fuzzy) matching
- `min_price` and `max_price` can be used individually (e.g., `min_price=300` means price ≥ 300)
- If both are provided and `min_price > max_price`, returns an empty result (or an error)
- All filters can be combined
- If no results match, returns an empty array `[]`
- If `is_pet_friendly` is omitted, no filter is applied. `true` shows only pet-friendly, `false` shows only non-pet-friendly

### Side Effects / Data Changes

No side effects; this is a read-only endpoint.

---

## View Listing Details

`GET /api/v1/property/list/{id}/`

### Description

Get detailed information for a single property by its ID. Only listings with `status = "published"` are visible to general users.

### Authentication

No authentication required.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing. |

### Request Body

No request body.

### Success Response

Status: `200 OK`

```json
{
  "id": "uuid",
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
  "description": "North-facing room with good natural light, close to tram stop, supermarket and restaurants nearby...",
  "images": [
    "https://cdn.example.com/images/xxx.jpg",
    "https://cdn.example.com/images/yyy.jpg",
    "https://cdn.example.com/images/zzz.jpg"
  ],
  "landlord": {
    "id": "uuid",
    "display_name": "John Smith",
    "avatar": "https://cdn.example.com/avatars/xxx.jpg",
    "phone_number": "0412 345 678"
  },
  "created_at": "2026-05-08T12:00:00Z",
  "updated_at": "2026-05-10T15:30:00Z"
}
```

### Error Responses

Status: `404 Not Found`  
Listing does not exist or is not published (not visible to general users).

Status: `500 Internal Server Error`

```json
{
  "detail": "An internal server error occurred."
}
```

### Side Effects / Data Changes

No side effects; this is a read-only endpoint.

---

## Save Listing

`POST /api/v1/property/save/`

### Description

Save (favourite) a listing. Only logged-in tenant users can save listings.

### Authentication

Authentication required.

Role: `tenant`

### Request Body

```json
{
  "listing_id": "uuid"
}
```

### Success Response

Status: `201 Created`

No response body.

### Error Responses

Status: `401 Unauthorized`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Status: `403 Forbidden`  
Logged in but role is not tenant (e.g., landlord trying to save).

```json
{
  "detail": "Only tenant users can save listings."
}
```

Status: `400 Bad Request`  
Request body missing `listing_id`.

```json
{
  "listing_id": ["This field is required."]
}
```

Status: `409 Conflict`  
Listing already saved (duplicate).

```json
{
  "detail": "You have already saved this listing."
}
```

Status: `404 Not Found`  
Listing does not exist.

```json
{
  "detail": "Listing not found."
}
```

### Business Rules

- Only users with `role = "tenant"` can save listings
- A user cannot save the same listing more than once (`user_id` + `listing_id` unique)
- No sensitive information should be returned in the response
- If the listing is deleted or does not exist, return 404

### Side Effects / Data Changes

Creates a record in the `saved_listings` table.

---

## Unsave Listing

`DELETE /api/v1/saved-listings/{id}/`

### Description

Remove a saved listing (unfavourite). Only logged-in tenant users can unsave their own saved listings.

### Authentication

Authentication required.

Role: `tenant`

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the saved listing record. |

### Request Body

No request body.

### Success Response

Status: `204 No Content`

No response body.

### Error Responses

Status: `401 Unauthorized`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Status: `403 Forbidden`  
Attempting to delete another user's saved listing.

```json
{
  "detail": "You do not have permission to perform this action."
}
```

Status: `404 Not Found`  
Saved listing record does not exist.

```json
{
  "detail": "Saved listing not found."
}
```

### Business Rules

- Users can only unsave their own saved listings
- After unsaving, no content should be returned (204)

### Side Effects / Data Changes

Deletes the corresponding record from the `saved_listings` table.

---

## List Saved Listings

`GET /api/v1/saved-listings/`

### Description

Get a list of all saved listings for the currently logged-in tenant user.

### Authentication

Authentication required.

Role: `tenant`

### Request Body

No request body.

### Success Response

Status: `200 OK`

```json
[
  {
    "id": "uuid",
    "created_at": "2026-05-10T12:00:00Z",
    "listing": {
      "id": "uuid",
      "title": "Cosy private room in Fitzroy",
      "location": {
        "city": "Melbourne",
        "administrative_area": "VIC",
        "suburb": "Fitzroy"
      },
      "price": 350.00,
      "room_type": "private_room",
      "is_pet_friendly": true,
      "cover_image": "https://cdn.example.com/images/xxx.jpg",
      "updated_at": "2026-05-08T12:00:00Z"
    }
  }
]
```

### Error Responses

Status: `401 Unauthorized`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Business Rules

- Only returns saved listings for the currently authenticated user
- If a saved listing is no longer `published` (e.g., delisted or deleted), it is **not** shown in the list
- Results are sorted by `created_at` in descending order (newest first)
- If no saved listings, returns an empty array `[]`

### Side Effects / Data Changes

No side effects; this is a read-only endpoint.