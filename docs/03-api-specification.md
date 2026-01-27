# API Specification for RAG Integration

> This document defines the expected API endpoints and payload formats for integrating
> external property data sources with the RAG Property Agent system.

## Overview

The RAG system uses a **Universal Data Adapter** pattern. Any property API can be
integrated by implementing an adapter that transforms its data to our standard format.

---

## Required Endpoints

### 1. Search Properties (READ)

**Endpoint:** `GET /api/rag/properties`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Free text search query |
| `property_type` | string | `house`, `shophouse`, `land`, `apartment`, `warehouse`, `office`, `villa` |
| `listing_type` | string | `sale` or `rent` |
| `city` | string | City name |
| `district` | string | District/area name |
| `price_min` | number | Minimum price in IDR |
| `price_max` | number | Maximum price in IDR |
| `bedrooms_min` | number | Minimum bedrooms |
| `land_area_min` | number | Minimum land area (m²) |
| `building_area_min` | number | Minimum building area (m²) |
| `page` | number | Page number (default: 1) |
| `limit` | number | Items per page (default: 10, max: 50) |

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-or-unique-id",
      "title": "Rumah Mewah 3KT di Sunggal",
      "property_type": "house",
      "listing_type": "sale",
      "price": 1500000000,
      "location": "Sunggal",
      "city": "Medan",
      "address": "Jl. Sei Mencirim No. 45",
      "bedrooms": 3,
      "bathrooms": 2,
      "land_area": 180,
      "building_area": 150,
      "floors": 2,
      "description": "Rumah mewah siap huni...",
      "features": ["Garasi 2 mobil", "Dekat sekolah"],
      "certificate_type": "SHM",
      "status": "active",
      "images": [
        {
          "url": "https://..../image.jpg",
          "thumb_url": "https://..../thumb.jpg",
          "is_cover": true
        }
      ],
      "agent": {
        "id": "agent-uuid",
        "name": "John Doe",
        "phone": "08123456789",
        "whatsapp": "08123456789",
        "photo": "https://..../photo.jpg",
        "office": "MetaProperty Medan"
      },
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-22T15:30:00Z"
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 10,
    "last_page": 15,
    "has_more": true
  }
}
```

---

### 2. Get Property Detail (READ)

**Endpoint:** `GET /api/rag/properties/{id}`

**Response:** Same format as single item in search response, with full details.

---

### 3. Create Property (WRITE)

**Endpoint:** `POST /api/rag/properties`

**Headers:**
```
Authorization: Bearer {api_token}
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Rumah Baru 3KT",
  "property_type": "house",
  "listing_type": "sale",
  "price": 900000000,
  "location": "Helvetia",
  "city": "Medan",
  "address": "Jl. Helvetia No. 10",
  "bedrooms": 3,
  "bathrooms": 2,
  "land_area": 120,
  "building_area": 100,
  "floors": 2,
  "description": "Rumah baru minimalis...",
  "features": ["Carport", "Taman"],
  "certificate_type": "SHM"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Property created successfully",
  "data": { ... }  // Full property object
}
```

---

### 4. Update Property (WRITE)

**Endpoint:** `PUT /api/rag/properties/{id}`

**Headers:**
```
Authorization: Bearer {api_token}
Content-Type: application/json
```

**Request Body:** (only include fields to update)

```json
{
  "price": 950000000,
  "status": "sold",
  "description": "Updated description..."
}
```

**Response:**

```json
{
  "success": true,
  "message": "Property updated successfully",
  "data": { ... }  // Updated property object
}
```

---

### 5. Delete Property (WRITE)

**Endpoint:** `DELETE /api/rag/properties/{id}`

**Headers:**
```
Authorization: Bearer {api_token}
```

**Response:**

```json
{
  "success": true,
  "message": "Property deleted successfully"
}
```

---

## Authentication

For WRITE operations, the API must support Bearer token authentication:

```
Authorization: Bearer {api_token}
```

The API should:
1. Validate the token
2. Identify the agent/user making the request
3. Check ownership before allowing updates/deletes

---

## Error Responses

**Standard Error Format:**

```json
{
  "success": false,
  "message": "Error description",
  "errors": {
    "field_name": ["Validation error message"]
  }
}
```

**HTTP Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (not owner of property) |
| 404 | Not Found |
| 500 | Server Error |

---

## Data Types Reference

### Property Types

| Value | Description |
|-------|-------------|
| `house` | Rumah |
| `shophouse` | Ruko |
| `land` | Tanah |
| `apartment` | Apartemen |
| `warehouse` | Gudang |
| `office` | Kantor |
| `villa` | Villa |

### Listing Types

| Value | Description |
|-------|-------------|
| `sale` | Dijual |
| `rent` | Disewakan |

### Status

| Value | Description |
|-------|-------------|
| `active` | Available |
| `sold` | Terjual |
| `rented` | Tersewa |
| `inactive` | Not available |

### Certificate Types

| Value | Description |
|-------|-------------|
| `SHM` | Sertifikat Hak Milik |
| `SHGB` | Sertifikat Hak Guna Bangunan |
| `HGB` | Hak Guna Bangunan |
| `AJB` | Akta Jual Beli |
| `Girik` | Girik/Letter C |

---

## Notes for MetaProperty Implementation

The existing MetaProperty API endpoints can be used as-is:

| RAG Endpoint | MetaProperty Equivalent |
|--------------|------------------------|
| `GET /api/rag/properties` | `GET /api/website/listings` |
| `GET /api/rag/properties/{id}` | `GET /api/website/listings/{slug}` |
| `POST /api/rag/properties` | `POST /api/admin/listings` |
| `PUT /api/rag/properties/{id}` | `PUT /api/admin/listings/{id}` |
| `DELETE /api/rag/properties/{id}` | `DELETE /api/admin/listings/{id}` |

The adapter will handle the mapping between formats.

---

*Last Updated: 2026-01-23*
