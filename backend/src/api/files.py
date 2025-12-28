from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..services.file_service import FileService
from ..services.auth_service import AuthService
from ..models.text_file import FileListItem, FileListResponse, PasswordRequest, AuthToken

router = APIRouter(prefix="/files", tags=["files"])
file_service = FileService()
auth_service = AuthService()
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证JWT令牌"""
    token = credentials.credentials

    if not auth_service.validate_token(token):
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    return token


@router.post("/verify-password", response_model=AuthToken)
async def verify_password(request: PasswordRequest):
    """验证访问口令"""
    try:
        token = auth_service.verify_password(request.password)
        return token
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=FileListResponse, dependencies=[Depends(verify_token)])
async def get_files_list(
    page: int = Query(1, ge=1, description="页码"), limit: int = Query(50, ge=1, le=100, description="每页文件数")
):
    """获取文件列表（需要认证）"""
    try:
        files = file_service.list_files(page, limit)
        total = file_service.get_total_files_count()

        return FileListResponse(files=files, total=total, page=page, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{filename}/delete")
async def delete_file(filename: str):
    """删除文件"""
    try:
        if not file_service.file_exists(filename):
            raise HTTPException(status_code=404, detail="File not found")

        file_service.delete_file(filename)
        return {"message": f"File {filename} deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{filename}/rename")
async def rename_file(filename: str, new_filename: str = Query(..., description="新文件名")):
    """重命名文件"""
    try:
        if not file_service._validate_filename(new_filename):
            raise HTTPException(status_code=400, detail="Invalid new filename")

        if not file_service.file_exists(filename):
            return {"message": f"File renamed to {new_filename}"}

        if file_service.file_exists(new_filename):
            raise HTTPException(status_code=400, detail="File with new name already exists")

        file_service.rename_file(filename, new_filename)
        return {"message": f"File renamed from {filename} to {new_filename}"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
