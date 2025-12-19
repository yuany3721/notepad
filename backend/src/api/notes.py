from fastapi import APIRouter, HTTPException, Path
from ..services.file_service import FileService
from ..models.text_file import TextFile, SaveRequest

router = APIRouter(prefix="/notes", tags=["notes"])
file_service = FileService()

@router.get("/{filename}", response_model=TextFile)
async def get_file(filename: str = Path(..., min_length=1, max_length=200)):
    """获取文件内容"""
    try:
        if file_service.file_exists(filename):
            return file_service.read_file(filename)
        else:
            # 文件不存在时返回一个空的文件对象，不实际创建文件
            from datetime import datetime
            return TextFile(
                filename=filename,
                content="",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                size=0
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{filename}", response_model=TextFile)
async def save_file(
    filename: str = Path(..., min_length=1, max_length=200),
    request: SaveRequest = None
):
    """保存文件内容"""
    try:
        return file_service.write_file(filename, request.content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))