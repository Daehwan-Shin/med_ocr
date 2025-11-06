# Eyedrops OCR Matcher

## Overview
This is a FastAPI backend application that performs OCR (Optical Character Recognition) on images of Korean eyedrop and ointment products and matches them against a CSV database using fuzzy matching.

## Project Structure
- `main.py` - FastAPI application with API endpoints
- `src/ocr_engine.py` - PaddleOCR wrapper for Korean text recognition
- `src/matcher.py` - Fuzzy matching logic using rapidfuzz
- `src/preprocess.py` - Image preprocessing functions
- `data/eyedrops_oint.csv` - Product database (제품명/품목명)

## Technology Stack
- **Framework**: FastAPI 0.121.0
- **OCR**: PaddleOCR 3.3.1 (Korean language support)
- **Image Processing**: OpenCV 4.12.0
- **Fuzzy Matching**: rapidfuzz
- **Data**: pandas 2.3.3

## API Endpoints

### `POST /match`
Upload an image file for OCR and product matching.
- **Parameters**: 
  - `file`: Image file (multipart/form-data)
  - `topk`: Number of top matches to return (default: 5)
- **Returns**: JSON with matches, OCR lines, and candidates

### `POST /match_text`
Match text directly without OCR.
- **Parameters**:
  - `text`: Text lines separated by newlines
  - `topk`: Number of top matches to return (default: 5)
- **Returns**: JSON with matches, OCR lines, and candidates

### `GET /`
Health check endpoint.

## Setup Status
✅ Python 3.11 installed
✅ All dependencies installed successfully
✅ PaddlePaddle system library issue resolved (libgomp.so.1)
✅ Korean OCR models downloaded automatically
✅ Workflow configured on port 8000 with LD_LIBRARY_PATH
✅ Server running successfully with full OCR functionality
✅ CSV database loaded (997 products)

## Recent Changes (November 6, 2025)
- Fixed dependency conflicts (opencv-python version compatibility with PaddleOCR)
- Updated PaddleOCR initialization for newer API (v3.3.1)
- Resolved PaddlePaddle system dependency by setting LD_LIBRARY_PATH to include libgomp.so.1
- Added .gitignore for Python projects
- Configured backend workflow on port 8000
- Both `/match` and `/match_text` endpoints fully functional

## Development
The backend runs on port 8000 with auto-reload enabled. Access the API at:
- Development: `http://localhost:8000`
- Replit environment: Accessible through the Replit proxy

## API Usage Examples
```bash
# Test root endpoint
curl http://localhost:8000/

# Match from image
curl -X POST "http://localhost:8000/match" \
  -F "file=@sample.jpg" \
  -F "topk=5"

# Match from text
curl -X POST "http://localhost:8000/match_text" \
  -F "text=Line 1
Line 2
Line 3" \
  -F "topk=5"
```
