class SDFLoaderError(Exception):
    """Base class for SDF loading errors."""


class SDFFileNotFoundError(SDFLoaderError):
    """Raised when the SDF file path does not exist."""


class SDFEmptyFileError(SDFLoaderError):
    """Raised when the SDF file contains no molecule records."""


class SDFMalformedRecordError(SDFLoaderError):
    """Raised when one or more molecule records failed to parse properly."""
