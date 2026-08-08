// static/app.js
let speedChart, pedalChart;
let selectedLapId = null;

window.addEventListener("DOMContentLoaded", () => {
    initCharts();
    fetchLaps();
    setInterval(fetchTelemetry, 16.7); // 1 second auto-refresh
});

function initCharts() {
    // 1. SPEED CHART (km/h)
    speedChart = new Chart(document.getElementById("speedChart"), {
        type: "line",
        data: { labels: [], datasets: [{ label: "Speed (km/h)", data: [], borderColor: "#ffd700", borderWidth: 2, pointRadius: 0 }] },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: "Lap Distance (m)", color: "#8b949e" }, ticks: { color: "#8b949e" } },
                y: { title: { display: true, text: "km/h", color: "#8b949e" }, ticks: { color: "#8b949e" } }
            },
            plugins: { legend: { labels: { color: "#e6edf3" } } }
        }
    });

    // 2. PEDALS CHART (Throttle & Brake strictly locked 0.0 - 1.0)
    pedalChart = new Chart(document.getElementById("pedalChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [
                { label: "Throttle %", data: [], borderColor: "#00ff66", borderWidth: 2, pointRadius: 0 },
                { label: "Brake %", data: [], borderColor: "#ff1744", borderWidth: 2, pointRadius: 0 }
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

        // Automatically select the most recent active lap
        if (data.laps.length > 0 && !selectedLapId) {
            selectedLapId = data.laps[0].lap_id;
            select.value = selectedLapId;
        }
    } catch (e) { 
        console.error("Error fetching laps:", e); 
    }
}

function onLapChange() {
    const select = document.getElementById("lapSelect");
    if (select) {
        selectedLapId = select.value;
        fetchTelemetry();
    }
}

async function fetchTelemetry() {
    if (!selectedLapId) return;

    try {
        const res = await fetch(`/api/telemetry/${selectedLapId}`);
        const data = await res.json();
        if (!data.lap_distance || data.lap_distance.length === 0) return;

        // Update KPI Cards safely if elements exist
        const kpiSpeed = document.getElementById("kpiSpeed");
        const kpiThrottle = document.getElementById("kpiThrottle");
        const kpiBrake = document.getElementById("kpiBrake");
        const kpiRows = document.getElementById("kpiRows");

        if (kpiSpeed) kpiSpeed.innerHTML = `${Math.max(...data.speed)} <small>km/h</small>`;
        if (kpiThrottle) kpiThrottle.innerHTML = `${Math.round(Math.max(...data.throttle) * 100)}%`;
        if (kpiBrake) kpiBrake.innerHTML = `${Math.round(Math.max(...data.brake) * 100)}%`;
        if (kpiRows) kpiRows.innerHTML = `${data.speed.length} rows`;

        // Update Steering Wheel Graphic safely if element exists
        const wheel = document.getElementById("steeringWheel");
        if (wheel && data.steer && data.steer.length > 0) {
            const lastSteer = data.steer[data.steer.length - 1];
            wheel.style.transform = `rotate(${lastSteer * 200}deg)`;
        }

        // Update 2D GPS Map Canvas safely if element exists
        const canvas = document.getElementById("mapCanvas");
        if (canvas && data.world_x && data.world_z && data.world_x.length > 0) {
            drawTrackMap(data.world_x, data.world_z, canvas);
        }

        // Update Chart Data
        const labels = data.lap_distance.map(d => Math.round(d));

        speedChart.data.labels = labels;
        speedChart.data.datasets[0].data = data.speed;
        speedChart.update("none");

        pedalChart.data.labels = labels;
        pedalChart.data.datasets[0].data = data.throttle;
        pedalChart.data.datasets[1].data = data.brake;
        pedalChart.update("none");

    } catch (e) { 
        console.error("Error fetching telemetry:", e); 
    }
}

function drawTrackMap(worldX, worldZ, canvas) {
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (worldX.length === 0) return;

    const minX = Math.min(...worldX), maxX = Math.max(...worldX);
    const minZ = Math.min(...worldZ), maxZ = Math.max(...worldZ);

    const scaleX = (canvas.width - 40) / (maxX - minX || 1);
    const scaleZ = (canvas.height - 40) / (maxZ - minZ || 1);

    ctx.beginPath();
    ctx.strokeStyle = "#00e5ff";
    ctx.lineWidth = 3;

    for (let i = 0; i < worldX.length; i++) {
        const x = 20 + (worldX[i] - minX) * scaleX;
        const z = 20 + (worldZ[i] - minZ) * scaleZ;

        if (i === 0) ctx.moveTo(x, z);
        else ctx.lineTo(x, z);
    }
    ctx.stroke();

    const lastIdx = worldX.length - 1;
    const currentX = 20 + (worldX[lastIdx] - minX) * scaleX;
    const currentZ = 20 + (worldZ[lastIdx] - minZ) * scaleZ;

    ctx.beginPath();
    ctx.arc(currentX, currentZ, 6, 0, 2 * Math.PI);
    ctx.fillStyle = "#ff1744";
    ctx.fill();
}