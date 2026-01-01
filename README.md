## Engine Definition:
In this Lab I define an engine as:

> **An engine is a system that converts stored energy into momentum transfer with an environment, subject to conservation laws.**

## 2.1 “System”

This is critical for software.

* The engine is **not magic**
* It has a boundary
* Things cross that boundary (energy, mass, momentum)

The simulation will always ask:

> “What crosses the system boundary?”

---

## 2.2 “Stored energy”

Fuel can be:

* Chemical
* Electrical
* Thermal
* Field energy (parameterized)

⚠️ We do **not** care *what* it is internally — only:

* How much energy is available
* How fast it can be released

That’s why the engine parameters include:

* `power_input`
* `energy_density`
* `efficiency`

---

## 2.3 “Momentum transfer” (THIS IS THE KEY)

Movement does **not** come from energy alone.

Movement comes from **momentum exchange**.

The engine must do **at least one** of these:

1. Expel mass (reaction engines)
2. Push on an external field (field engines)
3. Exchange momentum with spacetime *(speculative, constrained)*

This is where **anti-gravity claims are tested**.

---

## 2.4 “Environment”

No engine exists in isolation.

The environment may provide:

* Gravity
* Fields
* Reference frames

If there is **nothing** to push against:

> The engine must fail.

The code will enforce this.

---

## 2.5 “Conservation laws”

This is the judge, jury, and executioner.

No matter how creative the idea:

* Energy must balance
* Momentum must balance
* Mass must balance

This algorithm doesn’t *design* engines.
It **filters reality**.

That’s exactly what Noron does.

---

## ENGINE MODELS:

I define **three engine classes**.

---

### 2.1 Reaction-Based Engine (Baseline)

**Examples:**

* Chemical Rocket
* Ion drive
* Mass-ejection engine
* Ion thruster
* Photon rocket
* Nuclear thermal rocket

**Required parameters**

* Mass flow rate
* Exhaust velocity
* Energy source

**Purpose**

* Sanity baseline
* Validation
* Comparison


#### What leaves the system?

* **Mass and/or energy**

  * Exhaust mass (gas, ions)
  * Momentum-carrying radiation (photons, heat)

#### What does it push against?

* **The expelled exhaust**
* Ultimately: **conservation of momentum within the closed system**
* Space is *not* pushed against — the rocket pushes its own exhaust

#### Governing physics

* Newton’s Third Law
* Conservation of momentum
* Conservation of energy

### What law might it violate?

✅ **None** (when correctly modeled)

If performance claims exceed limits:

* **Energy conservation** (if exhaust energy < kinetic gain)
* **Relativistic limits** (near-c propulsion)

📌 **Key insight:**
A reaction engine *must* export momentum. No export → no acceleration.

---

### 2.2 Field-Interaction Engine (Speculative but legal)

**Examples:**
* EM-field interaction
* Gravitational field coupling (hypothetical)
* Electromagnetic thrusters
* Magnetoplasmadynamic drives,
* Gravity-assist propulsion
* Solar sails
* Sypothetical spacetime-metric engines

**Rules**

* Must exchange momentum with something
* Must consume energy

**Purpose**

* Explore edge cases
* Show why most ideas fail


#### What leaves the system?

* **Field momentum or energy**

  * EM radiation
  * Plasma interacting with external fields
  * Stress–energy transferred into spacetime curvature (hypothetical)

#### What does it push against?

* **External physical fields**

  * Electromagnetic fields
  * Solar photon flux
  * Gravitational field gradients
  * Spacetime geometry itself (if GR-consistent)

#### Governing physics

* Maxwell’s equations
* General Relativity
* Stress–energy tensor conservation

#### What law might it violate?

⚠️ **Only if improperly claimed**

* Momentum conservation **if the field interaction is ignored**
* Energy conservation **if the field source is not accounted for**

📌 **Key insight:**
Fields **carry momentum**.
If momentum flows into or out of a field, the engine is *not* reactionless.

> A field-based engine is still a reaction engine — the reaction just isn’t obvious.

---

### 2.3 Reactionless Claim Engine (Test subject)

**Examples:**

* EM-drive-like claims
* Inertial mass manipulation without exchange
* Internal oscillating mass drives
* “Anti-gravity” devices

**Behavior**

* Automatically audited
* Energy & momentum checked
* Almost always rejected

#### What leaves the system?

🚫 **Nothing** (by claim)

* No mass expelled
* No radiation emitted
* No external field momentum exchange

#### What does it push against?

❓ **Nothing identifiable**

* “The vacuum”
* “Inertia itself”
* “Asymmetric internal forces”

#### What law might it violate?

❌ **At least one fundamental law**

* Conservation of momentum (primary)
* Noether’s theorem (symmetry → conservation)
* Conservation of energy (often indirectly)
* Lorentz invariance (in many cases)

📌 **Key insight:**
If *nothing* leaves the system and *nothing external* is interacted with:

> **Acceleration is impossible in known physics**

That doesn’t mean:

* It’s fake by default
  But it **must**:
* Reveal a hidden momentum sink
* Or redefine what counts as “external” (vacuum ≠ nothing)
