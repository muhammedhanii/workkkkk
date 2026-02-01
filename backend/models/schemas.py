from typing import List, Optional
from pydantic import BaseModel


class Piece(BaseModel):
    """Represents a single piece to be cut"""
    name: str
    length: float  # cm (supports decimals)
    width: float   # cm (supports decimals)
    quantity: int
    length_constraint: bool = False  # شرط طول
    width_constraint: bool = False   # شرط عرض


class PlacedPiece(BaseModel):
    """Represents a piece placed on a board"""
    name: str
    length: float
    width: float
    x: float  # position
    y: float  # position
    rotated: bool = False


class Board(BaseModel):
    """Represents a single board with placed pieces"""
    board_number: int
    length: float = 2400  # mm (240 cm)
    width: float = 1200   # mm (120 cm)
    pieces: List[PlacedPiece]
    utilization: float
    waste_area: float


class CuttingResult(BaseModel):
    """Complete cutting optimization result"""
    boards: List[Board]
    total_boards: int
    overall_utilization: float
    rejected_pieces: List[Piece] = []
