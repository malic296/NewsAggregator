from typing import Optional
from fastapi import status

class AppError(Exception):
    def __init__(self, *, status_code: int, public_message: str, internal_message: Optional[str] = None):
        self.status_code = status_code
        self.internal_message = internal_message
        self.public_message = public_message if public_message else "Internal Server Error."

class CLIError(Exception):
    pass

class InvalidInvitationCode(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            public_message="Registrations are only available to closed group of people and not public."
        )

class AuthenticationRequiredError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            public_message="You need to login or register first."
        )

class InvalidCredentialsError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            public_message="Invalid login details."
        )

class EmailAlreadyUsedError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            public_message="Email already used."
        )

class UsernameAlreadyUsedError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            public_message="Username already used."
        )

class ArticleNotFoundError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            public_message="Article not found."
        )

class InvalidVerificationCodeError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            public_message="Invalid verification code."
        )

class RegistrationExpiredError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_410_GONE,
            public_message="Registration expired."
        )

class InvalidCurrentPasswordError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            public_message="Invalid current password."
        )

class PasswordReuseError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            public_message="Cannot change password to current password."
        )

class DependencyUnavailableError(AppError):
    def __init__(self, dependency: str = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            internal_message=f"Dependency {dependency if dependency else ""} unavailable.",
            public_message="Server failed because of external error. Try again later."
        )

class EnvVarNotFoundError(AppError):
    def __init__(self, variable: str = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            internal_message=f"Environment variables{": " + variable if variable else ""} not set correctly.",
            public_message="Server failed because of internal error. Try again later."
        )

class MappingError(AppError):
    def __init__(self, mapping_error: str, method: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            internal_message=f"Method {method} failed because of mapping error: {mapping_error}",
            public_message="Server failed because of internal error. Try again later."
        )

class DatabaseError(AppError):
    def __init__(self, message: str, method: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            internal_message=f"Query execution failed for method: {method}. Error message: {message}",
            public_message="Server failed because of internal error. Try again later."
        )

class ElasticSearchError(AppError):
    def __init__(self, message: str, method: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            internal_message=f"Elastic search failed during method: {method}. Error message: {message}",
            public_message="Server failed because of internal error. Try again later."
        )

class RateLimitExceededError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            public_message="Too many requests. Try again in a short moment."
        )

class ScrapingError(CLIError):
    pass


