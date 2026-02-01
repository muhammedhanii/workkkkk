import pandas as pd
from typing import List
from models.schemas import Piece


class ExcelParser:
    """Parse Excel files with cutting piece data"""
    
    @staticmethod
    def parse_excel(file_path: str) -> List[Piece]:
        """
        Parse Excel file with columns:
        - الاسم (Name)
        - الطول (Length in cm)
        - العرض (Width in cm)
        - الكمية (Quantity)
        - شريط طول (Length constraint)
        - شريط عرض (Width constraint)
        """
        try:
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Map Arabic column names
            column_map = {
                'الاسم': 'name',
                'الطول': 'length',
                'العرض': 'width',
                'الكمية': 'quantity',
                'شريط طول': 'length_constraint',
                'شريط عرض': 'width_constraint',
                # Also support alternative names
                'شرط طول': 'length_constraint',
                'شرط عرض': 'width_constraint'
            }
            
            # Rename columns
            df = df.rename(columns=column_map)
            
            # Remove rows with missing essential data
            df = df.dropna(subset=['name', 'length', 'width', 'quantity'])
            
            # Convert to pieces
            pieces = []
            for _, row in df.iterrows():
                pieces.append(Piece(
                    name=str(row['name']),
                    length=float(row['length']),
                    width=float(row['width']),
                    quantity=int(row['quantity']),
                    length_constraint=bool(row.get('length_constraint', False)),
                    width_constraint=bool(row.get('width_constraint', False))
                ))
            
            return pieces
            
        except Exception as e:
            raise ValueError(f"Error parsing Excel file: {str(e)}")
