"""
Comprehensive test for password reset token security.
"""
from datetime import datetime


class MockUser:
    """Mock user object for testing."""
    def __init__(self, pk, email, password, last_login=None):
        self.pk = pk
        self.email = email
        self.password = password
        self.last_login = last_login


class MockUserNoEmail:
    """Mock user without email field (as per AbstractBaseUser)."""
    def __init__(self, pk, password, last_login=None):
        self.pk = pk
        self.password = password
        self.last_login = last_login


def test_email_change_invalidates_token():
    """Test that changing email invalidates the token."""
    from django.contrib.auth.tokens import default_token_generator
    
    user = MockUser(
        pk=1,
        email='foo@example.com',
        password='hashed_password_123',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    token = default_token_generator.make_token(user)
    assert default_token_generator.check_token(user, token), "Token should be valid initially"
    
    user.email = 'bar@example.com'
    assert not default_token_generator.check_token(user, token), "Token should be invalid after email change"
    
    print("✅ Test 1 passed: Email change invalidates token")
    return True


def test_password_change_invalidates_token():
    """Test that changing password invalidates the token."""
    from django.contrib.auth.tokens import default_token_generator
    
    user = MockUser(
        pk=2,
        email='test@example.com',
        password='hashed_password_123',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    token = default_token_generator.make_token(user)
    assert default_token_generator.check_token(user, token), "Token should be valid initially"
    
    user.password = 'new_hashed_password_456'
    assert not default_token_generator.check_token(user, token), "Token should be invalid after password change"
    
    print("✅ Test 2 passed: Password change invalidates token")
    return True


def test_user_without_email():
    """Test that users without email field still work (AbstractBaseUser compatibility)."""
    from django.contrib.auth.tokens import default_token_generator
    
    user = MockUserNoEmail(
        pk=3,
        password='hashed_password_789',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    token = default_token_generator.make_token(user)
    assert default_token_generator.check_token(user, token), "Token should be valid for user without email"
    
    user.password = 'new_hashed_password_abc'
    assert not default_token_generator.check_token(user, token), "Token should be invalid after password change"
    
    print("✅ Test 3 passed: Users without email field work correctly")
    return True


def test_same_email_keeps_token_valid():
    """Test that keeping the same email doesn't invalidate the token."""
    from django.contrib.auth.tokens import default_token_generator
    
    user = MockUser(
        pk=4,
        email='stable@example.com',
        password='hashed_password_xyz',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    token = default_token_generator.make_token(user)
    assert default_token_generator.check_token(user, token), "Token should be valid initially"
    
    # Email stays the same
    user.email = 'stable@example.com'
    assert default_token_generator.check_token(user, token), "Token should still be valid with same email"
    
    print("✅ Test 4 passed: Same email keeps token valid")
    return True


def test_multiple_users_different_tokens():
    """Test that different users get different tokens."""
    from django.contrib.auth.tokens import default_token_generator
    
    user1 = MockUser(
        pk=5,
        email='user1@example.com',
        password='password1',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    user2 = MockUser(
        pk=6,
        email='user2@example.com',
        password='password2',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    token1 = default_token_generator.make_token(user1)
    token2 = default_token_generator.make_token(user2)
    
    assert token1 != token2, "Different users should have different tokens"
    assert default_token_generator.check_token(user1, token1), "User1's token should work for user1"
    assert not default_token_generator.check_token(user1, token2), "User2's token should not work for user1"
    assert default_token_generator.check_token(user2, token2), "User2's token should work for user2"
    assert not default_token_generator.check_token(user2, token1), "User1's token should not work for user2"
    
    print("✅ Test 5 passed: Different users have different tokens")
    return True


def test_empty_email():
    """Test that users with empty email string work correctly."""
    from django.contrib.auth.tokens import default_token_generator
    
    user = MockUser(
        pk=7,
        email='',
        password='hashed_password_empty',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    token = default_token_generator.make_token(user)
    assert default_token_generator.check_token(user, token), "Token should be valid for user with empty email"
    
    user.email = 'newemail@example.com'
    assert not default_token_generator.check_token(user, token), "Token should be invalid after setting email"
    
    print("✅ Test 6 passed: Empty email works correctly")
    return True


def test_none_email():
    """Test that users with None email work correctly."""
    from django.contrib.auth.tokens import default_token_generator
    
    user = MockUser(
        pk=8,
        email=None,
        password='hashed_password_none',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    token = default_token_generator.make_token(user)
    assert default_token_generator.check_token(user, token), "Token should be valid for user with None email"
    
    user.email = 'newemail@example.com'
    assert not default_token_generator.check_token(user, token), "Token should be invalid after setting email"
    
    print("✅ Test 7 passed: None email works correctly")
    return True


if __name__ == '__main__':
    all_passed = True
    
    try:
        all_passed &= test_email_change_invalidates_token()
        all_passed &= test_password_change_invalidates_token()
        all_passed &= test_user_without_email()
        all_passed &= test_same_email_keeps_token_valid()
        all_passed &= test_multiple_users_different_tokens()
        all_passed &= test_empty_email()
        all_passed &= test_none_email()
        
        if all_passed:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed")
            
    except AssertionError as e:
        print(f"\n❌ Test failed with assertion error: {e}")
        all_passed = False
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    exit(0 if all_passed else 1)
