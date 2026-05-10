# Property API

Base URL:

`/api/v1/property/`

---

## Browse Listings

`GET /api/v1/property/list/`

### Description

获取所有状态为 `published`（已发布）的房源列表。

### Authentication

不需要认证。

### Request Body

无请求体。

### Success Response

Status: `200 OK`

```json
[
  {
    "id": "uuid",
    "title": "朝阳区温馨单间",
    "location": {
      "city": "北京",
      "administrative_area": "朝阳区",
      "suburb": "三里屯"
    },
    "price": 3500.00,
    "room_type": "private_room",
    "is_pet_friendly": true,
    "cover_image": "https://cdn.example.com/images/xxx.jpg",
    "updated_at": "2026-05-08T12:00:00Z"
  },
  {
    "id": "uuid",
    "title": "浦东新区地铁口主卧",
    "location": {
      "city": "上海",
      "administrative_area": "浦东新区",
      "suburb": "世纪大道"
    },
    "price": 4200.00,
    "room_type": "entire_place",
    "is_pet_friendly": false,
    "cover_image": "https://cdn.example.com/images/yyy.jpg",
    "updated_at": "2026-05-07T10:00:00Z"
  }
]
```

### Error Responses
Status: `500 Internal Server Error`

服务器内部错误
```json
{
  "detail": "An internal server error occurred."
}
```

### Business Rules

- 只返回 status = "published" 的房源
- 状态为 draft / pending_review / rejected / archived 的房源不返回
- 返回结果按创建时间倒序排列（最新的在前）
- 如果没有已发布的房源，返回空数组 []

### Side Effects / Data Changes

- 无副作用，此为只读接口。


## Search and Filter Listings

`GET /api/v1/property/list/`

### Description

搜索和筛选已发布的房源。支持关键词匹配、位置筛选、价格区间筛选、宠物友好筛选，所有筛选条件可以组合使用。

### Authentication

不需要认证。

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `search` | string | 否 | 关键词，匹配标题、位置（城市/区域）、描述 |
| `city` | string | 否 | 按城市筛选 |
| `administrative_area` | string | 否 | 按行政区/区域筛选（如：朝阳区、浦东新区） |
| `min_price` | decimal | 否 | 最低价格 |
| `max_price` | decimal | 否 | 最高价格 |
| `is_pet_friendly` | boolean | 否 | 宠物友好，可选值：`true`、`false` |

### Request Body

无请求体。

### Success Response

Status: `200 OK`

```json
[
  {
    "id": "uuid",
    "title": "朝阳区温馨单间",
    "description": "靠近地铁站，交通便利，周边配套齐全",
    "location": {
      "city": "北京",
      "administrative_area": "朝阳区",
      "suburb": "三里屯"
    },
    "price": 3500.00,
    "room_type": "private_room",
    "is_pet_friendly": true,
    "cover_image": "https://cdn.example.com/images/xxx.jpg",
    "updated_at": "2026-05-08T12:00:00Z"
  }
]
```

### Example Requests

- 示例 1：关键词搜索
GET /api/v1/property/list/?search=三里屯

- 示例 2：按城市 + 价格范围筛选
GET /api/v1/property/list/?city=北京&min_price=3000&max_price=5000

- 示例 3：复合筛选（宠物友好 + 区域）
GET /api/v1/property/list/?administrative_area=朝阳区&is_pet_friendly=true

- 示例 4：关键词 + 价格范围 + 宠物友好
GET /api/v1/property/list/?search=地铁&min_price=2000&max_price=4000&is_pet_friendly=true

### Error Responses
Status: `400 Bad Request`
参数格式错误（如：min_price 不是数字）。
```json
{
  "detail": "Invalid query parameters."
}
```
Status: `500 Internal Server Error`
服务器内部错误。
```json
{
  "detail": "An internal server error occurred."
}
```

### Business Rules
- 只返回 status = "published" 的房源
- 关键词搜索 search 同时匹配：title（标题）、city（城市）、administrative_area（行政区）、suburb（街道/区域）、description（描述）
- search 为模糊匹配（部分匹配即可）
- min_price 和 max_price 可以只传其中一个（例如只传 min_price=3000 表示价格 ≥ 3000）
- 如果同时传了 min_price 和 max_price，且 min_price > max_price，返回空结果或报错
- 所有筛选条件可以任意组合（全部可选）
- 如果没有匹配结果，返回空数组 []
- is_pet_friendly 不传时表示不过滤，传 true 只显示宠物友好，传 false 只显示非宠物友好

### Side Effects / Data Changes
无副作用，此为只读接口。

## View Listing Details

`GET /api/v1/property/list/{id}/`

### Description

根据房源 ID 获取单个房源的详细信息。只有状态为 `published`（已发布）的房源对普通用户可见。

### Authentication

不需要认证。

### Path Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | string(uuid) | 是 | 房源的唯一标识符 |

### Request Body

无请求体。

### Success Response

Status: `200 OK`

```json
{
  "id": "uuid",
  "title": "朝阳区温馨单间",
  "price": 3500.00,
  "location": {
    "country": "中国",
    "administrative_area": "北京市",
    "city": "北京",
    "suburb": "朝阳区",
    "postcode": "100020",
    "street_address": "三里屯路xx号",
    "latitude": 39.935,
    "longitude": 116.455
  },
  "room_type": "private_room",
  "property_type": "apartment",
  "is_pet_friendly": true,
  "description": "房间朝南，采光好，靠近地铁站，周边有超市和餐厅...",
  "images": [
    "https://cdn.example.com/images/xxx.jpg",
    "https://cdn.example.com/images/yyy.jpg",
    "https://cdn.example.com/images/zzz.jpg"
  ],
  "landlord": {
    "id": "uuid",
    "display_name": "张房东",
    "avatar": "https://cdn.example.com/avatars/xxx.jpg",
    "phone_number": "1234567" 
  },
  "created_at": "2026-05-08T12:00:00Z",
  "updated_at": "2026-05-10T15:30:00Z"
}
```

### Error Responses
Status: `404 Not Found`

房源不存在，或房源未发布（对普通用户不可见）。

Status: `500 Internal Server Error`

服务器内部错误。

```json
{
  "detail": "An internal server error occurred."
}
```

### Side Effects / Data Changes
无副作用，此为只读接口。

## Save Listing

`POST /api/v1/property/save/`

### Description

收藏一个房源。只有已登录的租客用户可以收藏。

### Authentication

需要认证。

角色：`tenant`（租客）

### Request Body

```json
{
  "listing_id": "uuid"
}
```

### Success Response
Status: `Status: 201 Created`

无响应体。

### Error Responses
Status: `401 Unauthorized`

未登录。

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Status: `403 Forbidden`

已登录但角色不是租客（例如房东尝试收藏）。
```json
{
  "detail": "Only tenant users can save listings."
}
```

Status: `400 Bad Request`

请求体缺少 listing_id或user_id。
```json
{
  "listing_id": ["This field is required."]
}
```

Status: `409 Conflict`

已经收藏过该房源（重复收藏）。
```json
{
  "detail": "You have already saved this listing."
}
```

Status: `404 Not Found`

房源不存在。
```json
{
  "detail": "Listing not found."
}
```

### Business Rules
- 只有 role = "tenant" 的用户可以收藏
- 一个用户不能重复收藏同一个房源（user_id + listing_id 唯一）
- 响应中不应返回敏感信息
- 如果房源已被删除或不存在，返回 404

### Side Effects / Data Changes
在 saved_listings 表中创建一条记录

## Unsave Listing
`DELETE /api/v1/saved-listings/{id}/`

### Description
取消收藏一个房源。只有已登录的租客用户可以取消收藏自己的收藏记录。

### Authentication
需要认证。

角色：tenant（租客）

#### Path Parameters

| 参数名 | 类型 |	必填 |	说明 |
|--------|------|------|------|
| id	| string(uuid)	| 是	| 收藏记录的唯一标识符 |

### Request Body
无请求体。

### Success Response
Status: `204 No Content`

无响应体。

### Error Responses
Status: `401 Unauthorized`

未登录。

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Status: `403 Forbidden`

尝试删除其他用户的收藏记录。

```json
{
  "detail": "You do not have permission to perform this action."
}
```

Status: `404 Not Found`

收藏记录不存在。

```json
{
  "detail": "Saved listing not found."
}
```

### Business Rules
- 用户只能取消收藏自己的收藏记录
- 取消收藏后不应返回任何内容（204）

### Side Effects / Data Changes
从 saved_listings 表中删除对应的记录


## List Saved Listings
`GET /api/v1/saved-listings/`

### Description
获取当前已登录租客用户的所有收藏房源列表。

### Authentication
需要认证。

角色：tenant（租客）

### Request Body
无请求体。

#### Success Response
Status: `200 OK`

```json
[
  {
    "id": "uuid",
    "created_at": "2026-05-10T12:00:00Z",
    "listing": {
      "id": "uuid",
      "title": "朝阳区温馨单间",
      "location": {
        "city": "北京",
        "administrative_area": "朝阳区",
        "suburb": "三里屯"
      },
      "price": 3500.00,
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

未登录。

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Business Rules
- 只返回当前登录用户的收藏记录
- 如果收藏的房源状态不是 published（例如已下架、已删除），则不在列表中显示
- 返回结果按 created_at 倒序排列（最新的在前）
- 如果没有收藏记录，返回空数组 []

### Side Effects / Data Changes
无副作用，此为只读接口。