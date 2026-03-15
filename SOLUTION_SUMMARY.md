# Password Reset Token Security Fix - Solution Summary

## Problem Statement

As described in the PR, there was a security vulnerability in the password reset token generation:

**Sequence of the vulnerability:**
1. User has account with email address `foo@example.com`
2. Password reset request is made for that email (token generated but unused)
3. User changes their email address to `bar@example.com`
4. The old password reset email's token is still accepted ❌ (SECURITY ISSUE)

The token should have been invalidated when the email changed, but it wasn't.

## Root Cause

The `PasswordResetTokenGenerator._make_hash_value()` method did not include the user's email address in the hash calculation. It only included:
- User's primary key (pk)
- User's password
- User's last_login timestamp
- Token generation timestamp

This meant that changing the email address did not affect the token's validity.

## Solution

Modified the `_make_hash_value()` method in `django/contrib/auth/tokens.py` to include the user's email address in the hash calculation.

### Changes Made

1. **Added email field extraction** (line 88):
   ```python
   email_field = user.email if hasattr(user, 'email') else ''
   ```
   - Uses `hasattr()` to check if the user has an email attribute
   - Falls back to empty string for users without email (AbstractBaseUser compatibility)

2. **Included email in hash value** (line 89):
   ```python
   return str(user.pk) + user.password + str(login_timestamp) + str(timestamp) + str(email_field)
   ```
   - Appends the email field to the hash value string

3. **Updated documentation** (lines 72-78):
   - Updated docstring to mention email in the hash
   - Added point 3: "The email field will change if the user updates their email address"

## Key Features of the Fix

1. **Security**: Email changes now invalidate password reset tokens
2. **Backward Compatibility**: Handles users without email field (AbstractBaseUser)
3. **Edge Cases**: Properly handles None and empty string email values
4. **Existing Behavior**: Password changes still invalidate tokens (unchanged)

## Testing

All tests pass successfully:
- ✅ Email change invalidates token
- ✅ Password change invalidates token (existing behavior)
- ✅ Users without email field work correctly
- ✅ Same email keeps token valid
- ✅ Different users have different tokens
- ✅ Empty email works correctly
- ✅ None email works correctly

## Impact

**Security Impact**: This fix closes a security vulnerability where:
- An attacker could request a password reset for a target account
- Wait for the user to change their email (or social engineer them to do so)
- Use the old token to reset the password even though the email has changed

**Deployment Impact**: All existing password reset tokens will be invalidated when this change is deployed, as the hash calculation has changed. This is acceptable and desirable for security reasons. Users with pending password reset tokens will need to request new ones.

## Code Changes Summary

- **File Modified**: `django/contrib/auth/tokens.py`
- **Method Modified**: `PasswordResetTokenGenerator._make_hash_value()`
- **Lines Changed**: 3 lines added/modified
- **Lines of Code**: +2 lines (net)
