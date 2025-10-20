from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.models.dto import CsvInUrl, CsvReply
from app.services.csv_service import analyze_csv_from_url, analyze_csv_from_file
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/url", response_model=CsvReply)
async def csv_chat_url_endpoint(csv_in: CsvInUrl):
    """
    CSV analysis from URL endpoint.
    
    TODO: Implement pandas-based CSV analysis
    TODO: Generate matplotlib histograms and return as base64
    TODO: Add natural language query processing for data insights
    """
    try:
        logger.info(f"Analyzing CSV from URL: {csv_in.csvUrl}")
        result = await analyze_csv_from_url(csv_in.csvUrl, csv_in.prompt)
        return result
    except Exception as e:
        logger.error(f"CSV URL analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV analysis failed: {str(e)}")


@router.post("/file", response_model=CsvReply)
async def csv_chat_file_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form(...)
):
    """
    CSV analysis from uploaded file endpoint.
    
    TODO: Implement file validation (size, type)
    TODO: Use pandas for data exploration based on prompt
    TODO: Generate visualizations (histograms, scatter plots) as base64
    """
    try:
        logger.info(f"Analyzing uploaded CSV: {file.filename}")
        result = await analyze_csv_from_file(file, prompt)
        return result
    except Exception as e:
        logger.error(f"CSV file analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV analysis failed: {str(e)}")