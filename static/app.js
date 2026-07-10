const state = {
  meta: null,
  latestPayload: null,
  latestResult: null,
  checklistCosts: {}
};

const form = document.querySelector("#predict-form");
const tuneInput = form.elements.tune_level;
const tuneValue = document.querySelector("#tune-value");
const engineSelect = form.elements.engine_code;
const chassisSelect = form.elements.chassis_code;
const engineImg = document.querySelector("#engine-img");
const chassisImg = document.querySelector("#chassis-img");
const engineLabel = document.querySelector("#engine-label");
const chassisLabel = document.querySelector("#chassis-label");

const sandboxToggle = document.querySelector("#sandbox-toggle");
const sandboxFields = document.querySelector("#sandbox-fields");
const catalogEngineSelect = document.querySelector("#catalog-engine-select");
const catalogChassisSelect = document.querySelector("#catalog-chassis-select");

function formatFeature(name) {
  return name.replaceAll("_", " ").replace(/\b\w/g, l => l.toUpperCase());
}

// Show/Hide custom sandbox inputs
sandboxToggle.addEventListener("change", () => {
  const active = sandboxToggle.checked;
  sandboxFields.style.display = active ? "grid" : "none";
  catalogEngineSelect.style.display = active ? "none" : "block";
  catalogChassisSelect.style.display = active ? "none" : "block";
  updateVisuals();
});

function updateVisuals() {
  if (sandboxToggle.checked) {
    engineImg.src = '/engine_img.webp';
    engineLabel.textContent = form.elements.custom_engine_name.value || "Custom Engine";
    chassisImg.src = '/car_img.webp';
    chassisLabel.textContent = form.elements.custom_chassis_name.value || "Custom Chassis";
    return;
  }

  if (!state.meta) return;
  const engine = state.meta.engines.find(e => e.code === engineSelect.value);
  const chassis = state.meta.chassis.find(c => c.code === chassisSelect.value);

  if (engine) {
    engineImg.src = engine.image || '/engine_img.webp';
    engineLabel.textContent = engine.name;
    engineImg.style.transform = 'scale(1.02)';
    setTimeout(() => engineImg.style.transform = '', 200);
  }
  if (chassis) {
    chassisImg.src = chassis.image || '/car_img.webp';
    chassisLabel.textContent = chassis.name;
    chassisImg.style.transform = 'scale(1.02)';
    setTimeout(() => chassisImg.style.transform = '', 200);
  }
}

engineSelect.addEventListener("change", updateVisuals);
chassisSelect.addEventListener("change", updateVisuals);

// Hook sandbox input changes to update visuals live
form.elements.custom_engine_name.addEventListener("input", updateVisuals);
form.elements.custom_chassis_name.addEventListener("input", updateVisuals);

function payloadFromForm() {
  if (sandboxToggle.checked) {
    return {
      engine_code: "CUSTOM",
      chassis_code: "CUSTOM",
      tune_level: Number(tuneInput.value),
      cooling_capacity_index: Number(form.elements.cooling_capacity_index.value),
      tire_grip_index: Number(form.elements.tire_grip_index.value),
      suspension_index: Number(form.elements.suspension_index.value),
      gear_ratio: Number(form.elements.gear_ratio.value),
      donor_engine_overrides: {
        name: form.elements.custom_engine_name.value,
        displacement_l: Number(form.elements.custom_displacement_l.value),
        cylinders: Number(form.elements.custom_cylinders.value),
        compression_ratio: Number(form.elements.custom_compression_ratio.value),
        engine_weight_kg: Number(form.elements.custom_engine_weight_kg.value),
        base_hp: Number(form.elements.custom_base_hp.value),
        base_torque_nm: Number(form.elements.custom_base_torque_nm.value),
        forced_induction: Number(form.elements.custom_forced_induction.value),
        layout: form.elements.custom_layout.value,
        donor_mount_width_mm: Number(form.elements.custom_donor_mount_width_mm.value)
      },
      recipient_chassis_overrides: {
        name: form.elements.custom_chassis_name.value,
        recipient_weight_kg: Number(form.elements.custom_recipient_weight_kg.value),
        stock_hp: Number(form.elements.custom_stock_hp.value),
        engine_bay_width_mm: Number(form.elements.custom_engine_bay_width_mm.value),
        wheelbase_mm: Number(form.elements.custom_wheelbase_mm.value),
        drag_coefficient: Number(form.elements.custom_drag_coefficient.value),
        stock_gear_ratio: Number(form.elements.custom_stock_gear_ratio.value),
        drivetrain: form.elements.custom_drivetrain.value
      }
    };
  }

  return {
    engine_code: engineSelect.value,
    chassis_code: chassisSelect.value,
    tune_level: Number(tuneInput.value),
    cooling_capacity_index: Number(form.elements.cooling_capacity_index.value),
    tire_grip_index: Number(form.elements.tire_grip_index.value),
    suspension_index: Number(form.elements.suspension_index.value),
    gear_ratio: Number(form.elements.gear_ratio.value),
  };
}

async function api(path, options = {}) {
  try {
    const response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  } catch (err) {
    console.error(err);
    throw err;
  }
}

function renderMeta(meta) {
  engineSelect.innerHTML = meta.engines.map((engine) => `<option value="${engine.code}">${engine.name}</option>`).join("");
  chassisSelect.innerHTML = meta.chassis.map((chassis) => `<option value="${chassis.code}">${chassis.name}</option>`).join("");
  
  engineSelect.value = "K24A";
  chassisSelect.value = "MX5_NA";

  document.querySelector("#algorithms").innerHTML = meta.algorithms
    .map((algorithm) => {
      const score = algorithm.demo_r2 ? `Demo R² = ${algorithm.demo_r2}` : `Slide R² = ${algorithm.slide_r2}`;
      return `
        <article class="algo">
          <p class="muted eyebrow" style="margin-bottom:8px">${algorithm.tag}</p>
          <h3>${algorithm.name}</h3>
          <p style="color:var(--accent-primary); font-weight:800; margin:10px 0;">${score}</p>
          <p class="muted" style="font-size:0.9rem">${algorithm.description}</p>
        </article>
      `;
    })
    .join("");

  document.querySelector("#datasets").innerHTML = meta.data_sources
    .map((dataset) => `
      <article class="dataset">
        <h3 style="margin-bottom:8px">${dataset.name}</h3>
        <p class="muted" style="font-size:0.9rem; margin-bottom:8px;">${dataset.source} | ${dataset.records}</p>
        <p style="font-size:0.95rem">${dataset.key_features}</p>
      </article>
    `)
    .join("");
    
  updateVisuals();
}

function renderPrediction(result) {
  state.latestResult = result;

  const cards = [
    ["Horsepower", result.predictions.horsepower, "hp", result.confidence_intervals.horsepower],
    ["Torque", result.predictions.torque_nm, "Nm", result.confidence_intervals.torque_nm],
    ["0-60 mph", result.predictions.zero_to_sixty_s, "s", result.confidence_intervals.zero_to_sixty_s],
  ];
  
  document.querySelector("#prediction-cards").innerHTML = cards
    .map(([label, value, unit, interval]) => `
      <article class="metric">
        <span class="muted" style="font-weight:600">${label}</span>
        <strong>${value} <span style="font-size:0.5em;color:var(--text-muted)">${unit}</span></strong>
        <small class="muted" style="display:block;margin-top:10px;font-size:0.8rem">Confidence: ${interval.low} - ${interval.high}</small>
      </article>
    `)
    .join("");

  const score = result.compatibility.score;
  const labelColor = score >= 82 ? 'var(--accent-primary)' : score >= 68 ? '#10b981' : score >= 52 ? 'var(--accent-tertiary)' : 'var(--accent-secondary)';
  
  document.querySelector("#compatibility").innerHTML = `
    <div class="metric" style="padding:0; border:none; background:transparent">
      <div style="display:flex; justify-content:space-between; align-items:flex-end">
        <span style="color:${labelColor}; font-weight:800; font-size:1.2rem">${result.compatibility.label}</span>
        <strong style="margin:0; font-size:2.5rem">${score}<span style="font-size:0.5em;color:var(--text-muted)">/100</span></strong>
      </div>
      <div class="bar"><span style="width: ${score}%; background: ${labelColor}"></span></div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:20px; font-size:0.9rem">
        ${Object.entries(result.compatibility.breakdown)
          .map(([key, value]) => `<div><span class="muted">${formatFeature(key)}</span><br><b style="color:#fff">${value}</b></div>`)
          .join("")}
      </div>
    </div>
  `;

  document.querySelector("#importance").innerHTML = result.feature_importance
    .map((item) => `
      <div style="margin-bottom:12px">
        <div style="display:flex; justify-content:space-between; font-size:0.9rem; margin-bottom:4px">
          <b>${formatFeature(item.feature)}</b> 
          <span style="color:var(--accent-primary); font-weight:bold">${item.percent}%</span>
        </div>
        <div class="bar" style="margin:0; height:6px"><span style="width: ${item.percent}%"></span></div>
      </div>
    `)
    .join("");

  document.querySelector("#tips").innerHTML = result.tuning_tips.map((tip) => `<li>${tip}</li>`).join("");
  
  // Render Dyno Graph
  renderDynoGraph(result);
  
  // Render Fitment Clearance Checklists
  renderClearanceDiagnostics(result);
  
  // Setup build checklist cost items
  setupBuildChecklist(result);

  // Reset drag strip car
  resetDragStrip();

  // Animate results
  const resultGrid = document.querySelectorAll('.result-grid .panel');
  resultGrid.forEach(panel => {
    panel.style.animation = 'none';
    panel.offsetHeight; // trigger reflow
    panel.style.animation = null; 
  });
}

function renderComparison(result) {
  document.querySelector("#comparison").innerHTML = result.candidates
    .map((candidate) => `
      <article class="candidate">
        <strong>#${candidate.rank}</strong>
        <span style="font-weight:700">${candidate.engine.name}</span>
        <span>${candidate.predictions.horsepower} hp</span>
        <span>${candidate.predictions.torque_nm} Nm</span>
        <span>${candidate.predictions.zero_to_sixty_s}s</span>
        <span style="color:var(--accent-primary); font-weight:bold">${candidate.compatibility_score}/100</span>
      </article>
    `)
    .join("");
    
  document.querySelector("#comparison").scrollIntoView({behavior: 'smooth', block: 'nearest'});
}

// Extrapolate Torque and HP curves dynamically
function getTorqueFactor(rpm, rpmPeak) {
  if (rpm < rpmPeak) {
    return 0.65 + 0.35 * (1 - Math.pow((rpmPeak - rpm) / (rpmPeak - 1000), 2));
  } else {
    return 1.0 - 0.45 * Math.pow((rpm - rpmPeak) / (8000 - rpmPeak), 1.6);
  }
}

function renderDynoGraph(result) {
  const hp = result.predictions.horsepower;
  const torque = result.predictions.torque_nm;
  
  const isForced = result.engineered_features.forced_induction > 0.5;
  const cylinders = result.engineered_features.cylinders;
  const rpmPeak = isForced ? 4200 : cylinders >= 8 ? 3600 : 5800;

  // Generate data points
  const points = [];
  for (let rpm = 1000; rpm <= 8000; rpm += 100) {
    const tFactor = getTorqueFactor(rpm, rpmPeak) + (Math.sin(rpm / 400) * 0.01);
    const rpmTorque = torque * tFactor;
    const rpmHp = (rpmTorque * rpm) / 7121;
    points.push({ rpm, torque: rpmTorque, hp: rpmHp });
  }

  // Rescale curves to fit predicted peaks perfectly
  const maxTorqueVal = Math.max(...points.map(p => p.torque));
  const maxHpVal = Math.max(...points.map(p => p.hp));
  
  const tScale = torque / maxTorqueVal;
  const hScale = hp / maxHpVal;

  points.forEach(p => {
    p.torque = p.torque * tScale;
    p.hp = p.hp * hScale;
  });

  // Render on SVG
  const svg = document.getElementById("dyno-svg");
  const width = 500;
  const height = 280;
  const padL = 45;
  const padR = 45;
  const padT = 20;
  const padB = 30;
  
  const graphW = width - padL - padR;
  const graphH = height - padT - padB;

  // Maximum scales for axes
  const maxHpScale = Math.ceil(hp * 1.2 / 50) * 50;
  const maxTorqueScale = Math.ceil(torque * 1.2 / 50) * 50;

  const getX = (rpm) => padL + ((rpm - 1000) / 7000) * graphW;
  const getYHp = (val) => padT + graphH - (val / maxHpScale) * graphH;
  const getYTorque = (val) => padT + graphH - (val / maxTorqueScale) * graphH;

  // Build grid lines
  let gridLines = "";
  // X grid lines (RPM)
  for (let rpm = 2000; rpm <= 8000; rpm += 1000) {
    const x = getX(rpm);
    gridLines += `<line class="dyno-grid-line" x1="${x}" y1="${padT}" x2="${x}" y2="${padT + graphH}"></line>`;
    gridLines += `<text x="${x}" y="${height - 10}" fill="var(--text-muted)" font-size="9" text-anchor="middle">${rpm/1000}k</text>`;
  }
  // Y grid lines
  for (let i = 1; i <= 4; i++) {
    const ratio = i / 4;
    const y = padT + graphH * (1 - ratio);
    gridLines += `<line class="dyno-grid-line" x1="${padL}" y1="${y}" x2="${width - padR}" y2="${y}"></line>`;
    
    // Left axis (HP) label
    const hpVal = Math.round(maxHpScale * ratio);
    gridLines += `<text x="${padL - 8}" y="${y + 3}" fill="var(--accent-secondary)" font-size="9" text-anchor="end">${hpVal}</text>`;
    
    // Right axis (Torque) label
    const tVal = Math.round(maxTorqueScale * ratio);
    gridLines += `<text x="${width - padR + 8}" y="${y + 3}" fill="var(--accent-primary)" font-size="9" text-anchor="start">${tVal}</text>`;
  }

  // Draw curves
  const hpPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(p.rpm)} ${getYHp(p.hp)}`).join(' ');
  const torquePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(p.rpm)} ${getYTorque(p.torque)}`).join(' ');

  svg.innerHTML = `
    <!-- Grid -->
    ${gridLines}
    <!-- Curves -->
    <path class="dyno-curve-hp" d="${hpPath}"></path>
    <path class="dyno-curve-torque" d="${torquePath}"></path>
    <!-- Axis titles -->
    <text x="${padL - 10}" y="${padT - 8}" fill="var(--accent-secondary)" font-size="8" font-weight="bold" text-anchor="end">Power (hp)</text>
    <text x="${width - padR + 10}" y="${padT - 8}" fill="var(--accent-primary)" font-size="8" font-weight="bold" text-anchor="start">Torque (Nm)</text>
    <text x="${width / 2}" y="${height - 2}" fill="var(--text-muted)" font-size="9" text-anchor="middle">RPM</text>
    <!-- Interactive crosshair -->
    <line id="dyno-v-line" class="dyno-crosshair" x1="0" y1="${padT}" x2="0" y2="${padT + graphH}" style="display:none;"></line>
    <circle id="dyno-dot-hp" cx="0" cy="0" r="4" fill="var(--accent-secondary)" style="display:none;"></circle>
    <circle id="dyno-dot-torque" cx="0" cy="0" r="4" fill="var(--accent-primary)" style="display:none;"></circle>
  `;

  // Bind Sweep Slider
  const rpmSweep = document.getElementById("dyno-rpm-sweep");
  const rpmValue = document.getElementById("dyno-rpm-value");
  
  function updateSweepLine() {
    const val = Number(rpmSweep.value);
    rpmValue.textContent = val.toLocaleString();
    
    // Find matching point
    const closest = points.find(p => p.rpm >= val) || points[points.length - 1];
    
    const x = getX(closest.rpm);
    const yHp = getYHp(closest.hp);
    const yT = getYTorque(closest.torque);

    const vLine = document.getElementById("dyno-v-line");
    const dotHp = document.getElementById("dyno-dot-hp");
    const dotT = document.getElementById("dyno-dot-torque");
    const tooltip = document.getElementById("dyno-tooltip");

    if (vLine && dotHp && dotT) {
      vLine.setAttribute("x1", x);
      vLine.setAttribute("x2", x);
      vLine.style.display = "block";

      dotHp.setAttribute("cx", x);
      dotHp.setAttribute("cy", yHp);
      dotHp.style.display = "block";

      dotT.setAttribute("cx", x);
      dotT.setAttribute("cy", yT);
      dotT.style.display = "block";
    }

    // Position and content tooltip
    if (tooltip) {
      tooltip.style.left = `${x - 60}px`;
      tooltip.style.top = `${yHp - 65}px`;
      tooltip.style.display = "block";
      tooltip.innerHTML = `
        <b style="color:#fff">${closest.rpm} RPM</b><br>
        <span style="color:var(--accent-secondary)">Power: ${Math.round(closest.hp)} hp</span><br>
        <span style="color:var(--accent-primary)">Torque: ${Math.round(closest.torque)} Nm</span>
      `;
    }
  }

  rpmSweep.addEventListener("input", updateSweepLine);
  updateSweepLine();
}

// Virtual Drag Strip Simulation
let dragInterval = null;
function resetDragStrip() {
  if (dragInterval) clearInterval(dragInterval);
  
  const car = document.getElementById("drag-car");
  car.style.transition = 'none';
  car.style.left = "10px";
  car.style.transform = "scale(1)";
  
  // Reset tree lights
  document.getElementById("light-stage").style.backgroundColor = "#334155";
  document.getElementById("light-amber-1").style.backgroundColor = "#334155";
  document.getElementById("light-amber-2").style.backgroundColor = "#334155";
  document.getElementById("light-green").style.backgroundColor = "#334155";
  
  // Reset timeslip fields
  document.getElementById("slip-rt").textContent = "-.--- s";
  document.getElementById("slip-60ft").textContent = "-.--- s";
  document.getElementById("slip-18mile").textContent = "-.--- s @ --.- mph";
  document.getElementById("slip-14mile").textContent = "-.--- s @ --.- mph";
  document.getElementById("slip-0-60").textContent = "-.-- s";

  document.getElementById("drag-launch-btn").disabled = false;
}

document.getElementById("drag-reset-btn").addEventListener("click", resetDragStrip);

document.getElementById("drag-launch-btn").addEventListener("click", () => {
  if (!state.latestResult) return;
  
  const btn = document.getElementById("drag-launch-btn");
  btn.disabled = true;
  
  const car = document.getElementById("drag-car");
  const z60 = state.latestResult.predictions.zero_to_sixty_s;
  
  // Extrapolate timeslip metrics
  const rt = 0.150 + Math.random() * 0.120;
  const slip60ft = 1.25 + 0.16 * z60;
  const slip18t = 1.6 + 0.65 * z60;
  const slip18s = 158 - 11.5 * z60;
  const slip14t = 2.2 + 1.55 * z60;
  const slip14s = 216 - 17 * z60;

  // 1. Christmas Tree Countdown sequence
  setTimeout(() => {
    document.getElementById("light-stage").style.backgroundColor = "var(--accent-tertiary)";
  }, 200);

  setTimeout(() => {
    document.getElementById("light-amber-1").style.backgroundColor = "var(--accent-tertiary)";
  }, 600);

  setTimeout(() => {
    document.getElementById("light-amber-2").style.backgroundColor = "var(--accent-tertiary)";
  }, 1000);

  setTimeout(() => {
    document.getElementById("light-green").style.backgroundColor = "#10b981";
    
    // Launch Car!
    const startTime = Date.now();
    const duration = 2500; // Animation duration in ms (scaled)
    
    car.style.transition = `left ${duration}ms cubic-bezier(0.42, 0, 0.58, 1)`;
    car.style.left = "calc(100% - 70px)";
    
    // Animate subtle chassis squat on acceleration
    car.style.transform = "scaleY(0.93) scaleX(1.05)";
    setTimeout(() => {
      car.style.transform = "scale(1)";
    }, 400);

    // Live timeslip ticker
    const startTicks = Date.now();
    dragInterval = setInterval(() => {
      const elapsed = (Date.now() - startTicks) / 1000;
      const raceTime = elapsed * (slip14t / 2.5); // Map animation to real race time
      
      if (raceTime >= slip60ft) {
        document.getElementById("slip-60ft").textContent = `${slip60ft.toFixed(3)} s`;
      }
      if (raceTime >= z60) {
        document.getElementById("slip-0-60").textContent = `${z60.toFixed(2)} s`;
      }
      if (raceTime >= slip18t) {
        document.getElementById("slip-18mile").textContent = `${slip18t.toFixed(3)} s @ ${slip18s.toFixed(1)} mph`;
      }
      
      if (elapsed >= 2.5) {
        clearInterval(dragInterval);
        document.getElementById("slip-rt").textContent = `${rt.toFixed(3)} s`;
        document.getElementById("slip-60ft").textContent = `${slip60ft.toFixed(3)} s`;
        document.getElementById("slip-0-60").textContent = `${z60.toFixed(2)} s`;
        document.getElementById("slip-18mile").textContent = `${slip18t.toFixed(3)} s @ ${slip18s.toFixed(1)} mph`;
        document.getElementById("slip-14mile").textContent = `${slip14t.toFixed(3)} s @ ${slip14s.toFixed(1)} mph`;
      }
    }, 50);

  }, 1400);
});

// Fitment & Diagnostic Clearance Panel
function renderClearanceDiagnostics(result) {
  const cylinders = result.engineered_features.cylinders;
  const layout = result.engineered_features.drivetrain_match; 
  const difficulty = result.engineered_features.swap_difficulty_index;
  const cooling = result.engineered_features.cooling_capacity_index;
  const suspension = result.engineered_features.suspension_index;
  
  const isForced = result.engineered_features.forced_induction > 0.5;
  const engineBayWidth = result.engineered_features.recipient_weight_kg > 1300 ? 790 : 720; // estimate engine bay width

  // Diagnostics items
  const clearanceList = [];

  // 1. Geometry clearance check
  const mountWidth = cylinders >= 8 ? 760 : cylinders >= 6 ? 720 : 660;
  const clearanceSpace = engineBayWidth - mountWidth;
  if (clearanceSpace >= 100) {
    clearanceList.push({
      title: "Engine Bay Clearance",
      desc: `Generous width margins (est. +${clearanceSpace}mm clearance). Direct-drop geometry.`,
      status: "green"
    });
  } else if (clearanceSpace >= 40) {
    clearanceList.push({
      title: "Engine Bay Clearance",
      desc: `Tight side clearance (est. +${clearanceSpace}mm). Slim cooling fans and custom manifolds required.`,
      status: "yellow"
    });
  } else {
    clearanceList.push({
      title: "Engine Bay Clearance",
      desc: `Extreme fitment hazard (est. +${clearanceSpace}mm clearance). Steering column relocation or frame modification required.`,
      status: "red"
    });
  }

  // 2. Drivetrain match check
  if (layout >= 0.9) {
    clearanceList.push({
      title: "Drivetrain Linkage",
      desc: "Chassis layout matches donor layout. Direct gearbox housing tunnel alignment.",
      status: "green"
    });
  } else {
    clearanceList.push({
      title: "Drivetrain Linkage",
      desc: "Chassis layout mismatch. Requires gearbox swap, custom bellhousing adapter plate, and transmission tunnel welding.",
      status: "red"
    });
  }

  // 3. Electrical / ECU complexity
  if (isForced) {
    clearanceList.push({
      title: "Wiring & Electronics",
      desc: "Forced induction swap requires standalone ECU wiring, custom MAP sensor routing, and intercooler piping maps.",
      status: "yellow"
    });
  } else {
    clearanceList.push({
      title: "Wiring & Electronics",
      desc: "Naturally aspirated wiring. Simpler sub-harness pinouts.",
      status: "green"
    });
  }

  // 4. Weight distribution impact
  if (difficulty >= 0.70) {
    clearanceList.push({
      title: "Weight Distribution Balance",
      desc: "Heavy front-end load shift. Front spring rates must be stiffened by 20-30% to prevent suspension bottoming.",
      status: "red"
    });
  } else if (difficulty >= 0.45) {
    clearanceList.push({
      title: "Weight Distribution Balance",
      desc: "Minor front weight bias shift. Adjustable coilovers recommended to balance corner weights.",
      status: "yellow"
    });
  } else {
    clearanceList.push({
      title: "Weight Distribution Balance",
      desc: "Excellent chassis balance preserved. Front-to-rear distribution shift is under 2.5%.",
      status: "green"
    });
  }

  document.getElementById("clearance-diagnostics").innerHTML = clearanceList.map(item => `
    <div class="clearance-item">
      <div class="clearance-badge clearance-${item.status}">
        ${item.status === 'green' ? '✓' : item.status === 'yellow' ? '⚠' : '✗'}
      </div>
      <div>
        <strong style="color:#fff; font-size:0.9rem">${item.title}</strong>
        <p class="muted" style="font-size:0.8rem; margin-top:2px">${item.desc}</p>
      </div>
    </div>
  `).join("");
}

// Checklist & Budget Estimator
function setupBuildChecklist(result) {
  const difficulty = result.engineered_features.swap_difficulty_index;
  const layout = result.engineered_features.drivetrain_match;
  const cooling = result.engineered_features.cooling_capacity_index;
  const suspension = result.engineered_features.suspension_index;
  const cylinders = result.engineered_features.cylinders;

  const items = [
    {
      id: "mounts",
      title: "Fabricate Engine Mounts",
      desc: "Custom heavy-duty steel mounting brackets and bushings.",
      cost: Math.round(250 + difficulty * 350)
    },
    {
      id: "adapter",
      title: layout >= 0.9 ? "Gearbox Mounting & Bushings" : "Gearbox Adapter Plate & Driveshaft",
      desc: layout >= 0.9 ? "Standard alignment mounts." : "Custom driveshaft machining and bellhousing plate.",
      cost: layout >= 0.9 ? 180 : 850
    },
    {
      id: "ecu",
      title: "Standalone ECU & Wire Harness",
      desc: "Stand-alone ECU unit, custom sub-harness pinouts, sensor wiring.",
      cost: Math.round(450 + cylinders * 100)
    },
    {
      id: "cooling",
      title: cooling < 0.70 ? "Upgrade Triple-Core Aluminum Radiator" : "Cooling Hose Adapter kit",
      desc: cooling < 0.70 ? "Upgraded core radiator with high CFM fans." : "Custom aluminum hose adapter joints.",
      cost: cooling < 0.70 ? 450 : 90
    },
    {
      id: "tuning",
      title: "Professional Dyno Calibration",
      desc: "Multi-map calibration to optimize fuel, timing and safety tables.",
      cost: 650
    }
  ];

  if (suspension < 0.65) {
    items.push({
      id: "suspension",
      title: "Upgrade Springs and Bushings",
      desc: "Track-spec adjustable coilovers to counter front-heavy engine bias.",
      cost: 950
    });
  }

  const buildWeeks = Math.max(1, Math.round(difficulty * 8));
  document.getElementById("checklist-total-time").textContent = `${buildWeeks} ${buildWeeks === 1 ? 'Week' : 'Weeks'}`;

  // Populate HTML
  const container = document.getElementById("checklist-container");
  container.innerHTML = items.map(item => {
    const isChecked = state.checklistCosts[item.id] !== undefined ? 'checked' : '';
    const currentCost = state.checklistCosts[item.id] !== undefined ? state.checklistCosts[item.id] : item.cost;
    
    return `
      <div class="checklist-item ${isChecked}" id="chk-row-${item.id}">
        <input type="checkbox" id="chk-${item.id}" ${isChecked} style="width:18px; height:18px; cursor:pointer;" data-id="${item.id}" data-base-cost="${item.cost}">
        <div>
          <span class="checklist-item-title">${item.title}</span>
          <span class="checklist-item-desc">${item.desc}</span>
        </div>
        <div class="checklist-slider-label">
          Cost: $
          <input type="number" id="cost-input-${item.id}" value="${currentCost}" data-id="${item.id}">
        </div>
      </div>
    `;
  }).join("");

  // Bind cost update listeners
  items.forEach(item => {
    const box = document.getElementById(`chk-${item.id}`);
    const input = document.getElementById(`cost-input-${item.id}`);
    const row = document.getElementById(`chk-row-${item.id}`);

    function updateItemCost() {
      if (box.checked) {
        state.checklistCosts[item.id] = Number(input.value);
        row.classList.add("checked");
      } else {
        delete state.checklistCosts[item.id];
        row.classList.remove("checked");
      }
      recalculateChecklistTotal();
    }

    box.addEventListener("change", updateItemCost);
    input.addEventListener("input", updateItemCost);

    // Initial state setup (default all to CHECKED initially)
    if (state.checklistCosts[item.id] === undefined && ["mounts", "adapter", "ecu", "tuning"].includes(item.id)) {
      box.checked = true;
      state.checklistCosts[item.id] = item.cost;
      row.classList.add("checked");
    }
  });

  recalculateChecklistTotal();
}

function recalculateChecklistTotal() {
  let total = 0;
  Object.values(state.checklistCosts).forEach(cost => {
    total += cost;
  });
  document.getElementById("checklist-total-cost").textContent = `$${total.toLocaleString()}`;
}

// Saved Garage (LocalStorage) CRUD
function getSavedBuilds() {
  try {
    return JSON.parse(localStorage.getItem("garage_builds")) || [];
  } catch {
    return [];
  }
}

function saveBuild(build) {
  const builds = getSavedBuilds();
  builds.push(build);
  localStorage.setItem("garage_builds", JSON.stringify(builds));
  renderGarage();
}

function deleteBuild(id) {
  let builds = getSavedBuilds();
  builds = builds.filter(b => b.id !== id);
  localStorage.setItem("garage_builds", JSON.stringify(builds));
  renderGarage();
}

function renderGarage() {
  const builds = getSavedBuilds();
  const list = document.getElementById("garage-list");
  
  if (builds.length === 0) {
    list.innerHTML = `<div class="muted" style="text-align:center; padding: 20px 0; grid-column:1/-1;">Your garage is empty. Configure a swap and save it!</div>`;
    return;
  }

  list.innerHTML = builds.map(b => `
    <article class="garage-card">
      <span class="garage-card-title">${b.name}</span>
      <span class="muted" style="font-size:0.8rem">Saved on ${new Date(b.timestamp).toLocaleDateString()}</span>
      <div class="garage-card-stats">
        <div><span class="muted">Power</span><br><b>${b.hp} hp</b></div>
        <div><span class="muted">Torque</span><br><b>${b.torque} Nm</b></div>
        <div><span class="muted">Fitment</span><br><b>${b.fitment}/100</b></div>
      </div>
      <div class="garage-card-actions">
        <button class="btn-load" onclick="loadSavedBuild('${b.id}')">Load</button>
        <button class="btn-share" onclick="shareSavedBuild('${b.id}')" title="Copy share link">Share</button>
        <button class="btn-delete" onclick="deleteSavedBuild('${b.id}')">Delete</button>
      </div>
    </article>
  `).join("");
}

// Save current configuration to local storage
document.getElementById("save-build-btn").addEventListener("click", () => {
  if (!state.latestResult) return;
  
  const engineName = sandboxToggle.checked ? form.elements.custom_engine_name.value : state.meta.engines.find(e => e.code === engineSelect.value).name;
  const chassisName = sandboxToggle.checked ? form.elements.custom_chassis_name.value : state.meta.chassis.find(c => c.code === chassisSelect.value).name;
  
  const defaultBuildName = `${engineName} swapped ${chassisName}`;
  const buildName = prompt("Enter a name for this build:", defaultBuildName);
  
  if (buildName === null) return;
  
  const payload = payloadFromForm();
  
  const build = {
    id: 'build_' + Date.now(),
    name: buildName || defaultBuildName,
    timestamp: Date.now(),
    payload: payload,
    sandboxActive: sandboxToggle.checked,
    hp: state.latestResult.predictions.horsepower,
    torque: state.latestResult.predictions.torque_nm,
    fitment: state.latestResult.compatibility.score
  };

  saveBuild(build);
});

window.loadSavedBuild = function(id) {
  const builds = getSavedBuilds();
  const build = builds.find(b => b.id === id);
  if (!build) return;

  sandboxToggle.checked = build.sandboxActive;
  sandboxToggle.dispatchEvent(new Event("change"));

  if (build.sandboxActive) {
    const d = build.payload.donor_engine_overrides;
    const r = build.payload.recipient_chassis_overrides;

    form.elements.custom_engine_name.value = d.name;
    form.elements.custom_displacement_l.value = d.displacement_l;
    form.elements.custom_cylinders.value = d.cylinders;
    form.elements.custom_compression_ratio.value = d.compression_ratio;
    form.elements.custom_engine_weight_kg.value = d.engine_weight_kg;
    form.elements.custom_base_hp.value = d.base_hp;
    form.elements.custom_base_torque_nm.value = d.base_torque_nm;
    form.elements.custom_forced_induction.value = d.forced_induction;
    form.elements.custom_layout.value = d.layout;
    form.elements.custom_donor_mount_width_mm.value = d.donor_mount_width_mm;

    form.elements.custom_chassis_name.value = r.name;
    form.elements.custom_recipient_weight_kg.value = r.recipient_weight_kg;
    form.elements.custom_stock_hp.value = r.stock_hp;
    form.elements.custom_engine_bay_width_mm.value = r.engine_bay_width_mm;
    form.elements.custom_wheelbase_mm.value = r.wheelbase_mm;
    form.elements.custom_drag_coefficient.value = r.drag_coefficient;
    form.elements.custom_stock_gear_ratio.value = r.stock_gear_ratio;
    form.elements.custom_drivetrain.value = r.drivetrain;
  } else {
    engineSelect.value = build.payload.engine_code;
    chassisSelect.value = build.payload.chassis_code;
  }

  tuneInput.value = build.payload.tune_level;
  tuneValue.textContent = build.payload.tune_level;
  
  form.elements.cooling_capacity_index.value = build.payload.cooling_capacity_index;
  form.elements.tire_grip_index.value = build.payload.tire_grip_index;
  form.elements.suspension_index.value = build.payload.suspension_index;
  form.elements.gear_ratio.value = build.payload.gear_ratio;

  updateVisuals();
  runPrediction();
  window.scrollTo({top: 0, behavior: 'smooth'});
};

window.shareSavedBuild = function(id) {
  const builds = getSavedBuilds();
  const build = builds.find(b => b.id === id);
  if (!build) return;
  
  const link = generateShareLinkForPayload(build.payload, build.sandboxActive);
  navigator.clipboard.writeText(link).then(() => {
    alert("Build share link copied to clipboard!");
  });
};

window.deleteSavedBuild = function(id) {
  if (confirm("Are you sure you want to remove this build from your garage?")) {
    deleteBuild(id);
  }
};

// URL Query String Serialization & Sharing
function generateShareLinkForPayload(payload, sandboxActive) {
  const base = window.location.origin + window.location.pathname;
  const params = new URLSearchParams();
  
  params.set("sandbox", sandboxActive ? "1" : "0");
  params.set("tune", payload.tune_level);
  params.set("cooling", payload.cooling_capacity_index);
  params.set("tire", payload.tire_grip_index);
  params.set("suspension", payload.suspension_index);
  params.set("gear", payload.gear_ratio);

  if (sandboxActive) {
    const d = payload.donor_engine_overrides;
    const r = payload.recipient_chassis_overrides;
    
    params.set("e_name", d.name);
    params.set("e_disp", d.displacement_l);
    params.set("e_cyl", d.cylinders);
    params.set("e_comp", d.compression_ratio);
    params.set("e_wt", d.engine_weight_kg);
    params.set("e_hp", d.base_hp);
    params.set("e_tq", d.base_torque_nm);
    params.set("e_fi", d.forced_induction);
    params.set("e_ly", d.layout);
    params.set("e_mw", d.donor_mount_width_mm);

    params.set("c_name", r.name);
    params.set("c_wt", r.recipient_weight_kg);
    params.set("c_hp", r.stock_hp);
    params.set("c_bw", r.engine_bay_width_mm);
    params.set("c_wb", r.wheelbase_mm);
    params.set("c_dc", r.drag_coefficient);
    params.set("c_gr", r.stock_gear_ratio);
    params.set("c_dt", r.drivetrain);
  } else {
    params.set("engine", payload.engine_code);
    params.set("chassis", payload.chassis_code);
  }

  return base + "?" + params.toString();
}

function parseUrlParams() {
  const params = new URLSearchParams(window.location.search);
  if (!params.has("tune")) return;
  
  const isSandbox = params.get("sandbox") === "1";
  sandboxToggle.checked = isSandbox;
  sandboxToggle.dispatchEvent(new Event("change"));

  if (isSandbox) {
    form.elements.custom_engine_name.value = params.get("e_name") || "Custom Engine";
    form.elements.custom_displacement_l.value = Number(params.get("e_disp") || 2.0);
    form.elements.custom_cylinders.value = Number(params.get("e_cyl") || 4);
    form.elements.custom_compression_ratio.value = Number(params.get("e_comp") || 10.0);
    form.elements.custom_engine_weight_kg.value = Number(params.get("e_wt") || 180);
    form.elements.custom_base_hp.value = Number(params.get("e_hp") || 200);
    form.elements.custom_base_torque_nm.value = Number(params.get("e_tq") || 200);
    form.elements.custom_forced_induction.value = params.get("e_fi") || "0";
    form.elements.custom_layout.value = params.get("e_ly") || "longitudinal";
    form.elements.custom_donor_mount_width_mm.value = Number(params.get("e_mw") || 700);

    form.elements.custom_chassis_name.value = params.get("c_name") || "Custom Chassis";
    form.elements.custom_recipient_weight_kg.value = Number(params.get("c_wt") || 1200);
    form.elements.custom_stock_hp.value = Number(params.get("c_hp") || 150);
    form.elements.custom_engine_bay_width_mm.value = Number(params.get("c_bw") || 750);
    form.elements.custom_wheelbase_mm.value = Number(params.get("c_wb") || 2500);
    form.elements.custom_drag_coefficient.value = Number(params.get("c_dc") || 0.32);
    form.elements.custom_stock_gear_ratio.value = Number(params.get("c_gr") || 4.10);
    form.elements.custom_drivetrain.value = params.get("c_dt") || "RWD";
  } else {
    engineSelect.value = params.get("engine") || "K24A";
    chassisSelect.value = params.get("chassis") || "MX5_NA";
  }

  tuneInput.value = Number(params.get("tune") || 0.65);
  tuneValue.textContent = tuneInput.value;
  
  form.elements.cooling_capacity_index.value = Number(params.get("cooling") || 0.70);
  form.elements.tire_grip_index.value = Number(params.get("tire") || 0.70);
  form.elements.suspension_index.value = Number(params.get("suspension") || 0.70);
  form.elements.gear_ratio.value = Number(params.get("gear") || 4.10);

  updateVisuals();
}

// Print trigger handler
document.getElementById("print-sheet-btn").addEventListener("click", () => {
  window.print();
});

async function runPrediction() {
  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.textContent = "Predicting...";
  submitBtn.style.opacity = "0.8";
  
  try {
    state.latestPayload = payloadFromForm();
    const result = await api("/api/predict", {
      method: "POST",
      body: JSON.stringify(state.latestPayload),
    });
    renderPrediction(result);
  } finally {
    submitBtn.textContent = "Run Prediction";
    submitBtn.style.opacity = "1";
  }
}

tuneInput.addEventListener("input", () => {
  tuneValue.textContent = tuneInput.value;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await runPrediction();
});

document.querySelector("#compare-button").addEventListener("click", async (e) => {
  const btn = e.target;
  btn.textContent = "Analyzing...";
  
  try {
    const payload = state.latestPayload || payloadFromForm();
    const result = await api("/api/compare", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderComparison(result);
  } finally {
    btn.textContent = "Compare All Engines for Current Chassis";
  }
});

async function init() {
  try {
    state.meta = await api("/api/meta");
    renderMeta(state.meta);
    parseUrlParams();
    await runPrediction();
    renderGarage();
  } catch (error) {
    document.body.innerHTML = `<div style="padding:40px; text-align:center; color:#f43f5e">
      <h2>Initialization Error</h2>
      <p>${error.message}</p>
    </div>`;
  }
}

// Info Modal Logic
const INFO_CONTENT = {
  "donor_engine": "The engine being swapped into the chassis. Affects base horsepower, torque, overall weight, and mounting geometry.",
  "recipient_chassis": "The vehicle receiving the new engine. Determines engine bay dimensions, aerodynamic drag, stock cooling capability, and vehicle weight.",
  "tune_level": "Adjusts the aggressiveness of the engine calibration (ECU tune). A higher value increases both horsepower and torque, simulating a more aggressive map.",
  "cooling_capacity": "The readiness of the radiator and cooling system. A higher index allows the engine to safely sustain more horsepower without heat soak.",
  "tire_grip": "The friction coefficient of the chosen tires. High grip significantly reduces 0-60 mph times by minimizing wheel spin during launch.",
  "suspension_readiness": "The quality of dampers, springs, and bushings. A stiffer, track-ready suspension improves launch dynamics and power delivery to the ground.",
  "gear_ratio": "The gear ratio of the differential. A numerically higher ratio (e.g., 4.30) increases wheel torque for faster acceleration, while a lower ratio (e.g., 3.73) favors top speed.",
  "performance_stats": "Predicted peak engine power (Horsepower) and twisting force (Torque) after applying the tune, cooling modifier, and difficulty penalties. 0-60 mph estimates the time to accelerate based on power-to-weight, grip, and drag.",
  "fitment_readiness": "A score out of 100 representing how easily the engine fits into the chassis. Based on physical dimensions (width), weight distribution shifts, and drivetrain layout compatibility (e.g. RWD vs FWD).",
  "dyno_curve": "Estimated performance torque and horsepower graphs across the functional RPM range, scaled dynamically to match regression predictions.",
  "drag_strip": "A simulated 1/4 mile acceleration strip computing reaction time, 60-foot, 1/8 mile splits, and final speed and time.",
  "custom_engine_name": "A descriptive custom name for your custom engine build.",
  "custom_displacement_l": "Total volumetric displacement of the cylinders in liters. Larger displacement typically correlates with higher base torque.",
  "custom_cylinders": "The number of cylinders in the engine block. Affects weight, physical dimensions, mount complexity, and mechanical balance.",
  "custom_compression_ratio": "The ratio of cylinder volume at bottom dead center to volume at top dead center. Stiffer compression yields higher base thermal efficiency.",
  "custom_engine_weight_kg": "Dry physical weight of the engine unit. Heavier blocks alter weight distribution and lower handling/fitment scores.",
  "custom_base_hp": "Raw crank horsepower output before ECU tuning, exhaust, or cooling enhancements.",
  "custom_base_torque_nm": "Peak engine torque output measured in Newton-meters before modifications.",
  "custom_forced_induction": "Induction system type. Turbocharged/supercharged setups gain significantly larger percentage increases from active ECU tuning.",
  "custom_layout": "Engine crank orientation. Transverse engines drive wheels side-to-side (FWD bias), while Longitudinal engines run front-to-rear (RWD bias).",
  "custom_donor_mount_width_mm": "Outer width dimension of the engine mounting brackets. Must clear chassis engine bay widths for direct drop-in.",
  "custom_chassis_name": "A descriptive custom name for your custom vehicle chassis project.",
  "custom_recipient_weight_kg": "Base vehicle curb weight of the recipient chassis. Lighter vehicles achieve vastly superior 0-60 mph acceleration times.",
  "custom_stock_hp": "Peak power of the original engine of the chassis. Used to calculate torque output, chassis stiffness requirements, and performance gains.",
  "custom_engine_bay_width_mm": "Inner spacing of the recipient engine bay. Determines if the donor engine fits without hitting the frame rails.",
  "custom_wheelbase_mm": "Center distance between front and rear wheels. Shorter wheelbases launch faster but can be unstable under heavy power.",
  "custom_drag_coefficient": "Aerodynamic drag profile rating. Lower drag (Cd) enables higher top speeds and reduces high-speed wind resistance.",
  "custom_stock_gear_ratio": "The differential ring-and-pinion gear ratio. Numerically higher gear ratios (e.g. 4.10) multiply torque for faster low-speed launch.",
  "custom_drivetrain": "Configuration of driven wheels. All Wheel Drive (AWD) maximizes traction, while Rear Wheel Drive (RWD) and Front Wheel Drive (FWD) are traction-limited."
};

const modal = document.getElementById("info-modal");
const modalTitle = document.getElementById("modal-title");
const modalBody = document.getElementById("modal-body");
const closeBtn = document.querySelector(".close-btn");

document.querySelectorAll(".info-btn").forEach(btn => {
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    const infoKey = btn.getAttribute("data-info");
    const content = INFO_CONTENT[infoKey];
    if (content) {
      modalTitle.textContent = formatFeature(infoKey);
      modalBody.textContent = content;
      modal.style.display = "block";
    }
  });
});

closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target == modal) {
    modal.style.display = "none";
  }
});

init();
