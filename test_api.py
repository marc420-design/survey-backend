"""
Test script to verify the Survey API is working correctly
"""

import requests
import json
import time

API_URL = "http://127.0.0.1:8080"

def test_root():
    """Test the root endpoint"""
    print("Testing GET / ...")
    response = requests.get(f"{API_URL}/")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_health():
    """Test the health endpoint"""
    print("\nTesting GET /health ...")
    response = requests.get(f"{API_URL}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_submit_valid():
    """Test submitting a valid survey"""
    print("\nTesting POST /submit with valid data ...")

    data = {
        "eventTypes": ["Drum & Bass", "House/Techno"],
        "frequency": "Weekly",
        "toiletImportance": "Very important",
        "seatingImportance": "Nice to have",
        "fastEntryImportance": "Very important",
        "securityImportance": "Very important",
        "barPriorities": ["Fast service", "Cheap drink deals"],
        "idealPrices": {
            "singleSpiritMixer": 6,
            "doubleSpiritMixer": 8,
            "pint": 5,
            "bottleCan": 4
        },
        "soundSystemQuality": 5,
        "lightingLasers": 4,
        "stageVisualsScreens": 3,
        "smokeHazeEffects": 4,
        "roomAtmosphere": 5,
        "goodSoundSystemFeatures": ["Heavy bass", "No distortion"],
        "djValues": ["Track selection/energy", "Proper mixing/flow"],
        "genresMoreOf": "More Jungle and UK Garage events please!",
        "respectfulCrowd": 5,
        "cleanEnvironment": 5,
        "temperatureVentilation": 4,
        "zeroDramaAtmosphere": 5,
        "feelingSafe": "Yes",
        "averageEventPrice": "£10–£15",
        "premiumEventPrice": "£20–£25",
        "addOns": ["Free cloakroom", "Drink token(s)"],
        "clubsNeverGetRight": "Queue times and ventilation",
        "clubsDoMore": "Better sound systems and longer sets",
        "loyalAttendee": "Yes",
        "email": f"test{int(time.time())}@example.com"  # Unique email
    }

    response = requests.post(
        f"{API_URL}/submit",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_submit_duplicate_email():
    """Test submitting with duplicate email"""
    print("\nTesting POST /submit with duplicate email ...")

    email = "duplicate@example.com"

    data = {
        "eventTypes": ["Drum & Bass"],
        "frequency": "Weekly",
        "toiletImportance": "Very important",
        "barPriorities": ["Fast service"],
        "idealPrices": {"singleSpiritMixer": 6},
        "goodSoundSystemFeatures": ["Heavy bass"],
        "djValues": ["Big headliners"],
        "genresMoreOf": "Test",
        "clubsNeverGetRight": "Test",
        "clubsDoMore": "Test",
        "addOns": [],
        "email": email
    }

    # First submission
    response1 = requests.post(f"{API_URL}/submit", json=data)
    print(f"  First submission status: {response1.status_code}")

    # Second submission with same email
    response2 = requests.post(f"{API_URL}/submit", json=data)
    print(f"  Second submission status: {response2.status_code}")

    if response2.status_code == 400:
        print(f"  Error message: {response2.json()['detail']}")
        return True
    return False

def test_rate_limiting():
    """Test rate limiting"""
    print("\nTesting rate limiting (5 requests/minute) ...")

    data = {
        "eventTypes": ["Drum & Bass"],
        "frequency": "Weekly",
        "toiletImportance": "Very important",
        "barPriorities": ["Fast service"],
        "idealPrices": {"singleSpiritMixer": 6},
        "goodSoundSystemFeatures": ["Heavy bass"],
        "djValues": ["Big headliners"],
        "genresMoreOf": "Test",
        "clubsNeverGetRight": "Test",
        "clubsDoMore": "Test",
        "addOns": [],
        "email": None  # No email to avoid duplicate errors
    }

    success_count = 0
    rate_limited = False

    for i in range(7):
        # Use unique email for each
        data["email"] = f"ratelimit{int(time.time())}_{i}@example.com"
        response = requests.post(f"{API_URL}/submit", json=data)

        if response.status_code == 200:
            success_count += 1
            print(f"  Request {i+1}: Success")
        elif response.status_code == 429:
            rate_limited = True
            print(f"  Request {i+1}: Rate limited (429)")
            break
        else:
            print(f"  Request {i+1}: Unexpected status {response.status_code}")

        time.sleep(0.5)  # Small delay between requests

    print(f"  Successfully submitted {success_count} surveys before rate limit")
    return rate_limited

def test_input_validation():
    """Test input validation"""
    print("\nTesting input validation (oversized field) ...")

    data = {
        "eventTypes": ["Drum & Bass"],
        "frequency": "Weekly",
        "toiletImportance": "Very important",
        "barPriorities": ["Fast service"],
        "idealPrices": {"singleSpiritMixer": 6},
        "goodSoundSystemFeatures": ["Heavy bass"],
        "djValues": ["Big headliners"],
        "genresMoreOf": "A" * 1001,  # Exceeds max length
        "clubsNeverGetRight": "Test",
        "clubsDoMore": "Test",
        "addOns": [],
    }

    response = requests.post(f"{API_URL}/submit", json=data)
    print(f"  Status: {response.status_code}")

    if response.status_code == 422:
        print(f"  Validation error (as expected)")
        return True
    return False

def main():
    print("=" * 70)
    print("Survey API Integration Tests")
    print("=" * 70)

    tests = [
        ("Root Endpoint", test_root),
        ("Health Check", test_health),
        ("Valid Submission", test_submit_valid),
        ("Duplicate Email", test_submit_duplicate_email),
        ("Input Validation", test_input_validation),
        ("Rate Limiting", test_rate_limiting),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"[PASS] {name}\n")
            else:
                failed += 1
                print(f"[FAIL] {name}\n")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {name}: {e}\n")

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n[SUCCESS] All tests passed! API is working correctly.")
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Check the output above.")

if __name__ == "__main__":
    main()
