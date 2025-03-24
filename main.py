from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import Route Handlers
from routes.customer_auth import customer_auth_router
from routes.owner_auth import owner_auth_router
from routes.products_crud import product_router
from routes.cart_crud import cart_router
from routes.orders_crud import order_router
from routes.category_crud import category_router
from starlette.responses import RedirectResponse


# Initialize FastAPI app
app = FastAPI(
    title="E-commerce API",
    description="FastAPI Backend for E-commerce Platform",
    version="1.0",
    root_path="/",  # Explicitly set root path
    redirect_slashes=False  # Disable automatic trailing slash redirects
)


# CORS Middleware Configuration
ALLOWED_ORIGINS = [
    "https://e-commerce-owner-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
) 

# 🔹 Fix: Enforce HTTPS if request is incorrectly redirected
@app.middleware("http")
async def force_https_middleware(request: Request, call_next):
    """Ensure all requests use HTTPS to avoid Mixed Content errors."""
    if request.headers.get("x-forwarded-proto") == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(url))
    return await call_next(request)

# Register Routes
app.include_router(customer_auth_router, prefix="/customer-auth", tags=["Customer Authentication"])
app.include_router(owner_auth_router, prefix="/owner-auth", tags=["Owner Authentication"])
app.include_router(product_router, prefix="/products", tags=["Product Management"])
app.include_router(cart_router, prefix="/cart", tags=["Cart Management"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
app.include_router(category_router, prefix="/category", tags=["Category Management"])

# Root Endpoint
@app.get("/", tags=["Root"])
def home():
    return {"message": "Welcome to the E-commerce API - Secure & Optimized"}

# Run the app when executed directly
if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host=HOST, port=PORT)
