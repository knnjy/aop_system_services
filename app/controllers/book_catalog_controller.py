import fastapi

# This controller is now deprecated - all book operations are handled by book_controller.py
# This file is kept for backward compatibility only

router = fastapi.APIRouter(prefix="/api/books")

