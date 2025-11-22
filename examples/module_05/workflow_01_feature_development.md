# Workflow 01: Feature Development with AI

**Task**: Add user authentication to an existing FastAPI REST API

**Duration**: ~2 hours (vs ~4-5 hours without AI)

**Tools Used**:
- Claude Code (architecture, complex logic)
- GitHub Copilot (boilerplate, tests)
- Cursor (quick edits)

---

## 🎯 Goal

Add complete JWT-based authentication to a FastAPI application:
- Login/logout endpoints
- Token refresh mechanism
- Protected routes
- User registration
- Password hashing
- Database integration (PostgreSQL)

---

## 📋 Phase 1: Architecture Planning (Claude Code)

### Why Claude Code?
- Needs to understand existing codebase structure
- Architectural decisions require reasoning
- Multi-file changes

### Prompt Template

```
I need to add JWT authentication to my FastAPI app.

Current structure:
- src/api/routes/ (existing endpoints)
- src/db/models.py (SQLAlchemy models)
- src/core/config.py (app configuration)
- PostgreSQL database

Requirements:
- JWT tokens (access + refresh)
- Password hashing with bcrypt
- /auth/register, /auth/login, /auth/logout, /auth/refresh endpoints
- Protect existing routes with @require_auth decorator
- Store refresh tokens in database

Questions:
1. Where should I put the auth logic? (new module? separate service?)
2. How should I structure the token refresh flow?
3. Should I use dependency injection for the current user?

Please suggest:
- File structure
- Key design decisions
- Implementation approach
```

### Expected Response

Claude will analyze your codebase and suggest:

1. **File Structure**:
```
src/
├── auth/
│   ├── __init__.py
│   ├── router.py          # Auth endpoints
│   ├── dependencies.py    # get_current_user, require_auth
│   ├── schemas.py         # Pydantic models
│   ├── service.py         # Business logic (hashing, token generation)
│   └── models.py          # User, RefreshToken models
```

2. **Design Decisions**:
- Use FastAPI dependency injection for `get_current_user`
- Store only refresh tokens in DB (access tokens stateless)
- Use python-jose for JWT encoding/decoding
- Bcrypt for password hashing

3. **Implementation Steps**:
- Create auth module structure
- Add User and RefreshToken models
- Implement token generation/validation
- Create auth endpoints
- Add auth dependencies
- Protect existing routes

---

## 📋 Phase 2: Implementation (Copilot + Claude Code)

### Step 1: Create Models (Copilot)

**File**: `src/auth/models.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from src.db.base import Base
from datetime import datetime

# Type this comment and let Copilot suggest:
# User model with id, email, hashed_password, created_at

class User(Base):
    __tablename__ = "users"

    # Copilot will suggest these fields based on your comment
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# RefreshToken model with token, user_id, expires_at
class RefreshToken(Base):
    # Copilot fills this in following the pattern above
    ...
```

**Tip**: Copilot learns from your first model and replicates the pattern.

---

### Step 2: Token Service (Claude Code)

**Why Claude?** Complex logic with security considerations.

**Prompt**:
```
Create a token service in src/auth/service.py with:
- create_access_token(user_id) -> returns JWT access token (15 min expiry)
- create_refresh_token(user_id) -> returns JWT refresh token (7 days expiry)
- verify_token(token) -> returns payload or raises exception
- hash_password(password) -> bcrypt hash
- verify_password(plain, hashed) -> bool

Use:
- python-jose for JWT
- passlib with bcrypt for passwords
- Secret key from config

Include proper error handling and type hints.
```

Claude will generate a complete service with:
- Proper imports
- Configuration management
- Error handling
- Type annotations
- Security best practices

---

### Step 3: Auth Endpoints (Copilot)

**File**: `src/auth/router.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.auth import schemas, service
from src.db.session import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

# Type: @router.post("/register", response_model=
# Copilot suggests the entire endpoint:

@router.post("/register", response_model=schemas.UserResponse)
async def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    # [Copilot suggests the logic based on FastAPI patterns]
    ...

# Type: @router.post("/login"
# Copilot replicates the pattern:

@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    credentials: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    # [Copilot fills in the logic]
    ...
```

**Tip**: After writing the first endpoint completely, Copilot will suggest similar patterns for the remaining endpoints.

---

### Step 4: Dependencies (Claude Code)

**Why Claude?** Needs to integrate with existing FastAPI patterns.

**Prompt**:
```
Create auth dependencies in src/auth/dependencies.py:

1. get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))
   - Verifies JWT token
   - Loads user from database
   - Returns User object
   - Raises 401 if invalid

2. require_auth - alias for Depends(get_current_user)

Show me how to use this in existing routes.
```

Claude generates the dependency and shows integration:

```python
# In your existing routes:
from src.auth.dependencies import get_current_user, User

@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    return {"message": f"Hello {current_user.email}"}
```

---

## 📋 Phase 3: Testing (Copilot)

### Why Copilot?
Tests follow patterns - perfect for Copilot!

**File**: `tests/test_auth.py`

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Type: def test_register_success():
# Copilot suggests:

def test_register_success():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["email"] == "test@example.com"

# Type: def test_register_duplicate_email():
# Copilot follows the pattern:

def test_register_duplicate_email():
    # Register once
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    # Try to register again
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 400

# Copilot will suggest 10+ more test cases following this pattern!
```

---

## 📋 Phase 4: Quick Fixes (Cursor Cmd+K)

After implementing, you'll find small issues. Use Cursor Cmd+K for quick edits:

**Example 1**: Missing error handling
```
Select function → Cmd+K → "Add try/except for database errors"
```

**Example 2**: Missing validation
```
Select endpoint → Cmd+K → "Add email format validation"
```

**Example 3**: Documentation
```
Select function → Cmd+K → "Add docstring explaining parameters and return value"
```

---

## 📋 Phase 5: Integration Testing (Claude Code)

**Prompt**:
```
I've implemented auth. Help me test end-to-end:

1. Register a user
2. Login and get tokens
3. Access protected endpoint with token
4. Refresh token
5. Logout

Generate a test script that verifies the full flow.
```

Claude generates a comprehensive test script you can run manually or automate.

---

## ✅ Checklist

- [ ] **Phase 1**: Architecture planned (file structure, design decisions)
- [ ] **Phase 2**: Core implementation complete (models, services, routes)
- [ ] **Phase 3**: Unit tests written and passing
- [ ] **Phase 4**: Edge cases handled (validation, error handling)
- [ ] **Phase 5**: Integration tested (full flow works)
- [ ] **Security Review**: Check for common vulnerabilities
  - [ ] SQL injection protection (using parameterized queries)
  - [ ] Password stored hashed (never plain text)
  - [ ] JWT secret is secure and not hardcoded
  - [ ] Token expiry implemented correctly
  - [ ] HTTPS enforced in production
- [ ] **Documentation**: API docs updated (FastAPI auto-generates)
- [ ] **Code Review**: Manual review of all AI-generated code

---

## 📊 Time Comparison

**Without AI** (estimated):
- Architecture: 30 min
- Implementation: 2-3 hours
- Testing: 1 hour
- Debugging: 30-60 min
- **Total: 4-5 hours**

**With AI** (actual):
- Architecture (Claude): 15 min
- Implementation (Copilot + Claude): 45 min
- Testing (Copilot): 20 min
- Quick fixes (Cursor): 15 min
- Review: 25 min
- **Total: ~2 hours**

**Savings: 50%+**

---

## 🎓 Key Learnings

1. **Tool Selection Matters**: Claude for architecture, Copilot for implementation, Cursor for quick edits
2. **Provide Context**: The better your prompt, the better the result
3. **Iterate**: First generation rarely perfect
4. **Always Review**: AI can miss security issues
5. **Test Everything**: AI-generated code needs testing just like human code

---

## 🚀 Next Steps

- Apply this workflow to your own features
- Adapt prompts to your codebase
- Measure your time savings
- Share with your team

---

**Remember**: AI is a tool, not a replacement. You're still the architect, reviewer, and decision-maker.
