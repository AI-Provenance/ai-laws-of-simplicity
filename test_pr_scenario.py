"""
Test the exact scenario described in the PR:
1. Have account with email address foo@...
2. Password reset request for that email (unused)
3. foo@... account changes their email address
4. Password reset email is used
5. The password reset email's token should be rejected at that point
"""
from datetime import datetime


class MockUser:
    """Mock user object for testing."""
    def __init__(self, pk, email, password, last_login=None):
        self.pk = pk
        self.email = email
        self.password = password
        self.last_login = last_login


def test_pr_scenario():
    """Test the exact scenario from the PR description."""
    from django.contrib.auth.tokens import default_token_generator
    
    print("=" * 70)
    print("Testing PR Scenario: Email change should invalidate reset tokens")
    print("=" * 70)
    
    # Step 1: Have account with email address foo@...
    print("\n1. Creating user account with email foo@example.com")
    user = MockUser(
        pk=42,
        email='foo@example.com',
        password='pbkdf2_sha256$260000$hashed_password',
        last_login=datetime(2024, 1, 15, 10, 30, 0)
    )
    print(f"   User created: pk={user.pk}, email={user.email}")
    
    # Step 2: Password reset request for that email (unused)
    print("\n2. Generating password reset token (unused)")
    reset_token = default_token_generator.make_token(user)
    print(f"   Token generated: {reset_token}")
    print(f"   Token is valid: {default_token_generator.check_token(user, reset_token)}")
    
    # Step 3: foo@... account changes their email address
    print("\n3. User changes email address")
    old_email = user.email
    user.email = 'new_email@example.com'
    print(f"   Email changed from {old_email} to {user.email}")
    
    # Step 4 & 5: Password reset email is used - should be rejected
    print("\n4. Attempting to use the old password reset token")
    is_token_valid = default_token_generator.check_token(user, reset_token)
    print(f"   Token is valid: {is_token_valid}")
    
    if is_token_valid:
        print("\n" + "!" * 70)
        print("❌ SECURITY VULNERABILITY DETECTED!")
        print("!" * 70)
        print("The token should have been invalidated when the email changed!")
        print("This allows an attacker to use old reset tokens even after")
        print("the user has changed their email address.")
        return False
    else:
        print("\n" + "=" * 70)
        print("✅ SECURITY FIX VERIFIED!")
        print("=" * 70)
        print("The token was correctly invalidated when the email changed.")
        print("Old password reset tokens cannot be used after email changes.")
        return True


def test_password_change_still_invalidates():
    """Verify that password changes still invalidate tokens (existing behavior)."""
    from django.contrib.auth.tokens import default_token_generator
    
    print("\n" + "=" * 70)
    print("Verifying existing behavior: Password change invalidates tokens")
    print("=" * 70)
    
    user = MockUser(
        pk=43,
        email='test@example.com',
        password='pbkdf2_sha256$260000$old_password',
        last_login=datetime(2024, 1, 15, 10, 30, 0)
    )
    
    token = default_token_generator.make_token(user)
    print(f"\n1. Token generated for user with password: {user.password[:30]}...")
    print(f"   Token is valid: {default_token_generator.check_token(user, token)}")
    
    user.password = 'pbkdf2_sha256$260000$new_password'
    print(f"\n2. User password changed to: {user.password[:30]}...")
    
    is_valid = default_token_generator.check_token(user, token)
    print(f"   Token is valid: {is_valid}")
    
    if is_valid:
        print("\n❌ FAIL: Password change should invalidate token!")
        return False
    else:
        print("\n✅ PASS: Password change correctly invalidates token")
        return True


def test_no_email_field_compatibility():
    """Test compatibility with AbstractBaseUser (users without email field)."""
    from django.contrib.auth.tokens import default_token_generator
    
    print("\n" + "=" * 70)
    print("Testing AbstractBaseUser compatibility (no email field)")
    print("=" * 70)
    
    class UserWithoutEmail:
        def __init__(self, pk, password, last_login=None):
            self.pk = pk
            self.password = password
            self.last_login = last_login
    
    user = UserWithoutEmail(
        pk=44,
        password='pbkdf2_sha256$260000$password',
        last_login=datetime(2024, 1, 15, 10, 30, 0)
    )
    
    print("\n1. Creating user without email field")
    print(f"   User has email attribute: {hasattr(user, 'email')}")
    
    try:
        token = default_token_generator.make_token(user)
        print(f"\n2. Token generated successfully: {token}")
        
        is_valid = default_token_generator.check_token(user, token)
        print(f"   Token is valid: {is_valid}")
        
        if is_valid:
            print("\n✅ PASS: Users without email field work correctly")
            return True
        else:
            print("\n❌ FAIL: Token should be valid for user without email")
            return False
    except Exception as e:
        print(f"\n❌ FAIL: Exception raised: {e}")
        return False


if __name__ == '__main__':
    print("\n" + "#" * 70)
    print("# PASSWORD RESET TOKEN SECURITY TEST SUITE")
    print("#" * 70)
    
    all_passed = True
    
    all_passed &= test_pr_scenario()
    all_passed &= test_password_change_still_invalidates()
    all_passed &= test_no_email_field_compatibility()
    
    print("\n" + "#" * 70)
    if all_passed:
        print("# 🎉 ALL TESTS PASSED!")
    else:
        print("# ❌ SOME TESTS FAILED!")
    print("#" * 70)
    print()
    
    exit(0 if all_passed else 1)
