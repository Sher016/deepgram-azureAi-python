"""
Helper functions for file handling.
"""


def resolve_content_type(filename: str, default: str = "application/octet-stream") -> str:
    """
    Resolve the MIME type based on file extension.
    
    Args:
        filename: Name of the file (with extension)
        default: Default MIME type if extension is not recognized
    
    Returns:
        MIME type string
    """
    ext = filename.rsplit(".", 1)[-1].lower()
    
    mapping = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "flac": "audio/flac",
        "ogg": "audio/ogg",
        "opus": "audio/opus",
        "aac": "audio/aac",
        "m4a": "audio/mp4",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "mp4": "video/mp4",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
        "pdf": "application/pdf",
        "txt": "text/plain",
    }
    
    return mapping.get(ext, default)