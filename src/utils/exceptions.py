class MBLoaderError(Exception):
    """Base class for SDF loading errors."""


class SDFFileNotFoundError(MBLoaderError):
    """Raised when the SDF file path does not exist."""


class SDFEmptyFileError(MBLoaderError):
    """Raised when the SDF file contains no molecule records."""


class SDFMalformedRecordError(MBLoaderError):
    """Raised when one or more molecule records failed to parse properly."""
