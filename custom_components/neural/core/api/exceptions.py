"""Custom exceptions for Neural API."""


class MyVerisureError(Exception):
    """Base exception for Neural API errors."""


class MyVerisureAuthenticationError(MyVerisureError):
    """Authentication failed."""


class MyVerisureConnectionError(MyVerisureError):
    """Connection to Neural API failed."""


class MyVerisureResponseError(MyVerisureError):
    """Invalid response from Neural API."""


class MyVerisureMFAError(MyVerisureError):
    """MFA authentication error."""


class MyVerisureOTPError(MyVerisureError):
    """OTP authentication error."""


class MyVerisureDeviceAuthorizationError(MyVerisureError):
    """Device authorization error - device needs to be authorized."""
