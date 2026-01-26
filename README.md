# PEVS, Physics Engine Validation Simulator

#### Video Demo:  <>

## 📌 Overview

**PEVS (Physics Engine Validation Simulator)** is a physics-first simulation lab designed to **test propulsion and engine concepts against fundamental conservation laws**.

Rather than *designing* engines, PEVS acts as a **reality filter**:

> If an engine violates conservation of energy, momentum, or mass,
> the simulator detects, explains, and rejects it.

This project was developed as a **CS50 Final Project**, combining:

* rigorous physics modeling
* numerical simulation
* backend engineering
* a full Flask web interface with persistence

---

## 🎯 Core Idea

In PEVS, an **engine** is defined as:

> **A system that converts stored energy into momentum transfer with an environment, subject to conservation laws.**

Every simulation answers one central question:

> **What crosses the system boundary?**

If nothing crosses the boundary, **acceleration is impossible**.

---

## 🧠 Physics Principles Enforced

### 1️⃣ System Boundary

* Engines are **not magic**
* They have a boundary
* Energy, mass, or momentum must cross it

### 2️⃣ Stored Energy

The simulator does **not care** what the energy is internally:

* chemical
* electrical
* thermal
* field energy

Only this matters:

* how much energy exists
* how fast it can be released
* efficiency

### 3️⃣ Momentum Transfer (Key Principle)

Movement requires **momentum exchange**, not just energy.

An engine must do at least one of:

1. Expel mass (reaction engines)
2. Push on an external field
3. Exchange momentum with spacetime *(speculative, constrained)*

### 4️⃣ Environment

No engine exists in isolation.

The environment may provide:

* gravity
* fields
* reference frames

If there is **nothing to push against**, the engine must fail.

### 5️⃣ Conservation Laws (The Judge)

* Energy must balance
* Momentum must balance
* Mass must balance

PEVS does not *assume* engines are valid, it **audits them**.

---

## 🚀 Engine Models Implemented

### 🔹 1. Reaction Engines (Baseline)

**Examples**

* Chemical rockets
* Ion thrusters
* Photon rockets
* Nuclear thermal engines

**Physics**

* Newton’s Third Law
* Conservation of momentum & energy

**Verdict**

* ✅ Always valid when modeled correctly

---

### 🔹 2. Field-Interaction Engines (Constrained)

**Examples**

* Solar sails
* EM field propulsion
* Gravity-assist mechanisms
* Hypothetical spacetime metric engines

**Rules**

* Must exchange momentum with a real field
* Must account for field energy

**Verdict**

* ⚠️ Valid *only* when field momentum is correctly modeled

> Fields carry momentum.
> A field engine is still a reaction engine, the reaction is just less obvious.

---

### 🔹 3. Reactionless Claim Engines (Test Subjects)

**Examples**

* EM-drive-like claims
* Internal oscillating mass devices
* “Anti-gravity” engines with no exchange

**Behavior**

* Automatically audited
* Conservation laws enforced strictly

**Verdict**

* ❌ Rejected by physics

> If nothing leaves the system and nothing external is interacted with,
> acceleration is impossible in known physics.

---

## 🧪 Numerical Credibility (V1.5)

This project goes beyond a toy simulator.

It implements **numerical honesty**:

| Feature                     | Status |
| --------------------------- | ------ |
| Vector momentum             | ✅      |
| Per-step state recording    | ✅      |
| Energy / momentum residuals | ✅      |
| Drift detection             | ✅      |
| Stable integrator           | ✅      |
| Quantitative verdicts       | ✅      |

The simulator can **prove why** something failed, not just claim it did.

---

## 🧩 Architecture Overview

```
pevs/
│
├── core_physics/        # Physics authority (engine-agnostic)
│   ├── state.py
│   ├── simulator.py
│   ├── conservation.py
│   ├── environment.py
│   └── engines/
│
├── algoron/             # Reasoning / auditing layer
│   ├── auditor.py
│   └── diagnostics.py
│
├── simulation/          # Simulation orchestration
│
├── web/                 # Flask application
│   ├── app/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── templates/
│   │   └── static/
│   └── run.py
│
├── cli_ui/              # CLI interface
│
├── requirements.txt
└── README.md
```

---

## 🌐 Web Application Features

* User authentication
* Simulation creation & execution
* Per-step result inspection
* Conservation law analysis
* Simulation history
* Clean, responsive UI

All simulations are **persisted** using SQLite.

---

## 🛠 Technologies Used

* **Python**
* **Flask**
* **SQLAlchemy**
* **SQLite**
* **HTML / CSS / JavaScript**
* **Numerical physics modeling**

No machine learning, all reasoning is deterministic and explainable.

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
cd web
python run.py
```

Then open:

```
http://127.0.0.1:5000
```

---

## 📈 Current Project Status

✅ Physics Core, complete
✅ Numerical credibility (V1.5), complete
✅ Environment & field engines, complete
✅ Flask UI & database, complete

The simulator is now a **closed-system physics sandbox**.

---

## 🔮 Future Work

Planned next steps:

* Rule-based reasoning engine (Algoron layer)
* Parameter sweeps & optimization
* Relativistic consistency warnings
* Advanced fraud detection for closed systems

---

