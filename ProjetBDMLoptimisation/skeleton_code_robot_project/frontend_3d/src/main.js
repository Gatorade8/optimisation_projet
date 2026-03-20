// main.js — 3D Pixel Pathfinding Visualizer (Gameboy Retro)
// Uses Three.js + InstancedMesh for voxel grid rendering
// Follows 3d-pixel-web skill: antialias:false, pixel font, CRT scanlines, limited palette

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { fetchGrids, fetchGrid, solvePath } from './api.js';
import './style.css';

// ========================
// GAMEBOY PALETTE
// ========================
const PALETTE = {
  darkest:  0x0f380f,  // Obstacles
  dark:     0x306230,  // Path highlights
  light:    0x8bac0f,  // Goal
  lightest: 0x9bbc0f,  // Start
  floor:    0x1a3a1a,  // Free cells
  explored: 0x1f4f1f,  // Explored cells (animation)
};

// ========================
// THREE.JS SETUP
// ========================
const canvas = document.getElementById('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x050f05);

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x050f05, 0.04);

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 200);
camera.position.set(8, 12, 14);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0, 0);
controls.maxPolarAngle = Math.PI / 2.2;

const clock = new THREE.Clock();

// --- Lighting (flat / stylized — no shadows) ---
const ambient = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambient);
const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(8, 15, 10);
scene.add(dirLight);

// --- Resize ---
function onResize() {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  // Render at half res for pixel look, CSS scales it up
  renderer.setSize(innerWidth / 2, innerHeight / 2);
  canvas.style.width = '100%';
  canvas.style.height = '100%';
}
window.addEventListener('resize', onResize);
onResize();

// ========================
// GRID STATE
// ========================
let currentGridData = null;
let gridMeshes = [];       // Array of individual meshes for color changes
let pathAnimationId = null; // For cancelling ongoing animation

// ========================
// BUILD 3D GRID
// ========================
function clearGrid() {
  // Cancel any running path animation
  if (pathAnimationId !== null) {
    clearTimeout(pathAnimationId);
    pathAnimationId = null;
  }
  // Remove old meshes
  gridMeshes.forEach(m => {
    scene.remove(m);
    m.geometry.dispose();
    m.material.dispose();
  });
  gridMeshes = [];
}

function buildGrid(gridData) {
  clearGrid();
  currentGridData = gridData;
  const { grid, rows, cols } = gridData;
  
  const offsetX = -(cols - 1) / 2;
  const offsetZ = -(rows - 1) / 2;

  const geo = new THREE.BoxGeometry(0.9, 0.9, 0.9);
  
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const cell = grid[y][x];
      let color;
      let height = 0;

      if (cell === 'X') {
        color = PALETTE.darkest;
        height = 1.5;  // Obstacles are taller
      } else if (cell === 'S') {
        color = PALETTE.lightest;
        height = 0;
      } else if (cell === 'G') {
        color = PALETTE.light;
        height = 0;
      } else {
        color = PALETTE.floor;
        height = 0;
      }

      const mat = new THREE.MeshStandardMaterial({
        color: color,
        roughness: 0.8,
        metalness: 0.1
      });
      
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(
        x + offsetX,
        height / 2,
        y + offsetZ
      );
      
      if (cell === 'X') {
        mesh.scale.y = 2.5;
        mesh.position.y = 0.7;
      }

      // Store grid coordinates on the mesh for lookup
      mesh.userData = { gx: x, gy: y, cellType: cell, originalColor: color };
      scene.add(mesh);
      gridMeshes.push(mesh);
    }
  }

  // Floating particles for ambiance
  addParticles(rows, cols);

  // Center camera on grid
  controls.target.set(0, 0, 0);
  const maxDim = Math.max(rows, cols);
  camera.position.set(maxDim * 0.8, maxDim * 1.2, maxDim * 1.0);
  controls.update();
}

// ========================
// AMBIENT PARTICLES
// ========================
let particlesMesh = null;

function addParticles(rows, cols) {
  if (particlesMesh) {
    scene.remove(particlesMesh);
    particlesMesh.geometry.dispose();
    particlesMesh.material.dispose();
  }
  
  const count = 80;
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const spread = Math.max(rows, cols) * 1.5;
  
  for (let i = 0; i < count; i++) {
    positions[i * 3]     = (Math.random() - 0.5) * spread;
    positions[i * 3 + 1] = Math.random() * 8 + 1;
    positions[i * 3 + 2] = (Math.random() - 0.5) * spread;
  }
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  
  const mat = new THREE.PointsMaterial({
    color: PALETTE.lightest,
    size: 0.12,
    transparent: true,
    opacity: 0.5,
  });
  
  particlesMesh = new THREE.Points(geo, mat);
  scene.add(particlesMesh);
}

// ========================
// PATH ANIMATION
// ========================
function getMeshAt(gx, gy) {
  return gridMeshes.find(m => m.userData.gx === gx && m.userData.gy === gy);
}

function resetPathColors() {
  if (pathAnimationId !== null) {
    clearTimeout(pathAnimationId);
    pathAnimationId = null;
  }
  gridMeshes.forEach(m => {
    m.material.color.setHex(m.userData.originalColor);
    if (m.userData.cellType !== 'X') {
      m.scale.y = 1;
      m.position.y = 0;
    }
  });
}

function animatePath(path, color, delay = 60) {
  return new Promise((resolve) => {
    let i = 0;
    function step() {
      if (i >= path.length) {
        resolve();
        return;
      }
      const [gx, gy] = path[i];
      const mesh = getMeshAt(gx, gy);
      if (mesh && mesh.userData.cellType !== 'S' && mesh.userData.cellType !== 'G') {
        mesh.material.color.setHex(color);
        // Small pop-up animation
        mesh.scale.y = 1.6;
        mesh.position.y = 0.25;
        // Settle back down
        setTimeout(() => {
          if (mesh) {
            mesh.scale.y = 1.3;
            mesh.position.y = 0.12;
          }
        }, delay * 2);
      }
      i++;
      pathAnimationId = setTimeout(step, delay);
    }
    step();
  });
}

// ========================
// UI INTERACTIONS
// ========================
const gridSelect = document.getElementById('grid-select');
const algoButtons = document.querySelectorAll('.algo-btn');
const runAllBtn = document.getElementById('run-all-btn');
const resultsDiv = document.getElementById('results');
const resultsList = document.getElementById('results-list');
const statusText = document.getElementById('status-text');

function getGeneticParams() {
  return {
    pop: parseInt(document.getElementById('gen-pop').value) || 30,
    chrom: parseInt(document.getElementById('gen-chrom').value) || 20,
    gen: parseInt(document.getElementById('gen-gen').value) || 4,
    mut: (parseFloat(document.getElementById('gen-mut').value) || 5) / 100.0,
    tour: parseInt(document.getElementById('gen-tour').value) || 3
  };
}

function setStatus(text) {
  statusText.textContent = text;
}

// Load grid list on startup
async function init() {
  try {
    setStatus('CONNEXION API...');
    const grids = await fetchGrids();
    gridSelect.innerHTML = '';
    grids.forEach(g => {
      const opt = document.createElement('option');
      opt.value = g;
      opt.textContent = g.replace('.txt', '').toUpperCase();
      gridSelect.appendChild(opt);
    });
    
    if (grids.length > 0) {
      await loadGrid(grids[0]);
    }
    setStatus('PRET. CHOISIR UN ALGO.');
  } catch (err) {
    setStatus('ERREUR: LANCER LE SERVEUR PYTHON !');
    console.error('API Error:', err);
  }
}

async function loadGrid(gridName) {
  setStatus('CHARGEMENT GRILLE...');
  const data = await fetchGrid(gridName);
  buildGrid(data);
  resultsDiv.classList.add('hidden');
  setStatus(`GRILLE: ${gridName.replace('.txt', '').toUpperCase()} (${data.rows}x${data.cols})`);
}

gridSelect.addEventListener('change', () => {
  loadGrid(gridSelect.value);
});

// Single algo run
algoButtons.forEach(btn => {
  btn.addEventListener('click', async () => {
    if (!currentGridData) return;
    const algo = btn.dataset.algo;
    
    // Visual feedback
    algoButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active', 'running');
    resetPathColors();
    
    setStatus(`CALCUL ${algo.toUpperCase()}...`);
    
    try {
      const params = algo === 'genetic' ? getGeneticParams() : null;
      const result = await solvePath(gridSelect.value, algo, params);
      btn.classList.remove('running');
      
      if (result.path && result.path.length > 0) {
        await animatePath(result.path, PALETTE.dark, 80);
        setStatus(`${algo.toUpperCase()}: ${result.length} PAS EN ${result.time.toFixed(6)}s`);
      } else {
        setStatus(`${algo.toUpperCase()}: AUCUN CHEMIN !`);
      }
      
      // Show single result
      showResults([result]);
    } catch (err) {
      btn.classList.remove('running');
      setStatus('ERREUR API !');
      console.error(err);
    }
  });
});

// Compare all
runAllBtn.addEventListener('click', async () => {
  if (!currentGridData) return;
  
  algoButtons.forEach(b => b.classList.remove('active'));
  resetPathColors();
  setStatus('COMPARAISON EN COURS...');
  
  try {
    const algos = ['greedy', 'astar', 'genetic'];
    const results = [];
    
    for (const algo of algos) {
      const params = algo === 'genetic' ? getGeneticParams() : null;
      const result = await solvePath(gridSelect.value, algo, params);
      results.push(result);
    }
    
    // Animate the best (shortest successful) path
    const successResults = results.filter(r => r.success);
    if (successResults.length > 0) {
      const best = successResults.reduce((a, b) => a.length < b.length ? a : b);
      await animatePath(best.path, PALETTE.dark, 60);
      setStatus(`MEILLEUR: ${best.algo.toUpperCase()} (${best.length} PAS)`);
    } else {
      setStatus('AUCUN ALGORITHME N\'A TROUVE !');
    }
    
    showResults(results);
  } catch (err) {
    setStatus('ERREUR API !');
    console.error(err);
  }
});

function showResults(results) {
  resultsDiv.classList.remove('hidden');
  resultsList.innerHTML = '';
  
  // Find best
  const successResults = results.filter(r => r.success);
  const bestLength = successResults.length > 0
    ? Math.min(...successResults.map(r => r.length))
    : -1;
  
  const algoNames = { greedy: 'GLOUTON', astar: 'A*', genetic: 'GENETIQUE' };
  
  results.forEach(r => {
    const row = document.createElement('div');
    row.className = 'result-row' + (r.length === bestLength && r.success ? ' winner' : '');
    row.innerHTML = `
      <span class="result-name">${algoNames[r.algo] || r.algo}</span>
      <span class="result-length">${r.length} PAS</span>
      <span class="result-time">${r.time.toFixed(6)}s</span>
      <span class="result-status ${r.success ? 'success' : 'fail'}">${r.success ? '✓ OK' : '✗ ECHEC'}</span>
    `;
    resultsList.appendChild(row);
  });
}

// ========================
// ANIMATION LOOP
// ========================
let floatTime = 0;

renderer.setAnimationLoop(() => {
  const delta = clock.getDelta();
  floatTime += delta;
  
  controls.update();
  
  // Subtle floating animation on Start and Goal cells
  gridMeshes.forEach(m => {
    if (m.userData.cellType === 'S' || m.userData.cellType === 'G') {
      m.position.y = Math.sin(floatTime * 2.5 + m.userData.gx + m.userData.gy) * 0.15;
    }
  });
  
  // Rotate particles
  if (particlesMesh) {
    particlesMesh.rotation.y += delta * 0.05;
  }
  
  renderer.render(scene, camera);
});

// ========================
// BOOT
// ========================
init();
