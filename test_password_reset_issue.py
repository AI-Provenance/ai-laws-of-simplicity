"""
Test script to reproduce the password reset token issue.

The issue: When a user changes their email address, password reset tokens
generated before the email change should be invalidated, but they are not.
"""
from datetime import datetime


class MockUser:
    """Mock user object for testing."""
    def __init__(self, pk, email, password, last_login=None):
        self.pk = pk
        self.email = email
        self.password = password
        self.last_login = last_login


def test_password_reset_token_with_email_change():
    """
    Test that demonstrates the security issue:
    1. User has email foo@example.com
    2. Password reset token is generated
    3. User changes email to bar@example.com
    4. Old token should be invalid but is still accepted
    """
    from django.contrib.auth.tokens import default_token_generator
    
    # Step 1: Create user with initial email
    user = MockUser(
        pk=1,
        email='foo@example.com',
        password='hashed_password_123',
        last_login=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    # Step 2: Generate password reset token
    token = default_token_generator.make_token(user)
    print(f"Generated token: {token}")
    
    # Step 3: Verify token works with original email
    is_valid_before = default_token_generator.check_token(user, token)
    print(f"Token valid with original email (foo@example.com): {is_valid_before}")
    assert is_valid_before, "Token should be valid with original email"
    
    # Step 4: User changes their email address
    user.email = 'bar@example.com'
    print(f"User changed email to: {user.email}")
    
    # Step 5: Check if token is still valid (it shouldn't be!)
    is_valid_after = default_token_generator.check_token(user, token)
    print(f"Token valid after email change: {is_valid_after}")
    
    if is_valid_after:
        print("\n❌ SECURITY ISSUE: Token is still valid after email change!")
        print("This is a security vulnerability - old password reset tokens should be invalidated.")
        return False
    else:
        print("\n✅ FIXED: Token is correctly invalidated after email change!")
        return True


if __name__ == '__main__':
    success = test_password_reset_token_with_email_change()
    exit(0 if success else 1)
