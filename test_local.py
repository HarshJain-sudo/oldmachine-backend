#!/usr/bin/env python3
"""
Local testing script for OldMachine Backend APIs.

This script tests all API endpoints locally.

Usage:
    python test_local.py
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://oldmachine-backend.vercel.app/api/marketplace"
HEADERS = {"Content-Type": "application/json"}

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def print_section(title: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def pretty_print_json(data: Dict[Any, Any]):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_server_connection() -> bool:
    """Test if server is running."""
    try:
        response = requests.get(f"{BASE_URL.replace('/api/marketplace', '')}/admin/", timeout=5)
        return True
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Make sure the server is running:")
        print_info("Run: python manage.py runserver")
        return False
    except Exception as e:
        print_error(f"Error connecting to server: {e}")
        return False


def test_login_or_signup(phone_number: str = "9876543210", country_code: str = "+91") -> Optional[str]:
    """Test login or sign up API."""
    print_section("1. Testing Login/Sign Up API")
    
    url = f"{BASE_URL}/login_or_sign_up/v1/"
    payload = {
        "phone_number": phone_number,
        "country_code": country_code
    }
    
    print_info(f"POST {url}")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login/Sign Up successful!")
            pretty_print_json(data)
            
            user_id = data.get('user_id')
            if user_id:
                print_success(f"User ID: {user_id}")
                print_warning("Check server console logs for OTP code (in beta environment)")
                return user_id
            return None
        else:
            print_error(f"Login/Sign Up failed!")
            pretty_print_json(response.json())
            return None
            
    except Exception as e:
        print_error(f"Error: {e}")
        return None


def test_verify_otp(phone_number: str = "9876543210", otp: str = None) -> Optional[Dict[str, str]]:
    """Test verify OTP API."""
    print_section("2. Testing Verify OTP API")
    
    if not otp:
        print_warning("OTP not provided. Please enter OTP from server logs:")
        otp = input("Enter OTP: ").strip()
        if not otp:
            print_error("OTP is required")
            return None
    
    url = f"{BASE_URL}/verify_otp/v1/"
    payload = {
        "phone_number": phone_number,
        "otp": otp
    }
    
    print_info(f"POST {url}")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("OTP verification successful!")
            pretty_print_json(data)
            
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            
            if access_token and refresh_token:
                print_success(f"Access Token: {access_token[:20]}...")
                print_success(f"Refresh Token: {refresh_token[:20]}...")
                return data
            return None
        else:
            print_error("OTP verification failed!")
            pretty_print_json(response.json())
            return None
            
    except Exception as e:
        print_error(f"Error: {e}")
        return None


def test_get_categories(limit: int = 10, offset: int = 0) -> bool:
    """Test get categories API."""
    print_section("3. Testing Get Categories API")
    
    url = f"{BASE_URL}/categories_details/get/v1/?limit={limit}&offset={offset}"
    
    print_info(f"GET {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Get Categories successful!")
            
            categories = data.get('categories_details', [])
            print_info(f"Found {len(categories)} categories")
            
            if categories:
                pretty_print_json(data)
            else:
                print_warning("No categories found. Create some categories in admin panel.")
            
            return True
        else:
            print_error("Get Categories failed!")
            pretty_print_json(response.json())
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_get_category_products(category_code: str = "ELEC001", limit: int = 10, offset: int = 0) -> bool:
    """Test get category products API."""
    print_section("4. Testing Get Category Products API")
    
    url = f"{BASE_URL}/category_products_details/get/v1/?category_code={category_code}&limit={limit}&offset={offset}"
    
    print_info(f"GET {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Get Category Products successful!")
            
            products = data.get('products_details', [])
            total_count = data.get('total_count', '0')
            
            print_info(f"Found {len(products)} products (Total: {total_count})")
            
            if products:
                pretty_print_json(data)
            else:
                print_warning(f"No products found for category '{category_code}'")
            
            return True
        else:
            print_error("Get Category Products failed!")
            pretty_print_json(response.json())
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_get_product_details(product_code: str = "PROD001") -> bool:
    """Test get product details API."""
    print_section("5. Testing Get Product Details API")
    
    url = f"{BASE_URL}/product_details/get/v1/{product_code}/"
    
    print_info(f"GET {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Get Product Details successful!")
            pretty_print_json(data)
            return True
        elif response.status_code == 404:
            print_error(f"Product '{product_code}' not found!")
            pretty_print_json(response.json())
            return False
        else:
            print_error("Get Product Details failed!")
            pretty_print_json(response.json())
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_error_cases():
    """Test error handling."""
    print_section("6. Testing Error Cases")
    
    # Test invalid phone number
    print_info("Testing invalid phone number...")
    url = f"{BASE_URL}/login_or_sign_up/v1/"
    payload = {"phone_number": "123", "country_code": "+91"}
    response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
    if response.status_code == 400:
        print_success("Invalid phone number handled correctly")
    else:
        print_error("Invalid phone number not handled correctly")
    
    # Test invalid category code
    print_info("Testing invalid category code...")
    url = f"{BASE_URL}/category_products_details/get/v1/?category_code=INVALID"
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code == 400:
        print_success("Invalid category code handled correctly")
    else:
        print_error("Invalid category code not handled correctly")
    
    # Test product not found
    print_info("Testing product not found...")
    url = f"{BASE_URL}/product_details/get/v1/INVALID123/"
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code == 404:
        print_success("Product not found handled correctly")
    else:
        print_error("Product not found not handled correctly")


def main():
    """Main test function."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("  OldMachine Backend - Local API Testing")
    print("=" * 60)
    print(f"{Colors.RESET}\n")
    
    # Test server connection
    if not test_server_connection():
        sys.exit(1)
    
    print_success("Server is running!")
    
    # Test all APIs
    results = {
        "login_signup": False,
        "verify_otp": False,
        "get_categories": False,
        "get_category_products": False,
        "get_product_details": False,
    }
    
    # 1. Test Login/Sign Up
    user_id = test_login_or_signup()
    results["login_signup"] = user_id is not None
    
    # 2. Test Verify OTP (optional - requires OTP from logs)
    print_info("\nSkipping OTP verification (requires OTP from server logs)")
    print_info("To test OTP verification, uncomment the line below and provide OTP")
    # tokens = test_verify_otp()
    # results["verify_otp"] = tokens is not None
    
    # 3. Test Get Categories
    results["get_categories"] = test_get_categories()
    
    # 4. Test Get Category Products
    results["get_category_products"] = test_get_category_products()
    
    # 5. Test Get Product Details
    results["get_product_details"] = test_get_product_details()
    
    # 6. Test Error Cases
    test_error_cases()
    
    # Summary
    print_section("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Total: {passed_tests}/{total_tests} tests passed{Colors.RESET}\n")
    
    if passed_tests == total_tests:
        print_success("All tests passed! 🎉")
    else:
        print_warning("Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Testing interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

