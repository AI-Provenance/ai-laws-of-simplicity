"""
Django settings.
"""


class Settings:
    SECRET_KEY = 'test-secret-key-for-password-reset-tokens'
    PASSWORD_RESET_TIMEOUT = 259200  # 3 days in seconds


settings = Settings()
