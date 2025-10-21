# backend/app/routers/csv.py
"""
CSV router - Upload CSV or provide URL for data analysis.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.dto import CsvInUrl, CsvReply
from app.services.csv_service import analyze_csv
import logging
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/url", response_model=CsvReply)
async def analyze_csv_url(request: CsvInUrl):
    """
    Analyze CSV from a URL.
    Supports questions like: "Summarize", "Show stats", "Missing values", "Plot histogram"
    """
    try:
        logger.info(f"📊 Fetching CSV from URL: {request.csvUrl}")
        
        # Fetch CSV from URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(request.csvUrl))
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch CSV from URL: {response.status_code}"
                )
            
            csv_content = response.text
        
        logger.info(f"✅ CSV fetched: {len(csv_content)} characters")
        
        # Analyze CSV
        result = await analyze_csv(csv_content, request.prompt)
        
        return CsvReply(
            summary=result["summary"],
            plot_base64=result.get("plot_base64")
        )
        
    except httpx.RequestError as e:
        logger.error(f"❌ Error fetching CSV: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch CSV: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ CSV analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"CSV analysis failed: {str(e)}"
        )


@router.post("/file", response_model=CsvReply)
async def analyze_csv_file(
    file: UploadFile = File(...),
    prompt: str = "Summarize this dataset"
):
    """
    Analyze an uploaded CSV file.
    Supports questions like: "Summarize", "Show stats", "Missing values", "Plot histogram"
    """
    try:
        # Check file extension
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file (.csv extension)"
            )
        
        logger.info(f"📊 Processing CSV file: {file.filename}")
        
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        logger.info(f"✅ CSV loaded: {len(csv_content)} characters")
        
        # Analyze CSV
        result = await analyze_csv(csv_content, prompt)
        
        return CsvReply(
            summary=result["summary"],
            plot_base64=result.get("plot_base64")
        )
        
    except UnicodeDecodeError:
        logger.error("❌ Invalid CSV encoding")
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file encoding. Please ensure the file is UTF-8 encoded."
        )
    except Exception as e:
        logger.error(f"❌ CSV analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"CSV analysis failed: {str(e)}"
        )