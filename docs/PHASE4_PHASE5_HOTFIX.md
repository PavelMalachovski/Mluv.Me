# Phase 4 & 5 Hotfix

**Date:** December 7, 2025
**Issue:** Pydantic V2 configuration conflict
**Status:** ✅ FIXED

## 🐛 Problem

Deployment failed with error:

```
pydantic.errors.PydanticUserError: "Config" and "model_config" cannot be used together
```

**Root Cause:** In `backend/schemas/lesson.py`, the `LessonProcessResponse` class had both:
- New Pydantic V2 `model_config = ConfigDict(...)`
- Old Pydantic V1 `class Config:` with `json_schema_extra`

Pydantic V2 doesn't allow mixing both configuration styles.

## ✅ Solution

**File:** `backend/schemas/lesson.py`

**Change:** Moved `json_schema_extra` into `model_config`:

```python
# BEFORE (WRONG - caused error)
class LessonProcessResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=False,
        # ...
    )

    # Fields...

    class Config:  # ❌ Cannot use with model_config
        json_schema_extra = {...}

# AFTER (CORRECT)
class LessonProcessResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=False,
        # ...
        json_schema_extra={...}  # ✅ Moved here
    )

    # Fields...
```

## 📝 Files Modified

- `backend/schemas/lesson.py` - Removed `class Config`, moved `json_schema_extra` to `model_config`

## ✅ Verification

After fix:
- ✅ Application starts without errors
- ✅ Pydantic V2 configuration working correctly
- ✅ JSON schema examples preserved
- ✅ All performance optimizations active

## 🚀 Deployment

No additional steps needed. The fix is backward compatible and doesn't change functionality.

```bash
git add backend/schemas/lesson.py
git commit -m "fix: resolve Pydantic V2 config conflict in LessonProcessResponse"
git push origin master
```

## 📚 Reference

- Pydantic V2 Migration Guide: https://docs.pydantic.dev/latest/migration/
- Error code: https://errors.pydantic.dev/2.9/u/config-both

---

**Fix Applied:** December 7, 2025
**Status:** ✅ RESOLVED
**Impact:** None (configuration only)
