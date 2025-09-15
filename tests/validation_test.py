#!/usr/bin/env python3
"""
Detailed Test Runner for Validation Tests
Shows input data, expected results, and actual results for each test
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from transform import validate_row

def run_detailed_tests():
    print("=" * 80)
    print("DETAILED VALIDATION TEST RESULTS")
    print("=" * 80)
    
    # Test cases with detailed information
    test_cases = [
        {
            "name": "Valid Data Test",
            "description": "Test with valid data - should return True",
            "data": {"Name": "John Doe", "Age": "25", "Banner_id": "15", "Cookie": "abc123-def456-ghi789"},
            "expected": True
        },
        {
            "name": "Empty Name Test",
            "description": "Test with empty name - should return False",
            "data": {"Name": "", "Age": "25", "Banner_id": "15", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        },
        {
            "name": "Negative Age Test",
            "description": "Test with negative age - should return False",
            "data": {"Name": "John Doe", "Age": "-5", "Banner_id": "15", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        },
        {
            "name": "Zero Age Test",
            "description": "Test with zero age - should return False",
            "data": {"Name": "John Doe", "Age": "0", "Banner_id": "15", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        },
        {
            "name": "Banner ID Too High Test",
            "description": "Test with banner ID > 99 - should return False",
            "data": {"Name": "John Doe", "Age": "25", "Banner_id": "100", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        },
        {
            "name": "Negative Banner ID Test",
            "description": "Test with negative banner ID - should return False",
            "data": {"Name": "John Doe", "Age": "25", "Banner_id": "-1", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        },
        {
            "name": "Empty Cookie Test",
            "description": "Test with empty cookie - should return False",
            "data": {"Name": "John Doe", "Age": "25", "Banner_id": "15", "Cookie": ""},
            "expected": False
        },
        {
            "name": "Name with Numbers Test",
            "description": "Test with name containing numbers - should return False",
            "data": {"Name": "John123 Doe", "Age": "25", "Banner_id": "15", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        },
        {
            "name": "Name with Special Characters Test",
            "description": "Test with name containing special characters - should return False",
            "data": {"Name": "John@Doe", "Age": "25", "Banner_id": "15", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        },
        {
            "name": "Missing Fields Test",
            "description": "Test with missing fields - should return False",
            "data": {"Name": "John Doe", "Age": "25"},  # Missing Banner_id and Cookie
            "expected": False
        },
        {
            "name": "Non-numeric Age Test",
            "description": "Test with non-numeric age - should return False",
            "data": {"Name": "John Doe", "Age": "twenty-five", "Banner_id": "15", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        },
        {
            "name": "Non-numeric Banner ID Test",
            "description": "Test with non-numeric banner ID - should return False",
            "data": {"Name": "John Doe", "Age": "25", "Banner_id": "fifteen", "Cookie": "abc123-def456-ghi789"},
            "expected": False
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i:2d}. {test_case['name']}")
        print(f"    Description: {test_case['description']}")
        print(f"    Input Data: {test_case['data']}")
        print(f"    Expected: {test_case['expected']}")
        
        # Run the test
        try:
            actual = validate_row(test_case['data'])
            print(f"    Actual:   {actual}")
            
            if actual == test_case['expected']:
                print(f"    Result:   PASS")
                passed += 1
            else:
                print(f"    Result:   FAIL")
                failed += 1
                
        except Exception as e:
            print(f"    Result:   ERROR: {e}")
            failed += 1
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
    
    if failed == 0:
        print(f"\nALL TESTS PASSED!")
    else:
        print(f"\n  {failed} test(s) failed!")

if __name__ == "__main__":
    run_detailed_tests()
