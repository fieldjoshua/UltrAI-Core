# ACTION: phase4-database-configuration

Version: 1.0
Created: 2025-05-18
Status: NOT_STARTED
Progress: 0%

## Objective

Configure PostgreSQL database for the deployed application, building on the successful Phase 3 authentication deployment.

## Context

Phase 3 successfully deployed with:
- Authentication endpoints working
- JWT token generation/validation
- Service URL: https://ultrai-core.onrender.com/
- Database health endpoint returns: "not_configured"

## Todo List

- [ ] **Create PostgreSQL database on Render**
  - Use Render's managed PostgreSQL service
  - Choose appropriate plan (free tier if available)
  - Note connection string

- [ ] **Create database schema**
  - Users table for authentication
  - Documents table for analysis storage
  - Results table for LLM responses
  - Create migration files with Alembic

- [ ] **Update environment configuration**
  - Add DATABASE_URL to Render environment
  - Ensure proper connection string format
  - Test connection from app

- [ ] **Create app_with_database_full.py**
  - Combine auth + full database support
  - Add database models
  - Add CRUD operations
  - Integrate with existing endpoints

- [ ] **Update requirements-phase4.txt**
  - Ensure all database dependencies included
  - Keep minimal approach

- [ ] **Deploy Phase 4**
  - Update render.yaml for Phase 4
  - Deploy to Render
  - Monitor deployment logs

- [ ] **Test database functionality**
  - Test user persistence
  - Test document storage
  - Test query operations
  - Verify data integrity

- [ ] **Document Phase 4 results**
  - Performance metrics with database
  - Database schema documentation
  - Update deployment guide

## Success Criteria

1. Database successfully provisioned on Render
2. All tables created with proper schema
3. Authentication uses database for user storage
4. Document storage/retrieval working
5. Response times remain under 500ms
6. Database health endpoint returns "connected"

## Dependencies

- Completed Phase 3 deployment
- Render database service
- PostgreSQL connection details

## Technical Details

### Database Schema

```sql
-- Users table (authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    content TEXT,
    file_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    llm_provider VARCHAR(50),
    prompt TEXT,
    response TEXT,
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Environment Variables

```
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET=<existing-secret>
```

## Notes

- Use SQLAlchemy ORM for database operations
- Implement connection pooling
- Add database indexes for performance
- Consider data retention policies
- Implement proper error handling for database operations

## Next Phase Preview

Phase 5 will add:
- Redis caching layer
- Response caching
- Session management
- Rate limiting with Redis