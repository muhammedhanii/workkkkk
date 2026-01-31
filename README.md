# Wood Cutting Optimizer

A production-ready web application for optimizing wood board cutting and generating professional AutoCUT-style reports.

## Features

- 📊 **Excel Upload**: Upload cutting requirements in Excel format with Arabic column names
- 🔧 **Smart Optimization**: 2D bin-packing algorithm with guillotine cuts
- 📐 **Rotation Constraints**: Support for length and width constraints
- 📈 **Professional Reports**: AutoCUT-style visual cutting layouts
- 🎯 **High Utilization**: Minimize waste by optimizing piece placement
- 🐳 **Docker Ready**: One-command deployment with Docker Compose

## Technology Stack

### Backend
- **Python 3.11** with FastAPI
- **Pandas** for Excel parsing
- **Pillow** for report generation
- **Guillotine algorithm** for bin packing

### Frontend
- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **React** for UI components

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- (Optional) Node.js 20+ and Python 3.11+ for local development

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd workkkkk
```

2. Start the application:
```bash
docker compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Running Locally

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Excel File Format

Your Excel file should contain the following columns:

| Column Name | Type | Description |
|------------|------|-------------|
| الاسم | Text | Part name |
| الطول | Number | Length in cm |
| العرض | Number | Width in cm |
| الكمية | Number | Quantity |
| شرط طول | Boolean | Length constraint (must align with board length) |
| شرط عرض | Boolean | Width constraint (must align with board width) |

### Example

| الاسم | الطول | العرض | الكمية | شرط طول | شرط عرض |
|------|------|------|--------|---------|---------|
| P1 | 59.3 | 114 | 1 | FALSE | FALSE |
| P2 | 77.5 | 114 | 2 | FALSE | FALSE |
| P3 | 56 | 110 | 1 | FALSE | FALSE |
| P4 | 75 | 27.5 | 2 | FALSE | FALSE |

## Board Specifications

- **Standard Board Size**: 240 cm × 120 cm (2400 mm × 1200 mm)
- **Thickness**: Informational only
- **Algorithm**: First-Fit Decreasing with guillotine cuts
- **Optimization**: Minimizes number of boards and maximizes utilization

## API Endpoints

### POST /api/calculate
Calculate cutting layout from Excel file.

**Request**: Multipart form data with Excel file

**Response**:
```json
{
  "success": true,
  "result": {
    "boards": [...],
    "total_boards": 2,
    "overall_utilization": 67.85,
    "rejected_pieces": []
  }
}
```

### POST /api/calculate/report
Calculate cutting layout and return visual report as PNG.

**Request**: Multipart form data with Excel file

**Response**: PNG image file

## Report Features

The generated reports include:

1. **Summary Section**
   - Material name and specifications
   - Total boards used
   - Overall utilization percentage

2. **Per-Board Details**
   - Board dimensions
   - Utilization percentage
   - Piece count table
   - Visual cutting layout with labels
   - Waste areas (hatched pattern)

3. **AutoCUT-Style Formatting**
   - Professional layout
   - Clear borders and spacing
   - Dimension labels on pieces
   - Easy to read and print

## Business Rules

1. Pieces are expanded based on quantity
2. Pieces exceeding board size are rejected
3. Pieces can rotate unless constrained by شرط طول or شرط عرض
4. Constrained pieces are placed first (higher priority)
5. Pieces are sorted by area (descending)
6. Algorithm minimizes the number of boards used
7. Waste areas are tracked and displayed

## Project Structure

```
.
├── backend/
│   ├── api/              # API routes
│   ├── models/           # Data models
│   ├── packing/          # Packing algorithms
│   ├── services/         # Business logic
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Backend container
├── frontend/
│   ├── app/              # Next.js app
│   ├── public/           # Static assets
│   ├── package.json      # Node dependencies
│   └── Dockerfile        # Frontend container
├── docker-compose.yml    # Docker orchestration
└── README.md            # This file
```

## Development

### Adding New Features

1. **Backend**: Add new routes in `backend/api/routes.py`
2. **Packing Algorithm**: Modify `backend/packing/guillotine.py`
3. **Report Generation**: Update `backend/services/report_generator.py`
4. **Frontend**: Edit `frontend/app/page.tsx`

### Testing

```bash
# Backend
cd backend
pytest  # (if tests are added)

# Frontend
cd frontend
npm run test  # (if tests are added)
```

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use, modify the port mappings in `docker-compose.yml`.

### Docker Build Issues
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

### CORS Issues
The backend is configured to allow all origins. For production, update the CORS settings in `backend/main.py`.

## License

This project is provided as-is for cutting optimization purposes.

## Support

For issues and questions, please create an issue in the repository.
