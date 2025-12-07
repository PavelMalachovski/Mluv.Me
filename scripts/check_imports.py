#!/usr/bin/env python
"""
Quick script to check if all imports work correctly.
Used for validation before deployment.
"""

import sys

def check_imports():
    """Check all critical imports."""
    errors = []

    try:
        print("Checking backend.config...")
        from backend.config import Settings
        print("✅ backend.config OK")
    except Exception as e:
        errors.append(f"❌ backend.config: {e}")

    try:
        print("Checking backend.schemas.lesson...")
        from backend.schemas.lesson import LessonProcessResponse
        print("✅ backend.schemas.lesson OK")
    except Exception as e:
        errors.append(f"❌ backend.schemas.lesson: {e}")

    try:
        print("Checking backend.schemas.user...")
        from backend.schemas.user import UserResponse
        print("✅ backend.schemas.user OK")
    except Exception as e:
        errors.append(f"❌ backend.schemas.user: {e}")

    try:
        print("Checking backend.services.openai_client...")
        from backend.services.openai_client import OpenAIClient
        print("✅ backend.services.openai_client OK")
    except Exception as e:
        errors.append(f"❌ backend.services.openai_client: {e}")

    try:
        print("Checking backend.services.honzik_personality...")
        from backend.services.honzik_personality import HonzikPersonality
        print("✅ backend.services.honzik_personality OK")
    except Exception as e:
        errors.append(f"❌ backend.services.honzik_personality: {e}")

    try:
        print("Checking backend.routers.lesson...")
        from backend.routers.lesson import router
        print("✅ backend.routers.lesson OK")
    except Exception as e:
        errors.append(f"❌ backend.routers.lesson: {e}")

    if errors:
        print("\n" + "="*50)
        print("ERRORS FOUND:")
        for error in errors:
            print(error)
        return 1
    else:
        print("\n" + "="*50)
        print("✅ ALL IMPORTS SUCCESSFUL!")
        return 0

if __name__ == "__main__":
    sys.exit(check_imports())
