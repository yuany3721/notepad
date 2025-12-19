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
        self.notes_dir = Path(self.settings.notes_dir)
        self.notes_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_filename(self, filename: str) -> bool:
        """验证文件名是否安全"""
        # 检查文件名长度
        if len(filename) > 200 or len(filename) < 1:
            return False
        
        # 检查文件名是否包含非法字符
        illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
        if re.search(illegal_chars, filename):
            return False
        
        # 检查路径遍历攻击
        if '..' in filename or filename.startswith('/'):
            return False
        
        # 确保文件扩展名为.txt
        if not filename.lower().endswith('.txt'):
            return False
        
        return True
    
    def read_file(self, filename: str) -> TextFile:
        """读取文件内容"""
        if not self._validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")
        
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
                size=len(content)
            )
        except UnicodeDecodeError:
            raise ValueError(f"File {filename} is not a valid text file")
        except Exception as e:
            raise RuntimeError(f"Error reading file {filename}: {str(e)}")
    
    def write_file(self, filename: str, content: str) -> TextFile:
        """写入文件内容"""
        if not self._validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")
        
        if content is None:
            raise ValueError("Content cannot be None")
        
        if len(content) > 100000:
            raise ValueError("File content too large (max 100,000 characters)")
        
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
                size=len(content)
            )
        except Exception as e:
            raise RuntimeError(f"Error writing file {filename}: {str(e)}")
    
    def create_file(self, filename: str) -> TextFile:
        """创建新文件"""
        return self.write_file(filename, "")
    
    def list_files(self, page: int = 1, limit: int = 50) -> List[FileListItem]:
        """列出文件"""
        if page < 1:
            page = 1
        
        if limit < 1 or limit > 100:
            limit = 50
        
        files = []
        
        try:
            for file_path in self.notes_dir.glob("*.txt"):
                stat = file_path.stat()
                
                # 读取文件前100个字符作为预览
                preview = ""
                if stat.st_size > 0:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(100)
                            # 清理预览内容，移除换行符
                            preview = content.replace('\n', ' ').replace('\r', '').strip()
                            if len(preview) > 50:
                                preview = preview[:50] + "..."
                    except UnicodeDecodeError:
                        preview = "[非文本文件]"
                    except Exception:
                        preview = ""
                
                files.append(FileListItem(
                    filename=file_path.name,
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                    size=stat.st_size,
                    preview=preview
                ))
        except Exception as e:
            raise RuntimeError(f"Error listing files: {str(e)}")
        
        # 按创建时间倒序排列
        files.sort(key=lambda x: x.created_at, reverse=True)
        
        # 分页
        start = (page - 1) * limit
        end = start + limit
        
        return files[start:end]
    
    def get_total_files_count(self) -> int:
        """获取文件总数"""
        try:
            return len(list(self.notes_dir.glob("*.txt")))
        except Exception:
            return 0
    
    def file_exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        if not self._validate_filename(filename):
            return False
        
        file_path = self.notes_dir / filename
        return file_path.exists() and file_path.is_file()
    
    def delete_file(self, filename: str) -> bool:
        """删除文件"""
        if not self._validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")
        
        file_path = self.notes_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        
        try:
            file_path.unlink()
            return True
        except Exception as e:
            raise RuntimeError(f"Error deleting file {filename}: {str(e)}")
    
    def rename_file(self, old_filename: str, new_filename: str) -> bool:
        """重命名文件"""
        if not self._validate_filename(old_filename):
            raise ValueError(f"Invalid old filename: {old_filename}")
        
        if not self._validate_filename(new_filename):
            raise ValueError(f"Invalid new filename: {new_filename}")
        
        old_path = self.notes_dir / old_filename
        new_path = self.notes_dir / new_filename
        
        if not old_path.exists():
            raise FileNotFoundError(f"File {old_filename} not found")
        
        if new_path.exists():
            raise ValueError(f"File {new_filename} already exists")
        
        try:
            old_path.rename(new_path)
            return True
        except Exception as e:
            raise RuntimeError(f"Error renaming file {old_filename}: {str(e)}")