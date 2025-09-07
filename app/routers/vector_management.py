from fastapi import APIRouter, HTTPException
from app.schemas.vector_management_schemas import UploadRequest, DeleteEntryRequest, DeleteEntryResponse
from app.services.upload_service import upload_service
from app.services.qdrant_service import qdrant_service

router = APIRouter()

@router.post("/initialize")
async def initialize_collection():
    try:
        await qdrant_service.create_collection()
        return {"message": "Collection initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize collection: {str(e)}")

@router.post("/upload")
async def upload_data(request: UploadRequest):
    try:
        result = await upload_service.process_and_upload_data(request.data_type, request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload data: {str(e)}")


@router.post("/delete-entry", response_model=DeleteEntryResponse)
async def delete_entry(request: DeleteEntryRequest):
    try:
        result = await qdrant_service.delete_entry(
            name_space=request.name_space,
            original_id=request.original_id
        )
        
        deleted = bool(result and (hasattr(result, 'operation_id') or result))
        
        return DeleteEntryResponse(
            message="Entry deleted successfully" if deleted else "No matching entries found",
            name_space=request.name_space,
            original_id=request.original_id,
            deleted=deleted,
            operation_result=result.__dict__ if hasattr(result, '__dict__') else None
        )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete entry with name_space='{request.name_space}' and original_id='{request.original_id}': {str(e)}"
        )
