"""Structured exceptions for user-friendly error messages."""


class WanVidGenException(Exception):
    """Base exception for WanVidGen."""

    def __init__(self, message: str, user_message: str | None = None):
        """Initialize exception with technical and user-friendly messages.

        Args:
            message: Technical error message for logging.
            user_message: User-friendly message for GUI display.
        """
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)


class ModelLoadError(WanVidGenException):
    """Exception raised when a model fails to load."""

    pass


class ConfigError(WanVidGenException):
    """Exception raised for configuration errors."""

    pass


class GPUMemoryError(WanVidGenException):
    """Exception raised when there is insufficient GPU memory."""

    pass


class PipelineError(WanVidGenException):
    """Exception raised for pipeline-related errors."""

    pass


class GenerationError(WanVidGenException):
    """Exception raised during generation."""

    pass
