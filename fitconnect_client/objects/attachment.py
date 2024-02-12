import mimetypes
import uuid
from hashlib import sha512
from pathlib import Path
from fitconnect_client.log import logger


class Attachment:
    def __repr__(self) -> str:
        return f"Attachment<{self.id}>({self.filename})"

    def __init__(self, path: str, description: str = "", purpose: str = "attachment") -> None:
        self.path = Path(path)
        self.filename = self.path.name
        self.mime_type = mimetypes.guess_type(self.path.absolute())[0]
        self.id = str(uuid.uuid4())
        self.description = description
        self.purpose = purpose
        logger.debug(f"Parsed {self}")

    def get_api_metadata_impl(self) -> dict:
        with open(self.path, "rb") as file:
            hex_digest = sha512(file.read()).hexdigest()
        return {
            "hash": {"type": "sha512", "content": hex_digest},
            "purpose": self.purpose,
            "filename": self.filename,
            "description": self.description,
            "mimeType": self.mime_type,
            "attachmentId": self.id
        }
