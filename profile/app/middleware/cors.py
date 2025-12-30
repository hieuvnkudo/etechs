from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app) -> None:
    """Setup CORS middleware cho ứng dụng"""
    
    # CORS settings - có thể config qua environment variables
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Trong production, nên lấy từ environment variables
    # allowed_origins = settings.cors_origins.split(",") if hasattr(settings, "cors_origins") else []
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

