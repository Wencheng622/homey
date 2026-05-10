# Landlord API

Base URL:

`/api/v1/landlord/`

---

## Create Listing Draft

`POST /api/v1/landlord/listings/`

### Description

Landlord creates a listing draft. The system automatically sets the status to `draft`. Drafts are not visible to regular users.

### Authentication

Authentication required.

Role: `landlord`

### Request Body

```json
{
  "title": "Cosy private room in Fitzroy",
  "description": "North-facing room with good natural light, close to tram stop, supermarket and restaurants nearby...",
  "price": 350.00,
  "country": "Australia",
  "administrative_area": "VIC",
  "city": "Melbourne",
  "suburb": "Fitzroy",
  "postcode": "3065",
  "street_address": "123 Brunswick Street",
  "latitude": -37.798,
  "longitude": 144.978,
  "room_type": "private_room",
  "property_type": "apartment",
  "is_pet_friendly": true
}
```

### Request Field Notes

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Listing title, max length 200 characters |
| `description` | string | No | Detailed description of the listing |
| `price` | decimal | Yes | Monthly rent (AUD), must be greater than 0 |
| `country` | string | Yes | Country |
| `administrative_area` | string | No | State (e.g., NSW, VIC, QLD) |
| `city` | string | Yes | City |
| `suburb` | string | No | Suburb or district |
| `postcode` | string | No | Postcode (e.g., 2000, 3065) |
| `street_address` | string | No | Detailed street address |
| `latitude` | decimal | No | Latitude (-90 to 90) |
| `longitude` | decimal | No | Longitude (-180 to 180) |
| `room_type` | string | Yes | Room type: `entire_place` / `private_room` / `shared_room` |
| `property_type` | string | Yes | Property type: `apartment` / `house` / `townhouse` / `condo` / `studio` / `other` |
| `is_pet_friendly` | boolean | No | Whether pets are allowed, defaults to `false` |

### Success Response

Status: `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "landlord_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "title": "Cosy private room in Fitzroy",
  "description": "North-facing room with good natural light, close to tram stop, supermarket and restaurants nearby...",
  "price": 350.00,
  "country": "Australia",
  "administrative_area": "VIC",
  "city": "Melbourne",
  "suburb": "Fitzroy",
  "postcode": "3065",
  "street_address": "123 Brunswick Street",
  "latitude": -37.798,
  "longitude": 144.978,
  "room_type": "private_room",
  "property_type": "apartment",
  "is_pet_friendly": true,
  "status": "draft",
  "created_at": "2026-05-10T12:00:00Z",
  "updated_at": "2026-05-10T12:00:00Z"
}
```

### Error Responses

Status: `401 Unauthorized`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Status: `403 Forbidden`  
Logged in but role is not landlord.

```json
{
  "detail": "Only landlord users can create listings."
}
```

Status: `400 Bad Request`  
Request data validation failed.

```json
{
  "title": ["This field is required."],
  "price": ["Price must be greater than 0."],
  "room_type": ["Must be one of: entire_place, private_room, shared_room."]
}
```

### Business Rules

- Only users with `role = "landlord"` can create listings
- Newly created listings automatically have `status = "draft"`
- All optional fields can be omitted; the system uses defaults or `null`
- Draft listings **do not appear** in public browse/search endpoints
- Landlords can update drafts multiple times
- If latitude/longitude are provided, they must be valid
- Price must be greater than 0

### Side Effects / Data Changes

- Creates a record in `property_listings` table with `status = "draft"`
- `landlord_id` is automatically associated with the currently logged-in landlord user
- Automatically generates `created_at` and `updated_at` timestamps

---

## Edit Listing

`PATCH /api/v1/landlord/listings/{id}/`

### Description

Landlord edits their own listing. Supports partial updates (only send fields that need to be changed). Status handling after editing depends on the current listing status.

### Authentication

Authentication required.

Role: `landlord`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing |

### Request Body

```json
{
  "title": "Spacious master bedroom in Fitzroy (updated)",
  "description": "North-facing master bedroom, great natural light, close to tram stop...",
  "price": 380.00,
  "country": "Australia",
  "administrative_area": "VIC",
  "city": "Melbourne",
  "suburb": "Fitzroy",
  "postcode": "3065",
  "street_address": "123 Brunswick Street",
  "latitude": -37.798,
  "longitude": 144.978,
  "room_type": "private_room",
  "property_type": "apartment",
  "is_pet_friendly": false
}
```

### Request Field Notes

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Any field | Any | No | Only send fields that need to be updated; omitted fields remain unchanged |

Supported fields are the same as the Create endpoint:
- `title`
- `description`
- `price`
- `country`
- `administrative_area`
- `city`
- `suburb`
- `postcode`
- `street_address`
- `latitude`
- `longitude`
- `room_type`
- `property_type`
- `is_pet_friendly`

### Success Response

Status: `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "landlord_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "title": "Spacious master bedroom in Fitzroy (updated)",
  "description": "North-facing master bedroom, great natural light, close to tram stop...",
  "price": 380.00,
  "country": "Australia",
  "administrative_area": "VIC",
  "city": "Melbourne",
  "suburb": "Fitzroy",
  "postcode": "3065",
  "street_address": "123 Brunswick Street",
  "latitude": -37.798,
  "longitude": 144.978,
  "room_type": "private_room",
  "property_type": "apartment",
  "is_pet_friendly": false,
  "status": "draft",
  "created_at": "2026-05-10T12:00:00Z",
  "updated_at": "2026-05-12T15:30:00Z"
}
```

### Error Responses

Status: `401 Unauthorized`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Status: `403 Forbidden`  
Logged in but role is not landlord.

```json
{
  "detail": "Only landlord users can edit listings."
}
```

Status: `403 Forbidden`  
Attempting to edit someone else's listing.

```json
{
  "detail": "You do not have permission to edit this listing."
}
```

Status: `403 Forbidden`  
Listing is in a non-editable state.

```json
{
  "detail": "Listings with status 'pending_review' cannot be edited."
}
```

Status: `404 Not Found`

```json
{
  "detail": "Listing not found."
}
```

Status: `400 Bad Request`  
Request data validation failed.

```json
{
  "price": ["Price must be greater than 0."],
  "latitude": ["Must be between -90 and 90."]
}
```

### Business Rules

- Only users with `role = "landlord"` can edit listings
- Landlords can **only edit their own listings** (`landlord_id` must match)
- Supports partial updates (PATCH) — only send fields to change
- Behaviour depends on current `status`:

| Original Status | Editable? | New Status |
|----------------|-----------|-------------|
| `draft` | ✅ Yes | Remains `draft` |
| `rejected` | ✅ Yes | Remains `rejected` |
| `published` | ✅ Yes | Remains `published` (takes effect immediately) |
| `pending_review` | ❌ No | - |
| `archived` | ❌ No | - |

- Published listings are **updated immediately** after editing; no re-review required (Phase 1)
- Price must be greater than 0
- If latitude/longitude are provided, they must be valid
- `updated_at` timestamp is automatically updated after successful update

### Side Effects / Data Changes

- Updates the corresponding record in the `property_listings` table
- Updates the `updated_at` timestamp

---

## Upload Media

`POST /api/v1/landlord/listings/{id}/upload-media/`

### Description

Landlord uploads one or more images/videos for a listing. Media files are associated with the listing for display.

**Cover Rule**: If the listing currently has no images, the first image uploaded in this request automatically becomes the cover (`is_cover = true`).

### Authentication

Authentication required.

Role: `landlord`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing |

### Request Body

Uses `multipart/form-data` format.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `media` | file[] | Yes | One or more media files |

**Supported file formats:**
- Images: `jpg`, `jpeg`, `png`, `webp` — max size **10MB** each
- Videos: `mp4`, `mov` — max size **100MB** each

### Example Request

```http
POST /api/v1/landlord/listings/550e8400-e29b-41d4-a716-446655440000/upload-media/
Content-Type: multipart/form-data

media: image1.jpg
media: image2.png
media: video1.mp4
```

### Success Response

Status: `200 OK`

```json
{
  "media": [
    {
      "id": "uuid",
      "media_type": "image",
      "url": "https://cdn.example.com/listings/xxx/image1.jpg",
      "thumbnail_url": "https://cdn.example.com/listings/xxx/image1_thumb.jpg",
      "is_cover": true,
      "order": 0,
      "created_at": "2026-05-12T10:00:00Z"
    },
    {
      "id": "uuid",
      "media_type": "image",
      "url": "https://cdn.example.com/listings/xxx/image2.jpg",
      "thumbnail_url": "https://cdn.example.com/listings/xxx/image2_thumb.jpg",
      "is_cover": false,
      "order": 1,
      "created_at": "2026-05-12T10:00:01Z"
    },
    {
      "id": "uuid",
      "media_type": "video",
      "url": "https://cdn.example.com/listings/xxx/video1.mp4",
      "thumbnail_url": null,
      "is_cover": false,
      "order": 2,
      "created_at": "2026-05-12T10:00:02Z"
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
Logged in but role is not landlord.

```json
{
  "detail": "Only landlord users can upload media."
}
```

#### 403 Forbidden  
Attempting to upload media for someone else's listing.

```json
{
  "detail": "You do not have permission to upload media for this listing."
}
```

#### 404 Not Found

```json
{
  "detail": "Listing not found."
}
```

#### 400 Bad Request  
No files uploaded.

```json
{
  "media": ["No files were uploaded."]
}
```

#### 400 Bad Request  
Unsupported file type.

```json
{
  "detail": "Unsupported file type: .gif. Allowed types: jpg, jpeg, png, webp (image), mp4, mov (video)."
}
```

#### 400 Bad Request  
File too large.

```json
{
  "detail": "File 'video.mp4' exceeds maximum size of 100MB."
}
```

#### 400 Bad Request  
Exceeds maximum media count limit.

```json
{
  "detail": "Maximum 20 media files per listing. Current: 18, Uploading: 3"
}
```

### Business Rules

- Only users with `role = "landlord"` can upload media
- Landlords can **only upload media for their own listings**
- Supported formats:
  - Images: `jpg`, `jpeg`, `png`, `webp`
  - Videos: `mp4`, `mov`
- File size limits:
  - Images: **10MB**
  - Videos: **100MB**
- Maximum media per listing: **20** (total images + videos)
- **Cover rules**:
  - Only when the listing has **no images at all**, the first image in this upload becomes the cover (`is_cover = true`)
  - Once a listing already has a cover image, subsequently uploaded images will not change the cover
  - Videos **never** become the cover (even if the listing has no images)
  - Landlords can delete the current cover image to allow the next image to auto-become the new cover
- After successful upload, the system automatically generates:
  - Original file URL
  - Image thumbnail URL (videos return `null`)
- Media are arranged in upload order (`sort_order` field increments from 0)

### Side Effects / Data Changes

- Stores media files in cloud storage (e.g., OSS, S3)
- Generates `storage_key`: `listings/{listing_id}/{timestamp}_{filename}`
- Creates records in `listing_media` table
  - `media_type`: `image` or `video`
  - `storage_bucket`: bucket name
  - `storage_key`: unique object key
  - `is_cover`: automatically set based on cover rules
  - `sort_order`: current max order + 1
- Generates and stores thumbnails for images
- Thumbnails for videos return `null` in Phase 1

---

## Get Listing Media

`GET /api/v1/landlord/listings/{id}/media/`

### Description

Retrieves all media files (images and videos) for a specified listing.

### Authentication

Authentication required.

Role: `landlord`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing |

### Query Parameters (optional)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `media_type` | string | No | Filter by media type: `image` or `video`. If omitted, returns all. |

### Request Body

No request body.

### Success Response

Status: `200 OK`

```json
{
  "media": [
    {
      "id": "uuid",
      "media_type": "image",
      "url": "https://cdn.example.com/listings/xxx/image1.jpg",
      "thumbnail_url": "https://cdn.example.com/listings/xxx/image1_thumb.jpg",
      "is_cover": true,
      "order": 0,
      "created_at": "2026-05-12T10:00:00Z"
    },
    {
      "id": "uuid",
      "media_type": "image",
      "url": "https://cdn.example.com/listings/xxx/image2.jpg",
      "thumbnail_url": "https://cdn.example.com/listings/xxx/image2_thumb.jpg",
      "is_cover": false,
      "order": 1,
      "created_at": "2026-05-12T10:00:01Z"
    },
    {
      "id": "uuid",
      "media_type": "video",
      "url": "https://cdn.example.com/listings/xxx/video1.mp4",
      "thumbnail_url": null,
      "is_cover": false,
      "order": 2,
      "created_at": "2026-05-12T10:00:02Z"
    }
  ]
}
```

### Filter Examples

**Get only images:**
```
GET /api/v1/landlord/listings/{id}/media/?media_type=image
```

**Get only videos:**
```
GET /api/v1/landlord/listings/{id}/media/?media_type=video
```

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden  
Logged in but role is not landlord.

```json
{
  "detail": "Only landlord users can view media."
}
```

#### 403 Forbidden  
Attempting to view media for someone else's listing.

```json
{
  "detail": "You do not have permission to view media for this listing."
}
```

#### 404 Not Found

```json
{
  "detail": "Listing not found."
}
```

#### 400 Bad Request  
Invalid `media_type` parameter value.

```json
{
  "detail": "Invalid media_type. Must be 'image' or 'video'."
}
```

### Business Rules

- Landlords can **only view media for their own listings**
- Media is sorted by `sort_order` in ascending order
- If no media exists, returns an empty array `[]`
- `media_type` filter is optional, used for frontend type-based display
- Video `thumbnail_url` returns `null` in Phase 1 (thumbnails not implemented yet)

### Side Effects / Data Changes

No side effects; this is a read-only endpoint.

---

## Delete Media

`DELETE /api/v1/landlord/listings/{id}/media/{media_id}/`

### Description

Deletes a media file (image or video) from a listing. If the deleted file is the cover image, the remaining image with the smallest `sort_order` automatically becomes the new cover.

### Authentication

Authentication required.

Role: `landlord`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing |
| `media_id` | string(uuid) | Yes | Unique identifier of the media file |

### Request Body

No request body.

### Success Response

Status: `204 No Content`

No response body.

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden  
Logged in but role is not landlord.

```json
{
  "detail": "Only landlord users can delete media."
}
```

#### 403 Forbidden  
Attempting to delete media from someone else's listing.

```json
{
  "detail": "You do not have permission to delete this media."
}
```

#### 404 Not Found  
Listing or media file not found.

```json
{
  "detail": "Media not found."
}
```

#### 400 Bad Request  
Attempting to delete a video (if not supported in Phase 1).

```json
{
  "detail": "Deleting videos is not supported in Phase 1."
}
```

### Business Rules

- Landlords can **only delete media from their own listings**
- **Cover handling rules**:
  - If the deleted file is **not** the cover → file is removed, cover remains unchanged
  - If the deleted file **is** the cover:
    - If **other images remain** → the image with the smallest `sort_order` becomes the new cover
    - If **no images remain** → the listing has no cover (all `is_cover` fields become `false`)
  - Deleting a video **never affects the cover** (videos can never be covers)
- After deletion, the `sort_order` of remaining media is automatically renumbered (0, 1, 2, ... consecutively)
- Physical files can be deleted immediately or asynchronously (asynchronous deletion recommended — delete database record first)

### Side Effects / Data Changes

- Deletes the media record from the `listing_media` table
- Deletes the original file from cloud storage (image/video)
- When deleting an image, also deletes its thumbnail
- If the cover is deleted, automatically executes cover transfer logic
- Renumbers `sort_order` for remaining media (0, 1, 2...)

---

## Submit Listing for Review

`POST /api/v1/landlord/listings/{id}/submit-review/`

### Description

Landlord submits a draft listing for review. After submission, the listing status changes from `draft` to `pending_review`.

### Authentication

Authentication required.

Role: `landlord`

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
  "status": "pending_review",
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
Logged in but role is not landlord.

```json
{
  "detail": "Only landlord users can submit listings for review."
}
```

#### 403 Forbidden  
Attempting to submit someone else's listing.

```json
{
  "detail": "You do not have permission to submit this listing."
}
```

#### 404 Not Found

```json
{
  "detail": "Listing not found."
}
```

#### 409 Conflict  
Listing status is not `draft`.

```json
{
  "detail": "Only draft listings can be submitted for review. Current status: published"
}
```

### Business Rules

- Only users with `role = "landlord"` can submit for review
- Landlords can **only submit their own listings**
- Only listings with `status = "draft"` can be submitted for review
- After successful submission, status changes to `pending_review`
- Phase 1 does not validate required fields (left to frontend or later review process)

### Side Effects / Data Changes

- Updates `property_listings.status` to `pending_review`
- Updates `property_listings.updated_at` timestamp

---

## Archive Listing

`POST /api/v1/landlord/listings/{id}/archive/`

### Description

Landlord archives their own published listing. After archiving, the listing status changes from `published` to `archived`, and the listing is no longer visible to regular users.

### Authentication

Authentication required.

Role: `landlord`

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
  "status": "archived",
  "updated_at": "2026-05-13T14:30:00Z"
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
Logged in but role is not landlord.

```json
{
  "detail": "Only landlord users can archive listings."
}
```

#### 403 Forbidden  
Attempting to archive someone else's listing.

```json
{
  "detail": "You do not have permission to archive this listing."
}
```

#### 404 Not Found

```json
{
  "detail": "Listing not found."
}
```

#### 409 Conflict  
Listing status is not `published`.

```json
{
  "detail": "Only published listings can be archived. Current status: draft"
}
```

#### 409 Conflict  
Listing is already archived.

```json
{
  "detail": "Listing is already archived."
}
```

### Business Rules

- Only users with `role = "landlord"` can archive listings
- Landlords can **only archive their own listings**
- Only listings with `status = "published"` can be archived
- After archiving, status changes to `archived`
- Archived listings:
  - **Not visible** to regular users
  - Will not appear in public browse/search endpoints
  - Will not be visible even to tenants who have previously saved them (per Story 3 acceptance criteria)
- Archiving automatically records an `archived_at` timestamp (optional)
- Phase 1 does not support restoring from `archived` to `published` (can be extended later)
- Draft listings can be directly deleted (no archive flow needed)

### Side Effects / Data Changes

- Updates `property_listings.status` to `archived`
- Updates `property_listings.updated_at`
- Optional: records `archived_at` timestamp
- Optional: removes the listing from search engines/cache

---

## Delete Draft Listing

`DELETE /api/v1/landlord/listings/{id}/`

### Description

Landlord permanently deletes their own draft listing. Only listings with `draft` status can be deleted.

### Authentication

Authentication required.

Role: `landlord`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string(uuid) | Yes | Unique identifier of the listing |

### Request Body

No request body.

### Success Response

Status: `204 No Content`

No response body.

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden  
Logged in but role is not landlord.

```json
{
  "detail": "Only landlord users can delete listings."
}
```

#### 403 Forbidden  
Attempting to delete someone else's listing.

```json
{
  "detail": "You do not have permission to delete this listing."
}
```

#### 404 Not Found

```json
{
  "detail": "Listing not found."
}
```

#### 409 Conflict  
Listing status is not `draft`.

```json
{
  "detail": "Only draft listings can be deleted. Current status: published. Use archive instead."
}
```

### Business Rules

- Only users with `role = "landlord"` can delete listings
- Landlords can **only delete their own listings**
- Only listings with `status = "draft"` can be permanently deleted
- Published listings should be **archived** instead of deleted
- Deletion **physically removes** the database record (or soft deletes, depending on implementation strategy)
- Associated media files should also be handled on deletion

### Side Effects / Data Changes

- Deletes the record from the `property_listings` table
- Optional: deletes associated `listing_media` records
- Optional: deletes associated media files from cloud storage