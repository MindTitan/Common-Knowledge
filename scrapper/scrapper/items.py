from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Metadata:
    cleaned: bool = False


@dataclass
class FileItem:
    body: bytes
    source_url: str
    extension: str


@dataclass
class ScrappedItem:
    file_type: str
    source_url: str
    metadata: Metadata
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: str(datetime.now()))

