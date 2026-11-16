import math
import shutil
from typing import Any, Dict, List


def solve_circuit(topology: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Solve deterministic DC/AC circuit problems and provide explicit equation traces."""
    topo = topology.strip().lower()
    ngspice_path = shutil.which("ngspice")

    base_meta = {
        "topology": topo,
        "simulation_engine": "analytical_exact",
        "ngspice_available": bool(ngspice_path),
    }

    if topo == "ohms_law":
        v = params.get("voltage")
        i = params.get("current")
        r = params.get("resistance")
        known = sum(x is not None for x in (v, i, r))
        if known < 2:
            raise ValueError("Provide at least two of voltage, current, and resistance.")
        if v is None:
            v = float(i) * float(r)
        elif i is None:
            if float(r) == 0:
                raise ValueError("Resistance cannot be zero.")
            i = float(v) / float(r)
        elif r is None:
            if float(i) == 0:
                raise ValueError("Current cannot be zero.")
            r = float(v) / float(i)
        p = float(v) * float(i)
        return {
            **base_meta,
            "values": {"voltage_v": round(float(v), 6), "current_a": round(float(i), 6), "resistance_ohm": round(float(r), 6), "power_w": round(p, 6)},
            "steps": [f"V = I * R => {v:.4g} V = {i:.4g} A * {r:.4g} Ohm", f"P = V * I = {p:.4g} W"],
        }

    if topo == "series_parallel":
        resistors: List[float] = [float(x) for x in params.get("resistors", [100, 220, 330])]
        mode = str(params.get("connection", "series")).lower()
        vin = float(params.get("voltage", 12.0))
        if not resistors or any(r <= 0 for r in resistors):
            raise ValueError("All resistors must be positive (> 0 Ohm).")
        if mode == "series":
            r_eq = sum(resistors)
            i_tot = vin / r_eq
            branches = [{"resistor_ohm": r, "voltage_v": round(i_tot * r, 6), "current_a": round(i_tot, 6), "power_w": round(i_tot * i_tot * r, 6)} for r in resistors]
        elif mode == "parallel":
            r_eq = 1.0 / sum(1.0 / r for r in resistors)
            i_tot = vin / r_eq
            branches = [{"resistor_ohm": r, "voltage_v": round(vin, 6), "current_a": round(vin / r, 6), "power_w": round((vin * vin) / r, 6)} for r in resistors]
        else:
            raise ValueError("connection must be 'series' or 'parallel'")
        return {
            **base_meta,
            "values": {"r_eq_ohm": round(r_eq, 6), "total_current_a": round(i_tot, 6), "total_power_w": round(vin * i_tot, 6)},
            "branches": branches,
            "steps": [f"R_eq ({mode}) = {r_eq:.4g} Ohm", f"I_total = {vin:.4g} / {r_eq:.4g} = {i_tot:.4g} A"],
        }

    if topo == "voltage_divider":
        vin = float(params.get("vin", 12.0))
        r1 = float(params.get("r1", 1000.0))
        r2 = float(params.get("r2", 2000.0))
        if r1 < 0 or r2 < 0 or (r1 + r2) == 0:
            raise ValueError("R1 and R2 must be non-negative with R1 + R2 > 0.")
        vout = vin * (r2 / (r1 + r2))
        current = vin / (r1 + r2)
        return {
            **base_meta,
            "values": {"vin_v": vin, "vout_v": round(vout, 6), "current_a": round(current, 6), "r1_ohm": r1, "r2_ohm": r2},
            "steps": [f"V_out = V_in * R2 / (R1 + R2) = {vin} * {r2} / {r1 + r2} = {vout:.6g} V", f"I = {vin} / {r1 + r2} = {current:.6g} A"],
        }

    if topo == "rc_transient":
        vin = float(params.get("vin", 5.0))
        r = float(params.get("r", 1000.0))
        c = float(params.get("c", 1e-6))
        if r <= 0 or c <= 0:
            raise ValueError("Resistance and capacitance must be positive.")
        tau = r * c
        points = []
        for idx in range(51):
            t = (5.0 * tau) * (idx / 50.0)
            vc = vin * (1.0 - math.exp(-t / tau))
            ic = (vin / r) * math.exp(-t / tau)
            points.append({"t_s": round(t, 8), "vc_v": round(vc, 6), "ic_a": round(ic, 8)})
        return {
            **base_meta,
            "values": {"tau_s": tau, "steady_state_vc_v": vin, "initial_current_a": round(vin / r, 8)},
            "waveform": points,
            "steps": [f"Time constant tau = R * C = {tau:.6g} s", f"Vc(t) = {vin} * (1 - exp(-t / {tau:.4g}))"],
        }

    if topo == "rc_ac_filter":
        r = float(params.get("r", 1000.0))
        c = float(params.get("c", 1e-7))
        if r <= 0 or c <= 0:
            raise ValueError("Resistance and capacitance must be positive.")
        fc = 1.0 / (2.0 * math.pi * r * c)
        sweep = []
        for exp_val in [x * 0.25 for x in range(4, 25)]:
            freq = 10 ** exp_val
            ratio = 1.0 / math.sqrt(1.0 + (freq / fc) ** 2)
            db = 20.0 * math.log10(max(ratio, 1e-12))
            phase = -math.degrees(math.atan(freq / fc))
            sweep.append({"freq_hz": round(freq, 3), "gain": round(ratio, 6), "gain_db": round(db, 3), "phase_deg": round(phase, 2)})
        return {
            **base_meta,
            "values": {"cutoff_freq_hz": round(fc, 4), "r_ohm": r, "c_f": c},
            "frequency_response": sweep,
            "steps": [f"Low-pass RC cutoff frequency fc = 1 / (2*pi*R*C) = {fc:.4g} Hz"],
        }

    if topo == "kvl_kcl_loop":
        # Two-loop resistive bridge: V1 - I1*R1 - (I1 - I2)*R3 = 0 and (I1 - I2)*R3 - I2*R2 = 0
        v1 = float(params.get("v1", 12.0))
        r1 = float(params.get("r1", 100.0))
        r2 = float(params.get("r2", 200.0))
        r3 = float(params.get("r3", 300.0))
        if r1 <= 0 or r2 <= 0 or r3 <= 0:
            raise ValueError("Resistors R1, R2, R3 must be positive.")
        r_parallel = (r2 * r3) / (r2 + r3)
        i1 = v1 / (r1 + r_parallel)
        v_node = v1 - i1 * r1
        i2 = v_node / r2
        i3 = v_node / r3
        return {
            **base_meta,
            "values": {
                "node_voltage_v": round(v_node, 6),
                "i1_a": round(i1, 6),
                "i2_a": round(i2, 6),
                "i3_a": round(i3, 6),
                "kcl_residual_a": round(i1 - (i2 + i3), 9),
            },
            "steps": [
                f"KCL at shared node: I1 = I2 + I3",
                f"R_parallel(R2||R3) = {r_parallel:.4g} Ohm",
                f"I1 = {i1:.6g} A, V_node = {v_node:.6g} V, I2 = {i2:.6g} A, I3 = {i3:.6g} A",
            ],
        }

    raise ValueError(f"Unsupported circuit topology '{topology}'")
