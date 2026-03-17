# FrontierQu API Specification

**Version:** 1.0.0
**Last Updated:** March 14, 2026
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Endpoints](#endpoints)
5. [Request/Response Format](#requestresponse-format)
6. [Error Codes](#error-codes)
7. [Versioning Strategy](#versioning-strategy)
8. [Client SDKs](#client-sdks)

---

## Overview

FrontierQu API is a REST-based interface providing access to 195+ neuro-symbolic AI models, knowledge graph operations, and Quranic research capabilities. The API is built on FastAPI and deployed with OpenAPI/Swagger documentation.

### Base URL

```
Production: https://api.frontierqu.ai/v1
Development: http://localhost:8000/v1
```

### API Documentation

- **Swagger UI:** `/api/docs`
- **ReDoc:** `/api/redoc`
- **OpenAPI Specification:** `/openapi.json`

### Key Capabilities

- **Model Serving:** Access to 195+ architectures (neural, symbolic, quantum)
- **Knowledge Graph:** Query theological relationships, verses, tafsirs, hadiths
- **Semantic Search:** Vector-based concept matching
- **Governance:** Scholar board operations, audit logs, correction workflows
- **Corpus Management:** Verse, hadith, tafsir, and madhab data access

---

## Authentication

### JWT Token Format

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id_123",
    "email": "user@example.com",
    "role": "scholar",
    "scholar_board_member": true,
    "iat": 1678886400,
    "exp": 1678972800
  },
  "signature": "HMACSHA256(...)"
}
```

### Obtaining a Token

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "scholar@institution.edu",
  "password": "secure_password",
  "mfa_code": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "scholar@institution.edu",
    "role": "scholar",
    "permissions": ["read:corpus", "write:corrections", "read:audit_logs"]
  }
}
```

### Refresh Token

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

### User Roles

| Role | Access Level | Permissions |
|------|--------------|-------------|
| **public** | Read-only | Quran text, tafsirs, general history |
| **student** | Enhanced read | Hadith chains, linguistic analysis, basic fiqh |
| **scholar** | Write access | Corrections, annotations, audit logs |
| **board_member** | Administrative | System configuration, approval authority |

---

## Rate Limiting

### Limits by Role

| Role | Requests/Minute | Concurrent Requests | Burst Allowance |
|------|-----------------|---------------------|-----------------|
| public | 30 | 5 | 50 |
| student | 100 | 10 | 150 |
| scholar | 300 | 20 | 500 |
| board_member | 1000 | 50 | Unlimited |

### Rate Limit Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 287
X-RateLimit-Reset: 1678890000
X-RateLimit-RetryAfter: 60
```

### Handling Rate Limits

When limit is exceeded (HTTP 429):

```json
{
  "error": "rate_limit_exceeded",
  "message": "API rate limit exceeded",
  "retry_after": 60,
  "limit_details": {
    "limit": 300,
    "window_seconds": 60,
    "reset_at": "2026-03-14T15:00:00Z"
  }
}
```

---

## Endpoints

### Health & Status

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-14T14:30:00Z",
  "version": "1.0.0",
  "components": {
    "database": "operational",
    "knowledge_graph": "operational",
    "vector_store": "operational",
    "model_service": "operational"
  }
}
```

---

### Models

#### GET /models
List all available models.

**Response:**
```json
{
  "total_models": 195,
  "categories": {
    "neural": 120,
    "symbolic": 45,
    "quantum": 20,
    "neuro_symbolic": 10
  },
  "models": [
    {
      "name": "memetic",
      "category": "neural",
      "version": "1.0.0",
      "input_dim": 64,
      "embed_dim": 128,
      "parameters_millions": 12.5
    }
  ]
}
```

#### POST /models/{model_name}/load
Load a model into memory.

**Parameters:**
- `model_name` (path): Model identifier
- `input_dim` (query, default: 64): Input dimension
- `embed_dim` (query, default: 128): Embedding dimension

**Response:**
```json
{
  "status": "success",
  "model": "memetic",
  "loaded_at": "2026-03-14T14:30:00Z",
  "memory_usage_mb": 245
}
```

#### POST /inference
Run inference on a model.

**Request:**
```json
{
  "model_name": "memetic",
  "input_data": [[0.1, 0.2, ..., 0.64]],
  "parameters": {
    "temperature": 0.7,
    "top_k": 40,
    "max_tokens": 256
  }
}
```

**Response:**
```json
{
  "request_id": "req_abc123",
  "model_name": "memetic",
  "output": {
    "embeddings": [[...]],
    "logits": [[...]],
    "confidence": 0.95
  },
  "inference_time_ms": 245,
  "timestamp": "2026-03-14T14:30:00Z"
}
```

---

### Knowledge Graph

#### GET /graph/verses/{surah}:{ayah}
Get a verse and related entities.

**Response:**
```json
{
  "verse": {
    "id": "QURAN_2_183",
    "surah": 2,
    "ayah": 183,
    "text_arabic": "يَا أَيُّهَا الَّذِينَ آمَنُوا كُتِبَ عَلَيْكُمُ الصِّيَامُ",
    "text_english": "O you who have believed, decreed upon you is fasting...",
    "revelation_context": "Sha'ban 2 AH",
    "category": "Ahkam (Legal Rulings)"
  },
  "tafsirs": [
    {
      "scholar": "Ibn Kathir",
      "edition": "Dar al-Turath 1999",
      "text": "...",
      "confidence": 1.0
    }
  ],
  "hadiths": [
    {
      "text": "...",
      "chain": "Sahih Bukhari",
      "grade": "Sahih",
      "confidence": 0.99
    }
  ],
  "madhab_rulings": {
    "hanafi": { "ruling": "...", "confidence": 0.95 },
    "maliki": { "ruling": "...", "confidence": 0.93 },
    "shafi": { "ruling": "...", "confidence": 0.96 },
    "hanbali": { "ruling": "...", "confidence": 0.94 }
  }
}
```

#### GET /graph/search
Semantic search across knowledge graph.

**Query Parameters:**
- `q` (required): Search query
- `type` (optional): Filter by entity type (verse, tafsir, hadith, madhab)
- `limit` (optional, default: 10): Max results
- `offset` (optional, default: 0): Pagination offset

**Response:**
```json
{
  "query": "fasting",
  "total_results": 342,
  "results": [
    {
      "id": "QURAN_2_183",
      "type": "verse",
      "title": "Verse 2:183 - Fasting Ordained",
      "snippet": "O you who have believed, decreed upon you is fasting...",
      "relevance_score": 0.98,
      "confidence": 1.0
    }
  ]
}
```

---

### Corrections & Governance

#### POST /corrections
Submit a correction to the system.

**Request:**
```json
{
  "entity_type": "hadith",
  "entity_id": "HADITH_BUKHARI_1234",
  "correction_type": "grade_error",
  "evidence": "This hadith is Dhaif, not Sahih, as per Al-Albani's classification",
  "citation": {
    "source": "Silsilah al-Ahadith ad-Daifah",
    "page": 123,
    "year": 1995
  },
  "impact_level": "high"
}
```

**Response:**
```json
{
  "correction_id": "corr_xyz789",
  "status": "pending_review",
  "created_at": "2026-03-14T14:30:00Z",
  "assigned_reviewers": ["scholar1@institution.edu", "scholar2@institution.edu"],
  "timeline": {
    "review_deadline": "2026-03-21T14:30:00Z",
    "expected_resolution": "2026-03-28T14:30:00Z"
  }
}
```

#### GET /corrections/{correction_id}
Get correction details and review history.

**Response:**
```json
{
  "id": "corr_xyz789",
  "status": "pending_review",
  "entity_type": "hadith",
  "entity_id": "HADITH_BUKHARI_1234",
  "correction_type": "grade_error",
  "evidence": "...",
  "reviewer_comments": [
    {
      "reviewer": "scholar1@institution.edu",
      "comment": "Evidence is compelling. Recommend approval.",
      "status": "pending",
      "timestamp": "2026-03-15T10:00:00Z"
    }
  ],
  "approval_progress": {
    "total_required": 3,
    "approved": 1,
    "rejected": 0,
    "pending": 2
  }
}
```

#### POST /corrections/{correction_id}/vote
Scholar board votes on a correction.

**Request:**
```json
{
  "decision": "approve",
  "reasoning": "Evidence convincingly demonstrates a factual error in the original classification.",
  "confidence": 0.95
}
```

**Response:**
```json
{
  "correction_id": "corr_xyz789",
  "your_vote": "approve",
  "current_status": "pending_review",
  "approval_progress": {
    "total_required": 3,
    "approved": 2,
    "rejected": 0,
    "pending": 1
  },
  "next_action": "Awaiting final reviewer decision"
}
```

---

### Audit & Logging

#### GET /audit-logs
Retrieve audit logs (scholars only).

**Query Parameters:**
- `start_date` (optional): ISO 8601 timestamp
- `end_date` (optional): ISO 8601 timestamp
- `user_id` (optional): Filter by user
- `action_type` (optional): query, correction, approval, denial
- `limit` (optional, default: 100): Max records

**Response:**
```json
{
  "total_records": 1523,
  "logs": [
    {
      "timestamp": "2026-03-14T14:30:00Z",
      "user_id": "user_123",
      "user_email": "scholar@institution.edu",
      "action_type": "correction_submitted",
      "entity_type": "hadith",
      "entity_id": "HADITH_BUKHARI_1234",
      "details": {
        "correction_id": "corr_xyz789",
        "correction_type": "grade_error"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

---

### System Configuration

#### GET /system/configuration
Get current system configuration (board members only).

**Response:**
```json
{
  "version": "1.0.0",
  "deployment_mode": "production",
  "active_madhabs": ["hanafi", "maliki", "shafi", "hanbali"],
  "confidence_threshold": 0.80,
  "audit_sampling_rate": 0.05,
  "rate_limits": {
    "public": 30,
    "student": 100,
    "scholar": 300,
    "board": 1000
  },
  "corpus_version": "golden_v1.0_2024"
}
```

#### PATCH /system/configuration
Update system configuration (board members only).

**Request:**
```json
{
  "confidence_threshold": 0.85,
  "audit_sampling_rate": 0.10
}
```

---

## Request/Response Format

### Standard Request Format

All POST/PATCH requests use JSON:

```
Content-Type: application/json
```

### Standard Response Format

All responses follow a consistent envelope:

**Success (2xx):**
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "meta": {
    "timestamp": "2026-03-14T14:30:00Z",
    "request_id": "req_abc123",
    "api_version": "1.0.0"
  }
}
```

**Error (4xx, 5xx):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request was invalid",
    "details": {
      "field": "model_name",
      "issue": "Model not found"
    }
  },
  "meta": {
    "timestamp": "2026-03-14T14:30:00Z",
    "request_id": "req_abc123",
    "api_version": "1.0.0"
  }
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | OK | Request succeeded |
| **201** | Created | Resource created |
| **400** | Bad Request | Invalid parameters |
| **401** | Unauthorized | Missing/invalid token |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Error | Server error |
| **503** | Service Unavailable | Maintenance mode |

### Error Response Examples

#### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Input validation failed",
    "details": {
      "field": "model_name",
      "issue": "Model name must be alphanumeric",
      "provided": "model@123"
    }
  }
}
```

#### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Authentication required",
    "details": {
      "reason": "Invalid or expired token"
    }
  }
}
```

#### 403 Forbidden
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to access this resource",
    "details": {
      "required_role": "scholar",
      "your_role": "student"
    }
  }
}
```

#### 429 Rate Limit
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "details": {
      "limit": 300,
      "window_seconds": 60,
      "retry_after": 45
    }
  }
}
```

---

## Versioning Strategy

### Version Format

API versions follow semantic versioning: `MAJOR.MINOR.PATCH`

### Versioning Timeline

- **v1.x (Current):** Production. Backwards-compatible updates.
- **v2.x (Planned):** Major architectural changes. Overlaps with v1.x for 6 months.
- **Deprecation:** 12-month notice before endpoint removal.

### Version Negotiation

**URL-based (Recommended):**
```
https://api.frontierqu.ai/v1/models
```

**Header-based:**
```
Accept-Version: 1.0.0
```

---

## Client SDKs

### Python SDK

**Installation:**
```bash
pip install frontierqu-sdk
```

**Basic Usage:**
```python
from frontierqu import FrontierQuClient

# Initialize client
client = FrontierQuClient(
    api_key="your_api_key",
    base_url="https://api.frontierqu.ai/v1"
)

# List models
models = client.models.list()

# Run inference
result = client.models.inference(
    model_name="memetic",
    input_data=[[0.1, 0.2, ..., 0.64]],
    parameters={"temperature": 0.7}
)

# Search knowledge graph
results = client.graph.search(
    query="fasting",
    type="verse"
)

# Submit correction
correction = client.corrections.submit(
    entity_type="hadith",
    entity_id="HADITH_BUKHARI_1234",
    correction_type="grade_error",
    evidence="Evidence text...",
    impact_level="high"
)
```

**Full Documentation:** See `/docs/PYTHON_SDK_GUIDE.md`

### JavaScript/TypeScript SDK

**Installation:**
```bash
npm install @frontierqu/sdk
```

**Basic Usage:**
```typescript
import { FrontierQuClient } from '@frontierqu/sdk';

const client = new FrontierQuClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.frontierqu.ai/v1'
});

// List models
const models = await client.models.list();

// Run inference
const result = await client.models.inference({
  modelName: 'memetic',
  inputData: [[0.1, 0.2, ..., 0.64]],
  parameters: { temperature: 0.7 }
});

// Search knowledge graph
const results = await client.graph.search({
  query: 'fasting',
  type: 'verse'
});
```

**Full Documentation:** See `/docs/JAVASCRIPT_SDK_GUIDE.md`

---

## Additional Resources

- **OpenAPI Spec:** `/openapi.json`
- **Swagger UI:** `/api/docs`
- **ReDoc:** `/api/redoc`
- **Status Page:** https://status.frontierqu.ai
- **Support:** support@frontierqu.ai

---

**Last Updated:** March 14, 2026
**Next Review:** June 14, 2026
