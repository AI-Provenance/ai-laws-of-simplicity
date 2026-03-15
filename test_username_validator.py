"""
Test script to reproduce the username validator issue with trailing newlines.
"""
import sys
sys.path.insert(0, '.')

from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.core.exceptions import ValidationError


def test_validators():
    """Test that validators reject usernames with trailing newlines."""
    
    ascii_validator = ASCIIUsernameValidator()
    unicode_validator = UnicodeUsernameValidator()
    
    # Valid usernames (should pass)
    valid_usernames = [
        'user',
        'user123',
        'user.name',
        'user@example',
        'user+tag',
        'user-name',
        'user_name',
    ]
    
    # Invalid usernames with trailing newline (should fail but currently pass)
    invalid_usernames = [
        'user\n',
        'username\n',
        'test.user\n',
        'user@example\n',
    ]
    
    print("Testing valid usernames (should all pass):")
    for username in valid_usernames:
        try:
            ascii_validator(username)
            unicode_validator(username)
            print(f"  ✓ '{username}' - PASSED")
        except ValidationError as e:
            print(f"  ✗ '{username}' - FAILED (unexpected): {e}")
    
    print("\nTesting invalid usernames with trailing newline (should all fail):")
    for username in invalid_usernames:
        ascii_failed = False
        unicode_failed = False
        
        try:
            ascii_validator(username)
            print(f"  ✗ ASCIIUsernameValidator accepted '{repr(username)}' - BUG!")
        except ValidationError:
            ascii_failed = True
            print(f"  ✓ ASCIIUsernameValidator rejected '{repr(username)}'")
        
        try:
            unicode_validator(username)
            print(f"  ✗ UnicodeUsernameValidator accepted '{repr(username)}' - BUG!")
        except ValidationError:
            unicode_failed = True
            print(f"  ✓ UnicodeUsernameValidator rejected '{repr(username)}'")
    
    print("\n" + "="*70)
    print("ISSUE: Validators should reject usernames with trailing newlines")
    print("="*70)


if __name__ == '__main__':
    test_validators()
