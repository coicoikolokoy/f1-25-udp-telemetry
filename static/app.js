// static/app.js
let speedChart, pedalChart;
let selectedLapId = null;

// LERP Steering Variables
let currentSteer = 0, targetSteer = 0;

// LERP 2D Map Coordinates Variables
let currentX = 0, currentZ = 0;
let targetX = 0, targetZ = 0;

// Offscreen Canvas Cache for 0-Lag Track Path
let offscreenCanvas = document.createElement("canvas");
offscreenCanvas.width = 300;
offscreenCanvas.height = 300;
let isMapCached = false;
let mapMinX = 0, mapMaxX = 0, mapMinZ = 0, mapMaxZ = 0;
let mapScaleX = 1, mapScaleZ = 1;

window.addEventListener("DOMContentLoaded", () => {
    initCharts();
    fetchLaps();
    setInterval(fetchTelemetry, 200);   // Background API fetch (5Hz)
    requestAnimationFrame(renderLoop);  // GPU Hardware Animation Loop (60Hz / 120Hz)
});

// Hardware-Accelerated 60Hz/120Hz GPU Render Loop
function renderLoop() {
    // 1. LERP Steering Wheel
    currentSteer += (targetSteer - currentSteer) * 0.15;
    const wheel = document.getElementById("steeringWheel");
    if (wheel) {
        wheel.style.transform = `rotate(${currentSteer * 200}deg)`;
    }

    // 2. LERP 2D Map Crimson Car Dot (Zero Array Loops!)
    currentX += (targetX - currentX) * 0.15;
    currentZ += (targetZ - currentZ) * 0.15;

    const mainCanvas = document.getElementById("mapCanvas");
    if (mainCanvas && isMapCached) {
        const ctx = mainCanvas.getContext("2d");
        ctx.clearRect(0, 0, mainCanvas.width, mainCanvas.height);

        // Draw cached track background image (Instant 0-CPU operation!)
        ctx.drawImage(offscreenCanvas, 0, 0);

        // Draw LERP Crimson Car Dot
        const carPixelX = 20 + (currentX - mapMinX) * mapScaleX;
        const carPixelZ = 20 + (currentZ - mapMinZ) * mapScaleZ;

        ctx.beginPath();
        ctx.arc(carPixelX, carPixelZ, 6, 0, 2 * Math.PI);
        ctx.fillStyle = "#ff1744";
        ctx.fill();
    }

    requestAnimationFrame(renderLoop);
}

function initCharts() {
    // 1. SPEED CHART
    speedChart = new Chart(document.getElementById("speedChart"), {
        type: "line",
        data: { 
            labels: [], 
            datasets: [{ label: "Speed (km/h)", data: [], borderColor: "#ffd700", borderWidth: 2, tension: 0.4, pointRadius: 0 }] 
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: "Lap Distance (m)", color: "#8b949e" }, ticks: { color: "#8b949e" } },
                y: { title: { display: true, text: "km/h", color: "#8b949e" }, ticks: { color: "#8b949e" } }
            },
            plugins: { legend: { labels: { color: "#e6edf3" } } }
        }
    });

    // 2. PEDALS CHART
    pedalChart = new Chart(document.getElementById("pedalChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [
                { label: "Throttle %", data: [], borderColor: "#00ff66", borderWidth: 2, tension: 0.2, pointRadius: 0 },
                { label: "Brake %", data: [], borderColor: "#ff1744", borderWidth: 2, tension: 0.2, pointRadius: 0 }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: "Lap Distance (m)", color: "#8b949e" }, ticks: { color: "#8b949e" } },
                y: { min: 0.0, max: 1.0, title: { display: true, text: "Pedal Position (0.0 - 1.0)", color: "#8b949e" }, ticks: { color: "#8b949e" } }
            },
            plugins: { legend: { labels: { color: "#e6edf3" } } }
        }
    });
}

async function fetchLaps() {
    try {
        const res = await fetch("/api/laps");
        const data = await res.json();
        const select = document.getElementById("lapSelect");
        if (!select) return;
        select.innerHTML = "";

        data.laps.forEach(lap => {
            const opt = document.createElement("option");
            opt.value = lap.lap_id;
            opt.textContent = `Lap Session #${lap.lap_id} (Lap ${lap.lap_number} - ${lap.track_name})`;
            select.appendChild(opt);
        });

        if (data.laps.length > 0 && !selectedLapId) {
            selectedLapId = data.laps[0].lap_id;
            select.value = selectedLapId;
        }
    } catch (e) { console.error("Error fetching laps:", e); }
}

function onLapChange() {
    const select = document.getElementById("lapSelect");
    if (select) {
        selectedLapId = select.value;
        isMapCached = false; // Reset map cache for new lap
        fetchTelemetry();
    }
}

async function fetchTelemetry() {
    if (!selectedLapId) return;

    try {
        const res = await fetch(`/api/telemetry/${selectedLapId}`);
        const data = await res.json();
        if (!data.lap_distance || data.lap_distance.length === 0) return;

        // Update KPI Cards
        const kpiSpeed = document.getElementById("kpiSpeed");
        const kpiThrottle = document.getElementById("kpiThrottle");
        const kpiBrake = document.getElementById("kpiBrake");
        const kpiRows = document.getElementById("kpiRows");

        if (kpiSpeed) kpiSpeed.innerHTML = `${Math.max(...data.speed)} <small>km/h</small>`;
        if (kpiThrottle) kpiThrottle.innerHTML = `${Math.round(Math.max(...data.throttle) * 100)}%`;
        if (kpiBrake) kpiBrake.innerHTML = `${Math.round(Math.max(...data.brake) * 100)}%`;
        if (kpiRows) kpiRows.innerHTML = `${data.speed.length} rows`;

        // Update Steering Target
        if (data.steer && data.steer.length > 0) {
            targetSteer = data.steer[data.steer.length - 1];
        }

        // Cache Track Path Line ONCE on Offscreen Canvas
        if (data.world_x && data.world_z && data.world_x.length > 0) {
            cacheTrackOutline(data.world_x, data.world_z);
            targetX = data.world_x[data.world_x.length - 1];
            targetZ = data.world_z[data.world_z.length - 1];
        }

        // Update Chart Data (Sliding Window max 200 points)
        const maxLivePoints = 200;
        const labels = data.lap_distance.slice(-maxLivePoints).map(d => Math.round(d));

        speedChart.data.labels = labels;
        speedChart.data.datasets[0].data = data.speed.slice(-maxLivePoints);
        speedChart.update("none");

        pedalChart.data.labels = labels;
        pedalChart.data.datasets[0].data = data.throttle.slice(-maxLivePoints);
        pedalChart.data.datasets[1].data = data.brake.slice(-maxLivePoints);
        pedalChart.update("none");

    } catch (e) { console.error("Error fetching telemetry:", e); }
}

// Pre-renders the cyan track outline ONCE onto an offscreen image
function cacheTrackOutline(worldX, worldZ) {
    const ctx = offscreenCanvas.getContext("2d");
    ctx.clearRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);

    mapMinX = Math.min(...worldX); mapMaxX = Math.max(...worldX);
    mapMinZ = Math.min(...worldZ); mapMaxZ = Math.max(...worldZ);

    mapScaleX = (offscreenCanvas.width - 40) / (mapMaxX - mapMinX || 1);
    mapScaleZ = (offscreenCanvas.height - 40) / (mapMaxZ - mapMinZ || 1);

    ctx.beginPath();
    ctx.strokeStyle = "#00e5ff";
    ctx.lineWidth = 3;

    for (let i = 0; i < worldX.length; i++) {
        const x = 20 + (worldX[i] - mapMinX) * mapScaleX;
        const z = 20 + (worldZ[i] - mapMinZ) * mapScaleZ;

        if (i === 0) ctx.moveTo(x, z);
        else ctx.lineTo(x, z);
    }
    ctx.stroke();

    isMapCached = true;
}