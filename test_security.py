"""
Quick security tests for the Survey API
Run with: python test_security.py
"""

import sys
import os

# Set UTF-8 encoding for console output
if os.name == 'nt':  # Windows
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')

from main import app, SurveyResponse, IdealPrices
from pydantic import ValidationError

def test_input_validation():
    """Test that input validation works"""
    print("Testing input validation...")

    # Test oversized text field
    try:
        data = {
            "eventTypes": ["Drum & Bass"],
            "frequency": "Weekly",
            "toiletImportance": "Very important",
            "barPriorities": ["Fast service"],
            "idealPrices": {"singleSpiritMixer": 5},
            "goodSoundSystemFeatures": ["Heavy bass"],
            "djValues": ["Big headliners"],
            "genresMoreOf": "A" * 1001,  # Exceeds max length of 1000
            "clubsNeverGetRight": "Test",
            "clubsDoMore": "Test",
            "addOns": [],
        }
        SurveyResponse(**data)
        print("[FAIL] Should have rejected oversized field")
        return False
    except ValidationError as e:
        print("[PASS] Oversized field rejected")

    # Test invalid rating value
    try:
        data = {
            "eventTypes": ["Drum & Bass"],
            "frequency": "Weekly",
            "toiletImportance": "Very important",
            "barPriorities": ["Fast service"],
            "idealPrices": {"singleSpiritMixer": 5},
            "soundSystemQuality": 10,  # Exceeds max of 5
            "goodSoundSystemFeatures": ["Heavy bass"],
            "djValues": ["Big headliners"],
            "genresMoreOf": "Test",
            "clubsNeverGetRight": "Test",
            "clubsDoMore": "Test",
            "addOns": [],
        }
        SurveyResponse(**data)
        print("[FAIL] Should have rejected invalid rating")
        return False
    except ValidationError as e:
        print("[PASS] Invalid rating rejected")

    # Test valid data
    try:
        data = {
            "eventTypes": ["Drum & Bass"],
            "frequency": "Weekly",
            "toiletImportance": "Very important",
            "barPriorities": ["Fast service"],
            "idealPrices": {"singleSpiritMixer": 5},
            "soundSystemQuality": 5,
            "goodSoundSystemFeatures": ["Heavy bass"],
            "djValues": ["Big headliners"],
            "genresMoreOf": "Jungle, UK Garage",
            "clubsNeverGetRight": "Queue times",
            "clubsDoMore": "Better ventilation",
            "addOns": [],
        }
        SurveyResponse(**data)
        print("[PASS] Valid data accepted")
    except ValidationError as e:
        print(f"[FAIL] Valid data rejected: {e}")
        return False

    return True

def test_middleware_loaded():
    """Test that middleware is loaded"""
    print("\nTesting middleware configuration...")

    # Check CORS middleware
    cors_found = False
    security_found = False

    for middleware in app.user_middleware:
        if 'CORSMiddleware' in str(middleware):
            cors_found = True
        if 'SecurityHeadersMiddleware' in str(middleware):
            security_found = True

    if cors_found:
        print("[PASS] CORS middleware loaded")
    else:
        print("[FAIL] CORS middleware not found")

    if security_found:
        print("[PASS] Security headers middleware loaded")
    else:
        print("[FAIL] Security headers middleware not found")

    return cors_found and security_found

def test_rate_limiter():
    """Test that rate limiter is configured"""
    print("\nTesting rate limiter configuration...")

    if hasattr(app.state, 'limiter'):
        print("[PASS] Rate limiter configured")
        return True
    else:
        print("[FAIL] Rate limiter not found")
        return False

def main():
    print("=" * 60)
    print("Security Features Test Suite")
    print("=" * 60)

    tests_passed = 0
    tests_total = 3

    if test_input_validation():
        tests_passed += 1

    if test_middleware_loaded():
        tests_passed += 1

    if test_rate_limiter():
        tests_passed += 1

    print("\n" + "=" * 60)
    print(f"Results: {tests_passed}/{tests_total} test groups passed")
    print("=" * 60)

    if tests_passed == tests_total:
        print("\n[SUCCESS] All security features are working correctly!")
        return 0
    else:
        print(f"\n[ERROR] {tests_total - tests_passed} test group(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
