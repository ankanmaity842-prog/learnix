from fastapi import HTTPException, status


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationException(AppException):
    def __init__(
        self,
        message: str = "Authentication required",
    ):
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationException(AppException):
    def __init__(
        self,
        message: str = "Access denied",
    ):
        super().__init__(
            message,
            status.HTTP_403_FORBIDDEN,
        )


class ResourceNotFoundException(AppException):
    def __init__(
        self,
        message: str = "Resource not found",
    ):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
        )


def app_exception_to_http(
    exc: AppException,
) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message,
    )