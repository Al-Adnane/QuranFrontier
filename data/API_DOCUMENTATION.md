# Kasbah Frontier API Documentation

## Version 3.5.0 | 32 Modules | 180+ Capabilities

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Modules](#modules)
5. [Endpoints](#endpoints)
6. [Examples](#examples)
7. [Error Handling](#error-handling)
8. [Rate Limits](#rate-limits)

---

## Overview

The Kasbah Frontier API provides access to 32+ frontier technology modules for next-generation deepfake detection, privacy-preserving AI, and security testing.

### Capabilities

- **Privacy & Cryptography**: Differential Privacy, SMPC, Homomorphic Encryption, Zero-Knowledge ML
- **AI/ML Core**: Federated Learning, Continual Learning, Self-Supervised Detection, Quantum ML
- **Detection**: GenAI Detection, Temporal Forensics, Attention Forensics, Biometric Protection
- **Security**: Threat Simulation, Red Team Framework, AI Supply Chain Security
- **Intelligence**: Predictive Threat Intelligence, Cognitive Security, Memetic Warfare

---

## Authentication

```http
Authorization: Bearer <api_key>
```

---

## Base URL

```
https://api.kasbah.ai/v1
```

Development: `http://localhost:3000/api`

---

## Modules

### Module Categories

| Category | Modules |
|----------|---------|
| **Privacy & Crypto** | `differential-privacy`, `smpc`, `homomorphic-encryption`, `quantum-resistant`, `zero-knowledge-ml` |
| **AI/ML** | `federated-learning`, `continual-learning`, `self-supervised`, `quantum-ml`, `neuro-symbolic` |
| **Detection** | `genai-detection`, `temporal-forensics`, `attention-forensics`, `biometric-protection` |
| **Security** | `threat-simulation`, `red-team`, `ai-supply-chain`, `adversarial-defense` |
| **Intelligence** | `predictive-intelligence`, `cognitive-security`, `memetic-warfare`, `honeypot` |
| **Specialized** | `quran-frontier`, `neuromorphic`, `swarm-intelligence`, `self-healing` |

---

## Endpoints

### System Status

```http
GET /api/frontier?module=status
```

**Response:**
```json
{
  "status": "operational",
  "version": "3.5.0",
  "modules": {
    "genaiDetection": { "status": "active", "features": ["llm-text", "ai-art", "synthetic-voice"] },
    "quantumML": { "status": "active", "features": ["qfe", "vqc", "quantum-kernel"] }
  },
  "totalModules": 32,
  "totalCapabilities": 180
}
```

---

### GenAI Detection Suite

#### Detect AI-Generated Content

```http
POST /api/frontier?action=genai-detect
Content-Type: application/json

{
  "content": "base64-encoded-content",
  "modality": "auto" | "text" | "image" | "audio" | "video"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "id": "genai-123456",
    "modality": "text",
    "isAIGenerated": true,
    "confidence": 0.89,
    "generatorAttribution": {
      "generator": "ChatGPT",
      "modelFamily": "GPT",
      "confidence": 0.82
    },
    "artifacts": [
      {
        "type": "perplexity_anomaly",
        "severity": "high",
        "evidence": "Perplexity score: 12.3 vs baseline 50"
      }
    ]
  }
}
```

---

### Zero-Knowledge ML

#### Generate Private Detection Proof

```http
POST /api/frontier?action=zkml-proof
Content-Type: application/json

{
  "content": "base64-content",
  "modelCommitment": "hash-of-model-weights",
  "submitOnChain": false
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "detection": "real",
    "confidence": 0.92,
    "proof": {
      "id": "proof-123",
      "type": "detection_validity",
      "verificationKey": "0xabc...",
      "verified": false
    }
  }
}
```

---

### Quantum ML Detection

#### Quantum-Enhanced Detection

```http
POST /api/frontier?action=quantum-detect
Content-Type: application/json

{
  "features": [0.1, 0.2, 0.3, ...],
  "qubits": 8,
  "shots": 1024
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "quantumProbability": 0.78,
    "classicalProbability": 0.65,
    "quantumAdvantage": 1.2,
    "fidelity": 0.95,
    "circuitDepth": 24
  }
}
```

---

### Predictive Threat Intelligence

#### Predict Attack Likelihood

```http
POST /api/frontier?action=threat-predict
Content-Type: application/json

{
  "target": "infrastructure-name",
  "timeframe": {
    "start": "2024-01-01",
    "end": "2024-01-31",
    "granularity": "days"
  }
}
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "probability": 0.72,
    "confidence": 0.85,
    "threatCategory": "ransomware",
    "mitigationStrategies": [
      "Implement backup procedures",
      "Segment network",
      "Deploy EDR solutions"
    ]
  }
}
```

---

### Temporal Forensics

#### Analyze Video Timeline

```http
POST /api/frontier?action=temporal-analyze
Content-Type: application/json

{
  "videoFrames": ["base64-frame1", "base64-frame2", ...],
  "sampleRate": 10
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "coherenceScore": 0.85,
    "manipulationEvents": [
      {
        "type": "face_swap",
        "frameRange": { "start": 45, "end": 120 },
        "confidence": 0.92
      }
    ],
    "generationInfo": {
      "estimatedGenerations": 2,
      "reEncodings": 1
    }
  }
}
```

---

### AI Supply Chain Security

#### Audit Model Supply Chain

```http
POST /api/frontier?action=supply-chain-audit
Content-Type: application/json

{
  "modelId": "model-123",
  "verifyProvenance": true,
  "checkWatermarks": true
}
```

**Response:**
```json
{
  "success": true,
  "audit": {
    "trustScore": 0.85,
    "findings": [
      {
        "category": "provenance",
        "severity": "low",
        "title": "Training data license not verified"
      }
    ],
    "supplyChainDepth": 3
  }
}
```

---

### Self-Supervised Detection

#### Train and Detect

```http
POST /api/frontier?action=self-supervised-detect
Content-Type: application/json

{
  "unlabeledData": ["sample1", "sample2", ...],
  "input": "base64-input",
  "epochs": 10
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "detection": "anomaly",
    "anomalyScore": 2.5,
    "confidence": 0.78,
    "nearestNeighbors": [
      { "id": "sample-5", "distance": 0.12 }
    ]
  }
}
```

---

### Stress Testing

#### Run Stress Test

```http
POST /api/frontier?action=stress-test
Content-Type: application/json

{
  "config": {
    "requestsPerSecond": 100,
    "duration": 60000,
    "pattern": "sine"
  }
}
```

**Response:**
```json
{
  "success": true,
  "testId": "stress-123",
  "summary": {
    "totalRequests": 6000,
    "successfulRequests": 5950,
    "avgLatency": 125,
    "p99Latency": 450
  }
}
```

---

### Chaos Engineering

#### Run Chaos Experiment

```http
POST /api/frontier?action=chaos-experiment
Content-Type: application/json

{
  "experiment": {
    "type": "network_latency",
    "target": "api-service",
    "latencyMs": 500,
    "duration": 60000
  }
}
```

**Response:**
```json
{
  "success": true,
  "experimentId": "chaos-123",
  "status": "completed",
  "hypothesisValidated": true,
  "recoveryTime": 45000
}
```

---

### Compliance Audit

#### Run Compliance Check

```http
POST /api/frontier?action=compliance-check
Content-Type: application/json

{
  "framework": "GDPR",
  "scope": ["data-processing", "consent", "rights"]
}
```

**Response:**
```json
{
  "success": true,
  "reportId": "compliance-123",
  "score": 0.92,
  "passed": true,
  "findings": {
    "critical": 0,
    "high": 2,
    "medium": 5
  }
}
```

---

### Red Team Operations

#### Run Red Team Operation

```http
POST /api/frontier?action=red-team-operation
Content-Type: application/json

{
  "operation": {
    "type": "penetration-test",
    "targets": ["api", "web-app"],
    "intensity": "moderate"
  }
}
```

**Response:**
```json
{
  "success": true,
  "operationId": "op-123",
  "status": "completed",
  "objectivesAchieved": 3,
  "findingsCount": 5
}
```

---

## Examples

### JavaScript/TypeScript

```typescript
import { GenAIDetectionSuite, QuantumDetectionSuite } from '@/lib/frontier';

// GenAI Detection
const genai = new GenAIDetectionSuite();
const result = await genai.detect(contentBuffer, 'auto');

if (result.isAIGenerated) {
  console.log(`Detected ${result.generatorAttribution?.generator}`);
}

// Quantum Detection
const quantum = new QuantumDetectionSuite(8);
const qResult = await quantum.detect(features, 0.5);
console.log(`Quantum advantage: ${qResult.quantumAdvantage}x`);
```

### cURL

```bash
# Check system status
curl -X GET "https://api.kasbah.ai/api/frontier?module=status"

# Detect AI-generated content
curl -X POST "https://api.kasbah.ai/api/frontier?action=genai-detect" \
  -H "Content-Type: application/json" \
  -d '{"content": "base64-content", "modality": "text"}'

# Run stress test
curl -X POST "https://api.kasbah.ai/api/frontier?action=stress-test" \
  -H "Content-Type: application/json" \
  -d '{"config": {"requestsPerSecond": 100, "duration": 60000}}'
```

### Python

```python
import requests

BASE_URL = "https://api.kasbah.ai/api/frontier"

# Get status
response = requests.get(f"{BASE_URL}?module=status")
print(response.json())

# GenAI detection
data = {"content": "base64-content", "modality": "text"}
response = requests.post(f"{BASE_URL}?action=genai-detect", json=data)
result = response.json()
print(f"AI Generated: {result['result']['isAIGenerated']}")
```

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## Rate Limits

| Tier | Requests/min | Requests/day |
|------|--------------|--------------|
| Free | 60 | 1,000 |
| Pro | 600 | 50,000 |
| Enterprise | Unlimited | Unlimited |

---

## Changelog

### v3.5.0 (Latest)
- Added Quantum ML Detection
- Added Predictive Threat Intelligence
- Added Self-Supervised Detection Engine
- Enhanced API documentation

### v3.4.0
- Added GenAI Detection Suite
- Added AI Supply Chain Security
- Added Zero-Knowledge ML
- Added Temporal Forensics

### v3.3.0
- Added Threat Simulation
- Added Stress Testing
- Added Chaos Engineering
- Added Deployment Validator
- Added Compliance Audit
- Added Red Team Framework

---

## Support

- Documentation: https://docs.kasbah.ai
- GitHub: https://github.com/kasbah/frontier
- Email: support@kasbah.ai

---

**Kasbah Frontier Engine v3.5.0** | 32 Modules | 180+ Capabilities | $2B+ Valuation
