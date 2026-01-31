from typing import List, Optional
from pydantic import BaseModel


class Piece(BaseModel):
    """Represents a single piece to be cut"""
    name: str
    length: int  # cm
    width: int   # cm
    quantity: int
    length_constraint: bool = False  # شرط طول
    width_constraint: bool = False   # شرط عرض


class PlacedPiece(BaseModel):
    """Represents a piece placed on a board"""
    name: str
    length: int
    width: int
    x: int  # position
    y: int  # position
    rotated: bool = False


class Board(BaseModel):
    """Represents a single board with placed pieces"""
    board_number: int
    length: int = 2400  # mm (240 cm)
    width: int = 1200   # mm (120 cm)
    pieces: List[PlacedPiece]
    utilization: float
    waste_area: int


class CuttingResult(BaseModel):
    """Complete cutting optimization result"""
    boards: List[Board]
    total_boards: int
    overall_utilization: float
    rejected_pieces: List[Piece] = []
