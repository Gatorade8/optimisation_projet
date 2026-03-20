// api.js — Service layer for the Python FastAPI backend

const API_BASE = 'http://localhost:8000';

/**
 * Fetch the list of available grid files from backend.
 * @returns {Promise<string[]>} Array of grid filenames
 */
export async function fetchGrids() {
  const res = await fetch(`${API_BASE}/grids`);
  if (!res.ok) throw new Error('Failed to fetch grids');
  const data = await res.json();
  return data.grids;
}

/**
 * Load a specific grid's layout data.
 * @param {string} gridName - Name of the grid file (e.g. "grid1.txt")
 * @returns {Promise<{grid: string[][], start: number[], goal: number[], rows: number, cols: number}>}
 */
export async function fetchGrid(gridName) {
  const res = await fetch(`${API_BASE}/grids/${gridName}`);
  if (!res.ok) throw new Error(`Failed to fetch grid: ${gridName}`);
  return res.json();
}

/**
 * Run a pathfinding algorithm on a grid via the Python backend.
 * @param {string} gridName - Name of the grid file
 * @param {string} algo - Algorithm key: "greedy", "astar", or "genetic"
 * @param {object} params - Optional parameters for the genetic algorithm
 * @returns {Promise<{algo: string, path: number[][], length: number, time: number, success: boolean}>}
 */
export async function solvePath(gridName, algo, params = null) {
  let url = `${API_BASE}/solve?grid_name=${gridName}&algo=${algo}`;
  if (params && algo === 'genetic') {
    url += `&pop_size=${params.pop}&chrom_length=${params.chrom}&generations=${params.gen}&mutation_rate=${params.mut}&tournament_size=${params.tour}`;
  }
  const res = await fetch(url, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to solve: ${algo} on ${gridName}`);
  return res.json();
}
