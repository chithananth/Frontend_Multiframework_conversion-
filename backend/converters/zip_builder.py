"""
ZIP Builder – packages multiple files into an in-memory ZIP archive.
"""

import io
import zipfile


def build_zip(files: dict) -> bytes:
    """
    Build an in-memory ZIP.

    :param files: dict mapping filename (str) → file content (str)
    :returns:     bytes of the ZIP archive
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)
    buf.seek(0)
    return buf.read()
