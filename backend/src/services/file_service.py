import os
import re
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from ..models.text_file import TextFile, FileListItem
from ..utils.config import get_settings


class FileService:
    def __init__(self):
        self.settings = get_settings()
        self.notes_dir = Path(self.settings.notes_path)
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def _validate_filename(self, filename: str) -> bool:
        if len(filename) > 200 or len(filename) < 1:
            return False

        illegal_chars = r'[^a-zA-Z0-9_.\-\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]'
        if (
            re.search(illegal_chars, filename)
            or filename.startswith("_")
            or filename.startswith(".")
            or filename.startswith("-")
        ):
            return False

        if '..' in filename or filename.startswith('/'):
            return False

        return True

    def _add_txt_extension(self, filename: str) -> str:
        if not filename.lower().endswith('.txt'):
            return f"{filename}.txt"
        return filename

    def read_file(self, filename: str) -> TextFile:
        if not self._validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")

        filename = self._add_txt_extension(filename)
        file_path = self.notes_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            stat = file_path.stat()
            return TextFile(
                filename=filename,
                content=content,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                updated_at=datetime.fromtimestamp(stat.st_mtime),
                size=len(content),
            )
        except UnicodeDecodeError:
            raise ValueError(f"File {filename} is not a valid text file")
        except Exception as e:
            raise RuntimeError(f"Error reading file {filename}: {str(e)}")

    def write_file(self, filename: str, content: str) -> TextFile:
        if not self._validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")

        if content is None:
            raise ValueError("Content cannot be None")

        if len(content) > 100000:
            raise ValueError("File content too large (max 100,000 characters)")

        filename = self._add_txt_extension(filename)
        file_path = self.notes_dir / filename

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            stat = file_path.stat()
            return TextFile(
                filename=filename,
                content=content,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                updated_at=datetime.fromtimestamp(stat.st_mtime),
                size=len(content),
            )
        except Exception as e:
            raise RuntimeError(f"Error writing file {filename}: {str(e)}")

    def create_file(self, filename: str) -> TextFile:
        """创建新文件"""
        return self.write_file(filename, "")

    def list_files(self, page: int = 1, limit: int = 50) -> List[FileListItem]:
        if page < 1:
            page = 1

        if limit < 1 or limit > 100:
            limit = 50

        files = []

        try:
            for file_path in self.notes_dir.glob("*.txt"):
                stat = file_path.stat()

                preview = ""
                if stat.st_size > 0:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(100)
                            preview = content.replace('\n', ' ').replace('\r', '').strip()
                            if len(preview) > 50:
                                preview = preview[:50] + "..."
                    except UnicodeDecodeError:
                        preview = "[非文本文件]"
                    except Exception:
                        preview = ""

                files.append(
                    FileListItem(
                        filename=file_path.name,
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        size=stat.st_size,
                        preview=preview,
                    )
                )
        except Exception as e:
            raise RuntimeError(f"Error listing files: {str(e)}")

        files.sort(key=lambda x: x.created_at, reverse=True)

        start = (page - 1) * limit
        end = start + limit

        return files[start:end]

    def get_total_files_count(self) -> int:
        try:
            return len(list(self.notes_dir.glob("*.txt")))
        except Exception:
            return 0

    def file_exists(self, filename: str) -> bool:
        if not self._validate_filename(filename):
            return False

        filename = self._add_txt_extension(filename)
        file_path = self.notes_dir / filename
        return file_path.exists() and file_path.is_file()

    def delete_file(self, filename: str) -> bool:
        if not self._validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")

        filename = self._add_txt_extension(filename)
        file_path = self.notes_dir / filename

        if not file_path.exists():
            return True  # 文件已不存在

        try:
            file_path.unlink()
            return True
        except Exception as e:
            raise RuntimeError(f"Error deleting file {filename}: {str(e)}")

    def rename_file(self, old_filename: str, new_filename: str) -> bool:
        if not self._validate_filename(old_filename):
            raise ValueError(f"Invalid old filename: {old_filename}")

        if not self._validate_filename(new_filename):
            raise ValueError(f"Invalid new filename: {new_filename}")

        old_filename = self._add_txt_extension(old_filename)
        new_filename = self._add_txt_extension(new_filename)

        old_path = self.notes_dir / old_filename
        new_path = self.notes_dir / new_filename

        if not old_path.exists():
            return True

        if new_path.exists():
            raise ValueError(f"File {new_filename} already exists")

        try:
            old_path.rename(new_path)
            return True
        except Exception as e:
            raise RuntimeError(f"Error renaming file {old_filename}: {str(e)}")
