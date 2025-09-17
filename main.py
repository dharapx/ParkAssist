from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routers import user, admin, parking

origins = [
    "https://parkassistapi.dharapx.duckdns.org",
    "http://localhost:3000",  # for local development
]

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="ParkAssist API",
        version="1.0",
        description="API for ParkAssist",
        routes=app.routes,
    )
    # Override to use Bearer auth in Swagger UI
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="Parking Tracker API",
    description="API for tracking parking lot availability",
    version="0.0.1",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List your frontend domains here
    allow_credentials=True,
    allow_methods=["*"],    # Allow all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],    # Allow all headers
)
app.openapi = custom_openapi

app.include_router(user.router, prefix="/api/v1/user")
app.include_router(admin.router, prefix="/api/v1/admin")
app.include_router(parking.router, prefix="/api/v1/common/parking")
app.include_router(parking.router_guard, prefix="/api/v1/guard/parking")
app.include_router(parking.router_admin, prefix="/api/v1/admin/parking")