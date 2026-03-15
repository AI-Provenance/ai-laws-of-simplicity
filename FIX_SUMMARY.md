# Password Reset Token Security Fix

## Problem
When a user changes their email address, password reset tokens generated before the email change should be invalidated, but they were not. This creates a security vulnerability where:

1. User has account with email `foo@example.com`
2. Password reset request is made for that email (token generated but not used)
3. User changes their email address to `bar@example.com`
4. The old password reset email's token is still accepted (SECURITY ISSUE)

## Root Cause
The `PasswordResetTokenGenerator._make_hash_value()` method did not include the user's email address in the hash calculation. The hash only included:
- User's primary key (pk)
- User's password
- User's last_login timestamp
- Token generation timestamp

This meant that changing the email address did not invalidate existing tokens.

## Solution
Modified the `_make_hash_value()` method to include the user's email address in the hash calculation. The fix:

1. Checks if the user has an email attribute using `hasattr(user, 'email')`
2. Includes the email in the hash value
3. Handles edge cases:
   - Users without email field (AbstractBaseUser compatibility)
   - Users with None email
   - Users with empty string email

## Changes Made
File: `django/contrib/auth/tokens.py`

In the `_make_hash_value()` method:
- Added email field extraction with fallback to empty string
- Appended email to the hash value string
- Updated docstring to document the email field inclusion

## Testing
Created comprehensive tests that verify:
1. ✅ Email change invalidates token
2. ✅ Password change invalidates token (existing behavior)
3. ✅ Users without email field work correctly
4. ✅ Same email keeps token valid
5. ✅ Different users have different tokens
6. ✅ Empty email works correctly
7. ✅ None email works correctly

All tests pass successfully.

## Backward Compatibility
This change will invalidate all existing password reset tokens when deployed, as the hash calculation has changed. This is acceptable and actually desirable for security reasons. Users who have pending password reset tokens will need to request new ones.

## Security Impact
This fix closes a security vulnerability where attackers could potentially:
1. Request a password reset for a target account
2. Wait for the user to change their email (or social engineer them to do so)
3. Use the old token to reset the password even though the email has changed

With this fix, any change to the user's email address will immediately invalidate all pending password reset tokens for that user.
