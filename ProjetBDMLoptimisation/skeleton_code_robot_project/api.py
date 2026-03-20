import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from grid import load_grid
from algorithms.greedy import greedy_search
from algorithms.astar import astar_search
from algorithms.genetic import genetic_search

app = FastAPI(title="Pathfinding Robot API")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRIDS_DIR = os.path.join(BASE_DIR, "..", "grid_datasets")

ALGOS = {
    "greedy": greedy_search,
    "astar": astar_search,
    "genetic": genetic_search,
}

@app.get("/grids")
def list_grids():
    """List all available grid names."""
    if not os.path.exists(GRIDS_DIR):
        return {"grids": []}
    
    grids = [
        f for f in os.listdir(GRIDS_DIR)
        if f.endswith(".txt")
    ]
    return {"grids": grids}

@app.get("/grids/{grid_name}")
def get_grid(grid_name: str):
    """Load and return the raw grid layout."""
    filepath = os.path.join(GRIDS_DIR, grid_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Grid not found")
    
    grid, start, goal = load_grid(filepath)
    return {
        "grid_name": grid_name,
        "grid": grid,
        "start": start,
        "goal": goal,
        "rows": len(grid),
        "cols": len(grid[0]) if grid else 0
    }

@app.post("/solve")
def solve_path(
    grid_name: str, 
    algo: str,
    pop_size: int = 30,
    chrom_length: int = 20,
    generations: int = 4,
    mutation_rate: float = 0.05,
    tournament_size: int = 3,
    stagnation_limit: int = 5
):
    """Run a specific algorithm on a specific grid."""
    if algo not in ALGOS:
        raise HTTPException(status_code=400, detail="Algorithm not supported")
        
    filepath = os.path.join(GRIDS_DIR, grid_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Grid not found")
        
    grid, start, goal = load_grid(filepath)
    algo_fn = ALGOS[algo]
    
    debut = time.perf_counter()
    if algo == "genetic":
        path = algo_fn(
            grid, start, goal, 
            pop_size=pop_size, 
            chrom_length=chrom_length, 
            generations=generations, 
            mutation_rate=mutation_rate, 
            tournament_size=tournament_size,
            stagnation_limit=stagnation_limit
        )
    else:
        path = algo_fn(grid, start, goal)
    temps = time.perf_counter() - debut
    
    return {
        "algo": algo,
        "path": path,
        "length": len(path) if path else 0,
        "time": temps,
        "success": bool(path and path[-1] == goal)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
