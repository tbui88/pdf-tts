# PDF to Audio Backend API

FastAPI backend service for converting PDF documents to audio using MiniMax TTS.

## Features

- 📄 PDF text extraction using multiple libraries (pdfplumber, PyMuPDF)
- 🎤 High-quality text-to-speech using MiniMax TTS API
- 🔧 Intelligent text chunking for optimal TTS processing
- 🎵 Audio file merging and processing
- ⚡ Async processing with progress tracking
- 🔐 Environment-based configuration
- 📦 Docker support for easy deployment

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the environment template and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your MiniMax API credentials:

```env
MINIMAX_API_KEY=your_api_key_here
MINIMAX_GROUP_ID=your_group_id_here
```

### 3. Run Development Server

```bash
python dev.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```http
GET /health
```

### Convert PDF to Audio
```http
POST /api/convert-pdf
Content-Type: multipart/form-data

file: [PDF file]
```

Response:
```json
{
  "job_id": "uuid-string",
  "message": "Conversion started",
  "status": "processing"
}
```

### Check Conversion Status
```http
GET /api/conversion-status/{job_id}
```

Response:
```json
{
  "status": "completed",
  "progress": 100,
  "message": "Conversion completed successfully!",
  "audioUrl": "/audio/job_id.mp3",
  "estimatedDuration": 120.5
}
```

### Download Audio
```http
GET /api/download-audio/{job_id}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MINIMAX_API_KEY` | MiniMax TTS API key | Required |
| `MINIMAX_GROUP_ID` | MiniMax group ID | Optional |
| `PORT` | Server port | 8000 |
| `HOST` | Server host | 0.0.0.0 |
| `DEBUG` | Debug mode | True |
| `MAX_FILE_SIZE_MB` | Max PDF file size | 50 |
| `MAX_CHUNK_SIZE` | Max text chunk size for TTS | 2000 |
| `DEFAULT_VOICE` | Default TTS voice | female-qn-qingse |

### TTS Voice Options

Available MiniMax voices:
- `female-qn-qingse` - Clear female voice (default)
- `male-qn-qingse` - Clear male voice
- `female-shaonv` - Young female voice
- `male-youthful` - Youthful male voice

## Deployment

### Docker

Build and run with Docker:

```bash
docker build -t pdf-to-audio-api .
docker run -p 8000:8000 --env-file .env pdf-to-audio-api
```

### Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Configure environment variables
5. Deploy using `render.yaml` configuration

### Railway

1. Push code to GitHub
2. Create new project on Railway
3. Connect repository
4. Configure environment variables
5. Deploy automatically

### Manual Deployment

For VPS or other platforms:

```bash
# Install dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y ffmpeg

# Run with gunicorn (production)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Architecture

### Processing Pipeline

1. **File Upload**: Validate and store PDF temporarily
2. **Text Extraction**: Extract text using pdfplumber/PyMuPDF
3. **Text Processing**: Clean and chunk text for optimal TTS
4. **TTS Conversion**: Convert text chunks to audio using MiniMax
5. **Audio Merging**: Combine audio chunks into final file
6. **Cleanup**: Remove temporary files

### Error Handling

- Graceful fallbacks for PDF extraction
- Retry logic for TTS API calls
- Mock audio generation for testing
- Comprehensive logging

### Performance Considerations

- Async processing for better concurrency
- Background tasks for long-running operations
- Efficient memory usage with streaming
- Rate limiting for TTS API

## Development

### Project Structure

```
pdf-to-audio-backend/
├── main.py              # FastAPI application
├── pdf_processor.py     # PDF text extraction
├── tts_service.py       # MiniMax TTS integration
├── audio_utils.py       # Audio processing utilities
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── Dockerfile          # Docker configuration
├── render.yaml         # Render deployment
└── railway.json        # Railway deployment
```

### Adding New Features

1. **New TTS Provider**: Implement interface in `tts_service.py`
2. **Audio Processing**: Extend `audio_utils.py`
3. **File Formats**: Add support in `pdf_processor.py`
4. **API Endpoints**: Add routes in `main.py`

### Testing

Run development server with debug mode:

```bash
DEBUG=True python dev.py
```

Test API endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Upload test PDF
curl -X POST "http://localhost:8000/api/convert-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.pdf"
```

## Troubleshooting

### Common Issues

1. **TTS API Errors**: Check API key and rate limits
2. **PDF Extraction Failed**: Try different PDF or check file corruption
3. **Audio Merge Failed**: Install ffmpeg or check file permissions
4. **Memory Issues**: Reduce chunk size or file size limits

### Logs

Check application logs for detailed error information:

```bash
tail -f logs/app.log
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation
- Open an issue on GitHub
