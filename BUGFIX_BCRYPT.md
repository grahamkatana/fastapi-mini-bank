# 🐛 BUGFIX: Bcrypt Compatibility Issue (SOLVED)

## The Problem

You encountered this error when running tests:

```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
AttributeError: module 'bcrypt' has no attribute '__about__'
```

## Root Cause

**Bcrypt 4.0+ is incompatible with passlib 1.7.4**

This is a known issue with Python 3.12. The newer bcrypt library (4.x) changed its API structure, and passlib hasn't been updated to support it yet.

## The Fix ✅

I've fixed this by pinning bcrypt to version 3.2.2 in `requirements.txt`:

```txt
bcrypt==3.2.2
```

## How to Apply the Fix

### Option 1: Reinstall Dependencies (Recommended)

```bash
# Remove existing virtual environment
rm -rf venv

# Create new virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with fixed dependencies
pip install -r requirements.txt

# Run tests
pytest
```

### Option 2: Just Reinstall bcrypt

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Uninstall current bcrypt
pip uninstall bcrypt -y

# Install compatible version
pip install bcrypt==3.2.2

# Run tests
pytest
```

## Additional Fixes Applied

I also fixed some deprecation warnings:

### 1. SQLAlchemy 2.0 Warning
**Before:**
```python
from sqlalchemy.ext.declarative import declarative_base
```

**After:**
```python
from sqlalchemy.orm import declarative_base
```

### 2. Pydantic v2 Warning
**Before:**
```python
class UserResponse(BaseModel):
    class Config:
        from_attributes = True
```

**After:**
```python
from pydantic import ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

## Verification

After applying the fix, run:

```bash
# Run all tests
pytest -v

# Should see something like:
# ======================== 50 passed in 3.45s ========================
```

## Why This Happened

When you ran `pip install -r requirements.txt`, pip installed the **latest** version of bcrypt (4.1.2 at the time), which is incompatible with passlib 1.7.4.

By pinning `bcrypt==3.2.2`, we ensure everyone gets a compatible version.

## Alternative Solutions (Not Recommended)

### Option A: Use bcrypt directly (without passlib)

Update `app/core/security.py`:
```python
import bcrypt

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

### Option B: Wait for passlib update

Watch: https://github.com/pyca/bcrypt/issues/684

But Option A requires code changes, and Option B... well, you'd be waiting a while.

## Future-Proofing

In the future, always pin your dependencies:

```txt
# ❌ Bad (gets latest, might break)
bcrypt

# ✅ Good (specific version)
bcrypt==3.2.2

# ✅ Also good (allows patches but not breaking changes)
bcrypt>=3.2.0,<4.0.0
```

## Summary

✅ **Fixed:** bcrypt downgraded to 3.2.2  
✅ **Fixed:** SQLAlchemy deprecation warning  
✅ **Fixed:** Pydantic v2 warnings  
✅ **Result:** All tests should now pass!  

## Quick Commands

```bash
# Clean install
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Should see: ✅ All tests passing!
```

---

**Issue Resolved!** The updated `requirements.txt` in your download now has the fix. 🎉
