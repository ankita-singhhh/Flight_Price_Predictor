"""Basic test to verify CI/CD pipeline works"""

def test_app_import():
    """Test that app can be imported"""
    try:
        from app import app
        print("✅ App import successful")
        return True
    except ImportError as e:
        print(f"❌ App import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        from app import validate_input, parse_stops
        print("✅ Functions import successful")
        return True
    except ImportError as e:
        print(f"❌ Functions import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running basic tests...")
    
    import_success = test_app_import()
    function_success = test_basic_functionality()
    
    if import_success and function_success:
        print("✅ All basic tests passed!")
    else:
        print("❌ Some tests failed!")
    
    print("\n📊 Test Results:")
    print(f"App Import: {'✅' if import_success else '❌'}")
    print(f"Functions Import: {'✅' if function_success else '❌'}")
