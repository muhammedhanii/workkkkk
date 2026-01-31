from typing import List, Tuple, Optional
from models.schemas import Piece, PlacedPiece, Board, CuttingResult


class Rectangle:
    """Helper class for guillotine packing"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class GuillotinePacker:
    """2D bin packing using guillotine algorithm with First-Fit Decreasing"""
    
    def __init__(self, board_length: int = 2400, board_width: int = 1200):
        self.board_length = board_length  # mm
        self.board_width = board_width    # mm
        
    def pack_pieces(self, pieces: List[Piece]) -> CuttingResult:
        """
        Main packing algorithm:
        1. Expand quantity into individual pieces
        2. Reject pieces exceeding board size
        3. Sort by area (descending), constrained pieces first
        4. Pack using guillotine cuts
        """
        # Expand pieces by quantity
        expanded_pieces = []
        rejected_pieces = []
        
        for piece in pieces:
            for i in range(piece.quantity):
                # Convert cm to mm
                length_mm = piece.length * 10
                width_mm = piece.width * 10
                
                # Check if piece fits on board (with or without rotation)
                can_fit = False
                if (length_mm <= self.board_length and width_mm <= self.board_width):
                    can_fit = True
                elif (width_mm <= self.board_length and length_mm <= self.board_width):
                    # Can fit if rotated
                    if not piece.length_constraint and not piece.width_constraint:
                        can_fit = True
                
                if can_fit:
                    expanded_pieces.append({
                        'name': piece.name,
                        'length': length_mm,
                        'width': width_mm,
                        'length_constraint': piece.length_constraint,
                        'width_constraint': piece.width_constraint,
                        'area': length_mm * width_mm
                    })
                else:
                    rejected_pieces.append(piece)
        
        # Sort: constrained pieces first, then by area descending
        expanded_pieces.sort(key=lambda p: (
            not (p['length_constraint'] or p['width_constraint']),  # False < True, so constrained first
            -p['area']  # Then by area descending
        ))
        
        # Pack pieces into boards
        boards = []
        board_number = 1
        
        while expanded_pieces:
            board, remaining = self._pack_single_board(expanded_pieces)
            boards.append(board)
            board.board_number = board_number
            board_number += 1
            expanded_pieces = remaining
        
        # Calculate overall utilization
        total_area = self.board_length * self.board_width * len(boards)
        used_area = sum(board.utilization * self.board_length * self.board_width / 100 
                       for board in boards)
        overall_utilization = (used_area / total_area * 100) if total_area > 0 else 0
        
        return CuttingResult(
            boards=boards,
            total_boards=len(boards),
            overall_utilization=round(overall_utilization, 2),
            rejected_pieces=rejected_pieces
        )
    
    def _pack_single_board(self, pieces: List[dict]) -> Tuple[Board, List[dict]]:
        """Pack as many pieces as possible into a single board"""
        free_rectangles = [Rectangle(0, 0, self.board_length, self.board_width)]
        placed_pieces = []
        remaining_pieces = []
        
        for piece in pieces:
            placed = False
            
            # Try to place the piece in free rectangles
            for i, rect in enumerate(free_rectangles):
                placement = self._try_place_piece(piece, rect)
                
                if placement:
                    placed_piece, new_rects = placement
                    placed_pieces.append(placed_piece)
                    
                    # Remove used rectangle and add new ones
                    free_rectangles.pop(i)
                    free_rectangles.extend(new_rects)
                    
                    # Merge overlapping rectangles (simplified)
                    free_rectangles = self._merge_rectangles(free_rectangles)
                    
                    placed = True
                    break
            
            if not placed:
                remaining_pieces.append(piece)
        
        # Calculate utilization
        used_area = sum(p.length * p.width for p in placed_pieces)
        total_area = self.board_length * self.board_width
        utilization = (used_area / total_area * 100) if total_area > 0 else 0
        
        board = Board(
            board_number=0,  # Will be set by caller
            length=self.board_length,
            width=self.board_width,
            pieces=placed_pieces,
            utilization=round(utilization, 2),
            waste_area=total_area - used_area
        )
        
        return board, remaining_pieces
    
    def _try_place_piece(self, piece: dict, rect: Rectangle) -> Optional[Tuple[PlacedPiece, List[Rectangle]]]:
        """Try to place a piece in a rectangle"""
        length = piece['length']
        width = piece['width']
        
        # Try normal orientation
        if length <= rect.width and width <= rect.height:
            if not piece['width_constraint'] and not piece['length_constraint']:
                # No constraints, can place
                return self._place_and_split(piece, rect, length, width, False)
            elif piece['length_constraint'] and not piece['width_constraint']:
                # Length must align with board length (x-axis)
                return self._place_and_split(piece, rect, length, width, False)
        
        # Try rotated orientation (if no constraints)
        if not piece['length_constraint'] and not piece['width_constraint']:
            if width <= rect.width and length <= rect.height:
                return self._place_and_split(piece, rect, width, length, True)
        
        return None
    
    def _place_and_split(self, piece: dict, rect: Rectangle, 
                         placed_width: int, placed_height: int, 
                         rotated: bool) -> Tuple[PlacedPiece, List[Rectangle]]:
        """Place piece and create new free rectangles (guillotine cuts)"""
        placed = PlacedPiece(
            name=piece['name'],
            length=placed_width,
            width=placed_height,
            x=rect.x,
            y=rect.y,
            rotated=rotated
        )
        
        # Create new free rectangles using guillotine cuts
        new_rects = []
        
        # Right rectangle
        if rect.width > placed_width:
            new_rects.append(Rectangle(
                rect.x + placed_width,
                rect.y,
                rect.width - placed_width,
                rect.height
            ))
        
        # Top rectangle
        if rect.height > placed_height:
            new_rects.append(Rectangle(
                rect.x,
                rect.y + placed_height,
                placed_width,
                rect.height - placed_height
            ))
        
        return placed, new_rects
    
    def _merge_rectangles(self, rectangles: List[Rectangle]) -> List[Rectangle]:
        """Simplified rectangle merging - just remove tiny rectangles"""
        return [r for r in rectangles if r.width > 10 and r.height > 10]
