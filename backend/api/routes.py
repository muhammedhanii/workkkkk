from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import tempfile
import os
from services.excel_parser import ExcelParser
from services.report_generator import ReportGenerator
from packing.guillotine import GuillotinePacker
from models.schemas import CuttingResult

router = APIRouter()


@router.post("/calculate")
async def calculate_cutting(file: UploadFile = File(...)):
    """
    Calculate optimal cutting layout from uploaded Excel file
    Returns JSON result and generates report
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Parse Excel
        parser = ExcelParser()
        pieces = parser.parse_excel(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if not pieces:
            raise HTTPException(status_code=400, detail="No valid pieces found in Excel file")
        
        # Run packing algorithm
        packer = GuillotinePacker(board_length=2400, board_width=1200)
        result = packer.pack_pieces(pieces)
        
        return {
            "success": True,
            "result": result.dict(),
            "message": f"Successfully packed {len(pieces)} piece types into {result.total_boards} boards"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/calculate/report")
async def calculate_and_generate_report(file: UploadFile = File(...)):
    """
    Calculate optimal cutting layout and return visual report as PNG
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Parse Excel
        parser = ExcelParser()
        pieces = parser.parse_excel(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if not pieces:
            raise HTTPException(status_code=400, detail="No valid pieces found in Excel file")
        
        # Run packing algorithm
        packer = GuillotinePacker(board_length=2400, board_width=1200)
        result = packer.pack_pieces(pieces)
        
        # Generate report
        generator = ReportGenerator()
        report_buffer = generator.generate_report(result, material_name="Wood Board")
        
        return StreamingResponse(
            report_buffer,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=cutting_report.png"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
