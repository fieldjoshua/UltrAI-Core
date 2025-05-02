# Critical User Flows for MVP Testing

This document identifies the critical user flows that must be tested for the MVP release. These flows represent the core functionality that users will rely on and must work correctly for the MVP to be successful.

## 1. Document Analysis Flow

The most critical flow in the application is the document analysis process, which includes:

### 1.1 Document Upload

**Testing Priority: High**

- User can upload document in supported formats (PDF, DOCX, TXT)
- System validates document format and size
- Document is stored properly in the system
- Error handling for invalid documents

**Key API Endpoints:**
- `POST /api/documents/upload`
- `GET /api/documents/{document_id}`

**Test Cases:**
1. Upload valid documents in each supported format
2. Attempt to upload invalid formats
3. Upload documents exceeding size limits
4. Verify document metadata is correctly stored

### 1.2 Analysis Request

**Testing Priority: High**

- User can select document for analysis
- User can configure analysis parameters (models, depth, etc.)
- System validates and processes request
- Progress indicators work correctly

**Key API Endpoints:**
- `POST /api/analysis/create`
- `GET /api/analysis/{analysis_id}/status`

**Test Cases:**
1. Create analysis request with default parameters
2. Create analysis request with custom parameters
3. Create analysis with invalid parameters
4. Check status updates during processing

### 1.3 LLM Integration

**Testing Priority: Critical**

- System correctly calls appropriate LLM providers
- Handles LLM API responses and errors gracefully
- Processes and stores LLM results correctly
- Manages fallbacks if primary LLM is unavailable

**Key API Endpoints:**
- Internal calls to `/backend/services/llm_config_service.py`
- `POST /api/llm/process`

**Test Cases:**
1. Process document with mock OpenAI responses
2. Process document with mock Anthropic responses
3. Test fallback behavior when primary provider fails
4. Test error handling for rate limits and timeouts

### 1.4 Results Retrieval and Display

**Testing Priority: High**

- User can access analysis results
- Results are formatted and displayed correctly
- User can interact with results (expand, collapse, search)
- Results can be exported or shared

**Key API Endpoints:**
- `GET /api/analysis/{analysis_id}/results`
- `GET /api/analysis/{analysis_id}/export`

**Test Cases:**
1. Retrieve and display analysis results
2. Test interactive elements (expand/collapse sections)
3. Export results in different formats
4. Test caching and performance of results retrieval

## 2. User Authentication Flow

Authentication is necessary to protect user data and documents.

### 2.1 User Registration

**Testing Priority: Medium** (If included in MVP)

- New users can register with email/password
- System validates registration information
- Email verification works correctly (if implemented)
- New user account is created correctly

**Key API Endpoints:**
- `POST /api/auth/register`
- `POST /api/auth/verify-email` (if implemented)

**Test Cases:**
1. Register new user with valid information
2. Attempt registration with invalid data
3. Test email verification flow (if implemented)
4. Test duplicate registration attempt

### 2.2 Login/Logout

**Testing Priority: High**

- Registered users can log in
- System validates credentials
- Auth tokens are generated and stored correctly
- Users can log out and sessions are terminated

**Key API Endpoints:**
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/refresh-token`

**Test Cases:**
1. Log in with valid credentials
2. Attempt login with invalid credentials
3. Test token refresh flow
4. Verify logout terminates session

### 2.3 Session Management

**Testing Priority: Medium**

- Auth tokens are properly validated
- Protected routes require authentication
- Session timeouts work correctly
- Concurrent sessions are handled properly

**Key API Endpoints:**
- All protected API endpoints

**Test Cases:**
1. Access protected endpoints with valid token
2. Attempt access with invalid/expired token
3. Test session timeout behavior
4. Test concurrent login behavior

## 3. Analysis Configuration Flow

Users need to be able to configure how their documents are analyzed.

### 3.1 Model Selection

**Testing Priority: High**

- Available LLM models are displayed correctly
- User can select which models to use
- System respects model selection in analysis
- Unavailable models are properly indicated

**Key API Endpoints:**
- `GET /api/config/models`
- `POST /api/config/set-models`

**Test Cases:**
1. Retrieve available models list
2. Set active models for analysis
3. Verify model selection is respected in analysis
4. Test behavior with unavailable models

### 3.2 Analysis Parameters

**Testing Priority: Medium**

- User can configure analysis depth, focus, etc.
- Parameter validation works correctly
- System respects parameters in analysis
- Default parameters work as expected

**Key API Endpoints:**
- `GET /api/config/parameters`
- `POST /api/config/set-parameters`

**Test Cases:**
1. Retrieve available parameters
2. Set custom parameters for analysis
3. Verify parameters are respected in analysis
4. Test validation of invalid parameters

### 3.3 Configuration Management

**Testing Priority: Low** (May be post-MVP)

- User can save and load configurations
- Configurations are stored correctly
- User can share configurations
- Default configurations are available

**Key API Endpoints:**
- `GET /api/config/saved`
- `POST /api/config/save`
- `GET /api/config/defaults`

**Test Cases:**
1. Save custom configuration
2. Load saved configuration
3. Test default configurations
4. Share configuration with other users (if implemented)

## Testing Approach for MVP

For the MVP release, we will implement automated tests with the following approach:

1. **API Tests**: Implement pytest-based tests for all high-priority endpoints
   - Use FastAPI TestClient for endpoint testing
   - Create fixtures for common test data
   - Test both happy path and error conditions

2. **Mock-based LLM Tests**: Create mock responses for LLM providers
   - Store sample responses for different document types
   - Test both successful and error responses
   - Verify correct error handling and retries

3. **Frontend Integration Tests**: Limited set of tests for critical UI flows
   - Focus on document upload and analysis request
   - Verify results display and interaction
   - Test basic error states and loading indicators

4. **End-to-End Flow Tests**: A small set of tests covering the main user journey
   - Document upload → Analysis → Results viewing
   - Login → Document management → Analysis
   - Test at least one complete workflow

By focusing testing efforts on these critical flows, we can ensure the most important functionality works correctly for the MVP launch while deferring comprehensive testing for future iterations.