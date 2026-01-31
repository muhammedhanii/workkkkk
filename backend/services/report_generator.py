from io import BytesIO
from typing import List
from PIL import Image, ImageDraw, ImageFont
from models.schemas import Board, CuttingResult


class ReportGenerator:
    """Generates AutoCUT-style reports with visual layouts"""
    
    def __init__(self):
        self.margin = 40
        self.scale = 0.15  # Scale factor for visualization (1mm = 0.15 pixels)
        
    def generate_report(self, result: CuttingResult, material_name: str = "Material") -> BytesIO:
        """Generate complete report as PNG image"""
        
        # Calculate image dimensions
        board_visual_width = int(result.boards[0].length * self.scale)
        board_visual_height = int(result.boards[0].width * self.scale)
        
        # Estimate total height
        header_height = 200
        per_board_height = board_visual_height + 300
        total_height = header_height + per_board_height * len(result.boards) + 100
        
        # Create image
        img_width = max(800, board_visual_width + 2 * self.margin)
        img = Image.new('RGB', (img_width, total_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        y_offset = self.margin
        
        # Draw header
        y_offset = self._draw_header(draw, result, material_name, y_offset, 
                                     img_width, title_font, header_font, normal_font)
        
        # Draw each board
        for board in result.boards:
            y_offset = self._draw_board(draw, board, y_offset, img_width, 
                                       board_visual_width, board_visual_height,
                                       header_font, normal_font, small_font)
            y_offset += 50
        
        # Crop to actual content
        img = img.crop((0, 0, img_width, min(y_offset + 50, total_height)))
        
        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        return output
    
    def _draw_header(self, draw, result, material_name, y, width, 
                     title_font, header_font, normal_font):
        """Draw report header section"""
        # Title
        title = "AutoCUT Standard Report"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        draw.text((width // 2 - title_width // 2, y), title, fill='black', font=title_font)
        y += 40
        
        # Horizontal line
        draw.line([(self.margin, y), (width - self.margin, y)], fill='black', width=2)
        y += 20
        
        # Project info
        info_text = f"Project:          Material: {material_name}          Thickness: 12          Utilization: {result.overall_utilization:.2f}%"
        draw.text((self.margin, y), info_text, fill='black', font=normal_font)
        y += 40
        
        return y
    
    def _draw_board(self, draw, board: Board, y_start: int, img_width: int,
                    board_visual_width: int, board_visual_height: int,
                    header_font, normal_font, small_font):
        """Draw a single board with its pieces"""
        x_offset = self.margin
        
        # Board header
        header_text = f"Sheet: {board.length}mm x {board.width}mm          Utilization: {board.utilization:.2f}%          Count: 1"
        draw.text((x_offset, y_start), header_text, fill='black', font=header_font)
        y_start += 30
        
        # Part table header
        table_y = y_start
        draw.text((x_offset, table_y), "Part Name", fill='black', font=normal_font)
        draw.text((x_offset + 150, table_y), "Length", fill='black', font=normal_font)
        draw.text((x_offset + 250, table_y), "Width", fill='black', font=normal_font)
        draw.text((x_offset + 350, table_y), "Count", fill='black', font=normal_font)
        table_y += 25
        
        # Draw horizontal line
        draw.line([(x_offset, table_y), (x_offset + 450, table_y)], fill='black', width=1)
        table_y += 10
        
        # List pieces (grouped by name)
        piece_counts = {}
        for piece in board.pieces:
            key = f"{piece.name}_{piece.length}_{piece.width}"
            if key not in piece_counts:
                piece_counts[key] = {
                    'name': piece.name,
                    'length': piece.length,
                    'width': piece.width,
                    'count': 0
                }
            piece_counts[key]['count'] += 1
        
        for piece_data in piece_counts.values():
            draw.text((x_offset, table_y), piece_data['name'], fill='black', font=normal_font)
            draw.text((x_offset + 150, table_y), str(piece_data['length']), fill='black', font=normal_font)
            draw.text((x_offset + 250, table_y), str(piece_data['width']), fill='black', font=normal_font)
            draw.text((x_offset + 350, table_y), str(piece_data['count']), fill='black', font=normal_font)
            table_y += 20
        
        y_start = table_y + 20
        
        # Draw board visual
        board_x = x_offset
        board_y = y_start
        
        # Board outline
        draw.rectangle(
            [(board_x, board_y), 
             (board_x + board_visual_width, board_y + board_visual_height)],
            outline='black',
            width=2
        )
        
        # Draw placed pieces
        for piece in board.pieces:
            piece_x = board_x + int(piece.x * self.scale)
            piece_y = board_y + int(piece.y * self.scale)
            piece_w = int(piece.length * self.scale)
            piece_h = int(piece.width * self.scale)
            
            # Draw piece rectangle
            draw.rectangle(
                [(piece_x, piece_y), (piece_x + piece_w, piece_y + piece_h)],
                outline='black',
                width=1
            )
            
            # Draw piece label
            label = f"{piece.name}\n{piece.length} x {piece.width}"
            bbox = draw.textbbox((0, 0), label, font=small_font)
            label_width = bbox[2] - bbox[0]
            label_height = bbox[3] - bbox[1]
            
            # Center label in piece
            label_x = piece_x + (piece_w - label_width) // 2
            label_y = piece_y + (piece_h - label_height) // 2
            draw.text((label_x, label_y), label, fill='black', font=small_font)
        
        # Draw waste area (hatched pattern)
        self._draw_waste_pattern(draw, board, board_x, board_y, 
                                board_visual_width, board_visual_height)
        
        return y_start + board_visual_height + 20
    
    def _draw_waste_pattern(self, draw, board: Board, board_x: int, board_y: int,
                           board_width: int, board_height: int):
        """Draw hatched pattern for waste areas"""
        # Create a simple hatching by drawing diagonal lines
        # This is simplified - a more sophisticated version would identify actual waste rectangles
        
        # Calculate occupied area as rectangles
        occupied = set()
        for piece in board.pieces:
            px_start = int(piece.x * self.scale)
            py_start = int(piece.y * self.scale)
            px_end = int((piece.x + piece.length) * self.scale)
            py_end = int((piece.y + piece.width) * self.scale)
            
            for x in range(px_start, px_end, 5):
                for y in range(py_start, py_end, 5):
                    occupied.add((x, y))
        
        # Draw hatching in waste areas (simplified)
        spacing = 10
        for i in range(0, board_width + board_height, spacing):
            x1 = board_x + i
            y1 = board_y
            x2 = board_x
            y2 = board_y + i
            
            # Only draw if in waste area (very simplified check)
            if i % (spacing * 2) == 0:  # Draw some hatch lines
                draw.line([(x1, y1), (x2, y2)], fill='gray', width=1)
