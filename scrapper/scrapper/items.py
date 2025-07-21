from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Metadata:
    cleaned: bool = False
    edited: bool = False


@dataclass
class FileItem:
    body: bytes
    source_url: str
    extension: str


@dataclass
class MetadataItem:
    file_type: str
    source_url: str
    metadata: Metadata
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: str(datetime.now()))


@dataclass
class ScrappedItem:
    file: FileItem
    metadata: MetadataItem
    file_path: str | None = None
    metadata_path: str | None = None
    path: str | None = None
