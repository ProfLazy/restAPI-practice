from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Define the FastAPI app
app = FastAPI()

# Define a Pydantic model for the a simple item with a price and name
class Item(BaseModel):
    id: int
    name: str
    price: float

# Database
items_db: List[Item] = []

def get_id(item: Item) -> int:
    return item.id

def get_name(item: Item) -> str:
    return item.name

def get_price(item: Item) -> float:
    return item.price

# This is the base route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Test Item Store API!"}

# Route to get all items
@app.get("/items/", response_model=List[Item])
def get_items():
    return items_db

# Route to get a specific item by ID
@app.get("/items/search/id/{item_id}", response_model=Item)
def get_item_id(item_id: int):

    for item in items_db:
        if get_id(item) == item_id:
            return item
        
    raise HTTPException(status_code=404, detail="Item not found")

# Route to get a specific item by name or partial name
@app.get("/items/search/name/{name}", response_model=List[Item])
def get_item_name(name: str):
    
    if not name:
        raise HTTPException(status_code=400, detail="Name parameter is required")
    
    results = None
    new_name = name.lower()

    for item in items_db:
        if new_name in get_name(item).lower():
            if results is None:
                results = []
            results.append(item)

    if results is None:
        raise HTTPException(status_code=404, detail="No items found matching the name")
    return results

# Route to create a new item
@app.post("/items/", response_model=Item)
def create_item(item: Item):
    for existing_item in items_db:
        if get_id(existing_item) == get_id(item):
            raise HTTPException(status_code=400, detail="Item with this ID already exists")
    
    items_db.append(item)
    return item

# Route to update an existing item
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):

    index = 0

    for item in items_db:
        if get_id(item) == item_id:
            items_db[index] = updated_item
            return updated_item
        index += 1
    
    raise HTTPException(status_code=404, detail="Item not found")

# Route to delete an item
@app.delete("/items/{item_id}")
def delete_item(item_id: int):

    index = 0

    for item in items_db:
        if get_id(item) == item_id:
            del items_db[index]
            return {"detail": "Item deleted successfully"}
        index += 1
    
    raise HTTPException(status_code=404, detail="Item not found")

# Route to get items within a price range
@app.get("/items/price-range/", response_model=List[Item])
def get_items_in_price_range(min_price: float, max_price: float):
    
    if min_price < 0 or max_price < 0:
        raise HTTPException(status_code=400, detail="Price values must be non-negative")
    
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="Minimum price cannot be greater than maximum price")
    
    results = None

    for item in items_db:
        item_price = get_price(item)
        if min_price <= item_price <= max_price:
            if results is None:
                results = []
            results.append(item)

    if results is None:
        raise HTTPException(status_code=404, detail="No items found in the specified price range")
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)