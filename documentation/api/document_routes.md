# Document Routes API Documentation

## Overview

The document routes provide endpoints for managing document uploads, processing, and retrieval in the Ultra backend. These routes implement the multi-layered architecture described in the UltrLLMOrchestrator patent, featuring robust error handling, resource management, and transaction-based state management.

## Error Handling

The document routes use a standardized error handling system that provides detailed error information and proper cleanup:

- **ResourceNotFoundError**: When a document or session cannot be found
- **ServiceError**: For internal service failures with detailed context
- **ValidationError**: For input validation failures
- All errors include detailed context and proper cleanup procedures

## Endpoints

### Upload Document

```http
POST /api/upload-document
```

Uploads a document to the system with proper chunking and error handling.

**Request:**

- Content-Type: multipart/form-data
- Body: File upload

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "size": "number",
  "type": "string",
  "status": "string",
  "message": "string"
}
```

**Error Cases:**

- 400: Invalid file
- 404: Resource not found
- 500: Service error with details

### Get Document

```http
GET /api/documents/{document_id}
```

Retrieves document details by ID.

**Parameters:**

- document_id: string (path)

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "size": "number",
  "type": "string",
  "status": "string",
  "uploadDate": "string"
}
```

**Error Cases:**

- 404: Document not found
- 500: Service error with details

### List Documents

```http
GET /api/documents
```

Lists all uploaded documents.

**Response:**

```json
[
  {
    "id": "string",
    "name": "string",
    "size": "number",
    "type": "string",
    "status": "string",
    "uploadDate": "string"
  }
]
```

**Error Cases:**

- 500: Service error with details

### Create Document Session

```http
POST /api/create-document-session
```

Creates a session for chunked document upload.

**Request:**

```json
{
  "fileName": "string",
  "fileSize": "number",
  "chunkSize": "number",
  "totalChunks": "number"
}
```

**Response:**

```json
{
  "success": "boolean",
  "session_id": "string",
  "message": "string"
}
```

**Error Cases:**

- 400: Missing required fields
- 500: Service error with details

### Upload Document Chunk

```http
POST /api/upload-document-chunk
```

Uploads a chunk of a document within a session.

**Request:**

- Content-Type: multipart/form-data
- Body:
  - session_id: string
  - chunk_index: string
  - chunk: File

**Response:**

```json
{
  "success": "boolean",
  "message": "string"
}
```

**Error Cases:**

- 404: Session not found
- 500: Service error with details

## Implementation Details

### Resource Management

- Documents are stored in chunks for efficient handling
- Default chunk size: 1MB
- Automatic cleanup on failed uploads
- Session-based management for large files

### State Management

- Transaction-based metadata updates
- Atomic file operations
- Proper cleanup on failures
- Session state tracking

### Error Recovery

- Automatic cleanup of partial uploads
- Detailed error context for debugging
- Proper resource release
- Transaction rollback on failures

## Dependencies

- FastAPI
- UltraDocumentsOptimized service
- Error handling system
- Logging system

## Configuration

- Document storage path: Configurable via DOCUMENT_STORAGE_PATH environment variable
- Default chunk size: 1MB (configurable)
- File type restrictions: None (handled by service layer)
