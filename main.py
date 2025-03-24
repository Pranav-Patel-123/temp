from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.customer_auth import customer_auth_router
from routes.owner_auth import owner_auth_router
from routes.products_crud import product_router
from routes.cart_crud import cart_router
from routes.orders_crud import order_router
from routes.category_crud import category_router

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Register Routes
app.include_router(customer_auth_router, prefix="/customer-auth", tags=["Customer Authentication"])
app.include_router(owner_auth_router, prefix="/owner-auth", tags=["Owner Authentication"])
app.include_router(product_router, prefix="/products", tags=["Product Management"])
app.include_router(cart_router, prefix="/cart", tags=["Cart Management"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
app.include_router(category_router, prefix="/category", tags=["Category Management"])

@app.get("/", tags=["Root"])
def home():
    return {"message": "Welcome to the E-commerce API"}

# Run the app when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
