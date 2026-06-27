from fastapi import APIRouter, UploadFile, File, HTTPException
from app.backend.services.skin_service import skin_service

router = APIRouter()

@router.post("/analyze")
async def analyze_skin_image(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No visual image asset detected.")
        
    try:
        raw_image_bytes = await file.read()
        analysis_result = skin_service.analyze_image_stream(raw_image_bytes)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
            
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))