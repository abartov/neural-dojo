# Workflow 04: Large-Scale Refactoring with AI

**Scenario**: Refactor monolithic `user_service.py` (800 lines) into modular components

**Duration**: ~90 minutes (vs ~4-5 hours without AI)

**Tools Used**:
- Claude Code (planning and multi-file refactoring)
- GitHub Copilot (boilerplate and tests)
- VSCode (free IDE)

---

## 🎯 Goal

**Current State**: One massive file
```
src/services/user_service.py (800 lines)
- User CRUD
- Authentication
- Profile management
- Notifications
- Analytics
- Password reset
- Email verification
```

**Target State**: Modular structure
```
src/users/
├── __init__.py
├── crud.py           # CRUD operations
├── auth.py           # Authentication
├── profile.py        # Profile management
├── notifications.py  # User notifications
├── analytics.py      # User analytics
└── verification.py   # Email/password flows
```

---

## 📋 Step 1: Plan the Refactor (Claude Code)

### Prompt

```
I have a monolithic user service file (800 lines) that needs refactoring.

**Current file structure**:
[paste the file or key sections]

**Problems**:
- Too large (800 lines)
- Mixed concerns (CRUD, auth, notifications, etc.)
- Hard to test
- Merge conflicts frequent

**Goal**:
- Split into logical modules
- Maintain backward compatibility
- Don't break existing imports
- Easier to test each module

Please suggest:
1. How to split this into modules
2. File structure
3. Step-by-step refactoring plan (safe incremental approach)
4. How to handle imports and backward compatibility
```

### Claude's Plan Example

```
## Refactoring Plan

### Phase 1: Create New Structure (No Breaking Changes)

1. Create new directory structure
2. Extract functions to new modules
3. Keep original file as facade (re-exports everything)
4. Update tests gradually
5. Remove facade once migration complete

### File Structure:

```
src/users/
├── __init__.py          # Re-export everything (backward compat)
├── crud.py              # get_user, create_user, update_user, delete_user
├── auth.py              # login, logout, verify_token, change_password
├── profile.py           # get_profile, update_profile, upload_avatar
├── notifications.py     # notify_user, get_notifications, mark_read
├── analytics.py         # track_login, get_user_stats
└── verification.py      # send_verification, verify_email, reset_password
```

### Step-by-Step Process:

#### Step 1: Create Directory and __init__.py
```python
# src/users/__init__.py
"""
User management module.
Re-exports all functions for backward compatibility.
"""
# Will import from submodules once created
```

#### Step 2: Extract CRUD Functions
Move these functions to `crud.py`:
- `get_user_by_id()`
- `get_user_by_email()`
- `create_user()`
- `update_user()`
- `delete_user()`

```python
# src/users/crud.py
from sqlalchemy.orm import Session
from src.models import User

def get_user_by_id(db: Session, user_id: int) -> User | None:
    # Move implementation here
    ...
```

#### Step 3: Update __init__.py
```python
# src/users/__init__.py
from .crud import get_user_by_id, get_user_by_email, create_user, update_user, delete_user

# Re-export for backward compatibility
__all__ = [
    "get_user_by_id",
    "get_user_by_email",
    "create_user",
    "update_user",
    "delete_user",
]
```

#### Step 4: Update Imports in Old File
```python
# src/services/user_service.py (now a facade)
from src.users import (
    get_user_by_id,
    get_user_by_email,
    create_user,
    update_user,
    delete_user,
)

# Re-export for backward compatibility (old imports still work)
__all__ = [...]
```

#### Step 5: Repeat for Other Modules
Extract auth functions, profile functions, etc. one module at a time.

#### Step 6: Update Tests
Create focused test files for each module:
- `tests/users/test_crud.py`
- `tests/users/test_auth.py`
- etc.

#### Step 7: Deprecate Old File
After all imports updated:
```python
# src/services/user_service.py
import warnings
from src.users import *

warnings.warn(
    "user_service.py is deprecated. Import from src.users instead",
    DeprecationWarning,
    stacklevel=2
)
```

#### Step 8: Remove Old File
After deprecation period (e.g., 1 release cycle), delete the facade.
```

---

## 📋 Step 2: Execute Refactor (Claude Code)

### Prompt for Each Module

```
Extract the CRUD functions from user_service.py to a new crud.py module.

**Functions to extract**:
- get_user_by_id
- get_user_by_email
- create_user
- update_user
- delete_user

**Requirements**:
- Keep function signatures identical
- Move imports needed by these functions
- Add type hints if missing
- Add docstrings if missing

Here's the current code:
[paste the relevant functions]
```

Claude will:
1. Create the new file with proper imports
2. Add type hints
3. Add docstrings
4. Preserve exact functionality

---

## 📋 Step 3: Write Tests for New Modules (Copilot in VSCode)

Open `tests/users/test_crud.py` in VSCode:

```python
import pytest
from sqlalchemy.orm import Session
from src.users import crud
from src.models import User

# Type: def test_get_user_by_id_success():
# Copilot suggests:

def test_get_user_by_id_success(db_session: Session):
    """Test getting user by ID when user exists."""
    # Arrange
    user = User(id=1, email="test@example.com")
    db_session.add(user)
    db_session.commit()

    # Act
    result = crud.get_user_by_id(db_session, 1)

    # Assert
    assert result is not None
    assert result.id == 1
    assert result.email == "test@example.com"

# Type: def test_get_user_by_id_not_found():
# Copilot follows the pattern:

def test_get_user_by_id_not_found(db_session: Session):
    """Test getting user by ID when user doesn't exist."""
    result = crud.get_user_by_id(db_session, 999)
    assert result is None

# Copilot will suggest 10+ more tests!
```

---

## 📋 Step 4: Update Imports Across Codebase (VSCode Find & Replace)

Use VSCode's powerful find and replace:

**Find**:
```
from src.services.user_service import get_user_by_id
```

**Replace**:
```
from src.users import get_user_by_id
```

Use "Replace All" or review each one.

**Pro tip**: Use regex for bulk changes:

**Find** (regex):
```
from src\.services\.user_service import (.+)
```

**Replace**:
```
from src.users import $1
```

---

## 📋 Step 5: Verify Nothing Broke

```bash
# Run all tests
pytest

# If any fail, investigate:
pytest -v --tb=short

# Check imports
python -m src.users  # Should import without errors

# Check linting
flake8 src/users/
mypy src/users/
```

---

## ✅ Refactoring Checklist

### Preparation
- [ ] Create backup branch
- [ ] Run all tests (baseline)
- [ ] Document current import patterns
- [ ] Plan module structure with AI

### Execution
- [ ] Create new directory structure
- [ ] Extract first module (e.g., CRUD)
- [ ] Update __init__.py for re-exports
- [ ] Write tests for new module
- [ ] Repeat for each module
- [ ] Update imports across codebase

### Verification
- [ ] All tests pass
- [ ] No import errors
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Code review by team

### Cleanup
- [ ] Add deprecation warning to old file
- [ ] Update documentation
- [ ] Wait one release cycle
- [ ] Remove old file

---

## 📊 Benefits of AI-Assisted Refactoring

**Without AI**:
- Manual code extraction (error-prone)
- Manually track all imports
- Write all tests from scratch
- **Risk**: High (easy to miss something)
- **Time**: 4-5 hours

**With AI**:
- AI extracts code (preserves functionality)
- AI suggests test cases
- Find/replace handles imports
- **Risk**: Lower (systematic approach)
- **Time**: ~90 minutes

---

## 🎓 Key Learnings

1. **Incremental is Safer**: Refactor one module at a time
2. **Backward Compatibility**: Use facade pattern during transition
3. **Test Everything**: Write tests for new modules before removing old code
4. **AI Helps Structure**: Great at suggesting module boundaries
5. **Humans Verify**: AI can miss subtle dependencies

---

## 💡 Advanced: Automated Refactoring Script

```bash
#!/bin/bash
# refactor-module.sh
#
# Automates extraction of a module with AI assistance

MODULE_NAME=$1
FUNCTIONS=$2

echo "Extracting $MODULE_NAME module..."

# 1. Create new file
mkdir -p src/users
touch src/users/${MODULE_NAME}.py

# 2. Use AI to extract functions
cat > /tmp/refactor_prompt.txt << EOF
Extract these functions from src/services/user_service.py to src/users/${MODULE_NAME}.py:
$FUNCTIONS

Preserve exact functionality, add type hints and docstrings.

Source file:
$(cat src/services/user_service.py)
EOF

# Call AI (example with Claude)
# ... (AI generates the new module)

# 3. Run tests
pytest tests/users/test_${MODULE_NAME}.py

# 4. Update imports
# ... (find and replace)

echo "Refactoring complete! Review changes and commit."
```

Usage:
```bash
./refactor-module.sh crud "get_user_by_id,create_user,update_user"
```

---

**Remember**: Refactoring is about improving structure without changing behavior. AI helps with the mechanical work, you provide the architectural vision.
