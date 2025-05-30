import os
from typing import Union
import logging

logger = logging.getLogger("FileUtils")

def get_file_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip('.')

# async def read_file_content(file) -> Union[str, bytes]:
#     try:
#         if file.content_type.startswith('text/') or file.content_type in ['application/json']:
#             return (await file.read()).decode('utf-8')
#         else:
#             return await file.read()
#     except Exception as e:
#         logger.error(f"Error reading file: {str(e)}")
#         raise


# utils/file_utils.py
async def read_file_content(file) -> Union[str, bytes]:
    """Read file content based on file type"""
    try:
        content = await file.read()
        # If no content_type or it's text/JSON, try decoding
        if not getattr(file, 'content_type', None) or \
           (file.content_type and file.content_type.startswith(('text/', 'application/json')):
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content
        return content
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise