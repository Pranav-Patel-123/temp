from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import category_crud, cart_crud, customer_auth, orders_crud, owner_auth, products_crud

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(category_crud.router)
app.include_router(cart_crud.router)
app.include_router(customer_auth.router)
app.include_router(orders_crud.router)
app.include_router(owner_auth.router)
app.include_router(products_crud.router)

@app.get("/")
def home():
    return {"message": "FastAPI App is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
