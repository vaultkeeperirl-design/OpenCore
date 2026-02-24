# Patch Journal

## 2026-02-25 - Unlimited File Upload Vulnerability

**Learning:** The application lacked input validation for file uploads on both the client (frontend) and server (backend), potentially leading to denial-of-service via memory exhaustion. This highlights a need for comprehensive input validation at all boundaries.
**Action:** Implemented strict file size limits on the client side (10MB) and a backend safeguard (15MB for Base64 payloads). Future endpoints accepting files must include explicit size validation.
