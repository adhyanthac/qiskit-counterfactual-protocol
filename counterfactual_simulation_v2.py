"""
Counterfactual Quantum Communication Simulation — v2 (Enhanced)
================================================================

Implementation of the Chained Quantum Zeno Effect (CQZE) protocol for
counterfactual communication using Qiskit and Aer simulator.

NEW in v2
---------
* Leakage-probability sweep  (P_leak vs M for several values of N)
* Success-probability sweep   (P_success vs M, N)
* Bloch-sphere snapshots at key circuit stages
* Fidelity analysis            (|⟨ψ_ideal | ψ_actual⟩|²)
* Side-by-side bar chart comparing both scenarios in one figure
* Consolidated multi-panel output saved as counterfactual_results_v2.png

Reference: Salih et al., Phys. Rev. Lett. 110, 170502 (2013)
Author: Adhyantha Chandrasekaran
Date: March 2026
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.quantum_info import Statevector, state_fidelity
from qiskit_ibm_runtime import QiskitRuntimeService

token = os.getenv("QISKIT_IBM_TOKEN")
instance = os.getenv("QISKIT_IBM_INSTANCE")

if not token:
    raise RuntimeError(
        "Missing IBM Quantum token. Set the QISKIT_IBM_TOKEN environment variable "
        "before running this script."
    )

service = QiskitRuntimeService(
    channel="ibm_quantum_platform",
    token=token,
    instance=instance,
)


def get_ibm_service():
    """Create an IBM Quantum service from environment variables."""
    return QiskitRuntimeService(
        channel="ibm_quantum_platform",
        token=token,
        instance=instance,
    )

# ────────────────────────────────────────────────────────────────────
# Core protocol class (unchanged logic, new analysis helpers)
# ────────────────────────────────────────────────────────────────────

class CounterfactualCommunication:
    """
    Implements counterfactual communication protocol using CQZE.

    Alice receives information from Bob without photons traveling
    through the transmission channel.

    Parameters
    ----------
    M : int
        Number of outer cycle iterations (Alice's interferometer)
    N : int
        Number of inner cycle iterations (transmission channel)
    """

    def __init__(self, M=128, N=128):
        self.M = M
        self.N = N
        self.theta_M = np.pi / (4 * M)   # outer-cycle rotation angle
        self.theta_N = np.pi / (4 * N)   # inner-cycle rotation angle

        # Theoretical leakage probability (leading-order)
        self.leakage_prob = (np.pi / (4 * M * N)) ** 2

    # ── circuit construction ──────────────────────────────────────

    def create_circuit(self, bob_blocks=False, measure=True):
        """
        Create quantum circuit for counterfactual communication.

        Parameters
        ----------
        bob_blocks : bool
            If True, Bob blocks (PC on, applies X gate).
            If False, Bob passes (identity).
        measure : bool
            If True, add measurement at end of circuit.

        Returns
        -------
        QuantumCircuit
        """
        qr = QuantumRegister(1, 'photon')
        cr = ClassicalRegister(1, 'detector')
        qc = QuantumCircuit(qr, cr)

        # Initial state: |H⟩ = |0⟩ (horizontal polarisation)

        # ===== OUTER CYCLE (M rotations) — Alice's interferometer =====
        for cycle in range(self.M):
            qc.ry(2 * self.theta_M, qr[0])
            qc.barrier(label=f'Outer{cycle+1}')

        # ===== INNER CYCLE (N rotations) — Transmission channel =====
        for cycle in range(self.N):
            qc.ry(2 * self.theta_N, qr[0])

            # Bob's Pockels Cell acts at mid-transmission
            if cycle == self.N // 2:
                if bob_blocks:
                    qc.x(qr[0])            # Pauli-X: H ↔ V flip
                    qc.barrier(label='Bob_BLOCKS')
                else:
                    qc.barrier(label='Bob_PASS')
            else:
                qc.barrier(label=f'Inner{cycle+1}')

        # ===== RETURN PATH — Reverse inner cycle =====
        for cycle in range(self.N):
            qc.ry(-2 * self.theta_N, qr[0])
            qc.barrier(label=f'RetInner{cycle+1}')

        # ===== RETURN PATH — Reverse outer cycle =====
        for cycle in range(self.M):
            qc.ry(-2 * self.theta_M, qr[0])
            qc.barrier(label=f'RetOuter{cycle+1}')

        if measure:
            qc.measure(qr[0], cr[0])

        return qc

    # ── simulation ────────────────────────────────────────────────

    def run_simulation(self, bob_blocks=False, shots=8192):
        """Run the simulation and return (circuit, counts, statevector)."""
        qc = self.create_circuit(bob_blocks, measure=True)
        simulator = AerSimulator()
        job = simulator.run(qc, shots=shots)
        counts = job.result().get_counts()

        qc_no_m = self.create_circuit(bob_blocks, measure=False)
        statevector = Statevector.from_instruction(qc_no_m)
        return qc, counts, statevector

    # ── state-evolution tracker ───────────────────────────────────

    def get_state_evolution(self, bob_blocks=False):
        """Track quantum state after every gate application."""
        states, labels = [], ['Init']

        qc = QuantumCircuit(1)
        states.append(Statevector.from_instruction(qc))

        # Outer cycle
        for i in range(self.M):
            qc.ry(2 * self.theta_M, 0)
            states.append(Statevector.from_instruction(qc))
            labels.append(f'RY_M({i+1})')

        # Inner cycle (forward)
        for i in range(self.N):
            qc.ry(2 * self.theta_N, 0)
            if i == self.N // 2 and bob_blocks:
                qc.x(0)
            states.append(Statevector.from_instruction(qc))
            lbl = f'RY_N({i+1})'
            if i == self.N // 2 and bob_blocks:
                lbl += '+X'
            labels.append(lbl)

        # Return inner
        for i in range(self.N):
            qc.ry(-2 * self.theta_N, 0)
            states.append(Statevector.from_instruction(qc))
            labels.append(f'RY†_N({i+1})')

        # Return outer
        for i in range(self.M):
            qc.ry(-2 * self.theta_M, 0)
            states.append(Statevector.from_instruction(qc))
            labels.append(f'RY†_M({i+1})')

        return states, labels

    # ── helpers ───────────────────────────────────────────────────

    def analyze_results(self, counts, shots=8192):
        h_count = counts.get('0', 0)
        v_count = counts.get('1', 0)
        print(f"  D₃  (|H⟩ = |0⟩): {h_count:>5}  ({100*h_count/shots:.1f}%)")
        print(f"  D₁/D₂ (|V⟩ = |1⟩): {v_count:>5}  ({100*v_count/shots:.1f}%)")
        return h_count, v_count


# ────────────────────────────────────────────────────────────────────
# NEW — Sweep functions for paper-style analysis
# ────────────────────────────────────────────────────────────────────

def sweep_leakage(M_range, N_values):
    """
    Compute theoretical P_leak = (π/(4MN))² for each (M, N) pair.

    Returns dict  N -> (M_array, P_leak_array)
    """
    results = {}
    for N in N_values:
        M_arr = np.array(M_range)
        P_leak = (np.pi / (4 * M_arr * N)) ** 2
        results[N] = (M_arr, P_leak)
    return results


def sweep_success(M_range, N_values, shots=4096):
    """
    Run simulations for many (M, N) values and record
    Alice's success probability for both Bob-pass and Bob-block.

    Returns dict  N -> { 'M': [...], 'pass_H': [...], 'block_V': [...] }
    """
    results = {}
    for N in N_values:
        data = {'M': [], 'pass_H': [], 'block_V': []}
        for M in M_range:
            comm = CounterfactualCommunication(M=M, N=N)

            # Bob passes  → Alice should detect |H⟩ (bit 0)
            _, counts_pass, _ = comm.run_simulation(bob_blocks=False, shots=shots)
            h_pass = counts_pass.get('0', 0) / shots

            # Bob blocks  → Alice should detect |V⟩ (bit 1)
            _, counts_block, _ = comm.run_simulation(bob_blocks=True, shots=shots)
            v_block = counts_block.get('1', 0) / shots

            data['M'].append(M)
            data['pass_H'].append(h_pass)
            data['block_V'].append(v_block)

        results[N] = data
    return results


def compute_fidelity_table(M_range, N_values):
    """
    For each (M,N) compute state fidelity of the final state vs the
    ideal outcome  (|H⟩ when Bob passes,  |V⟩ when Bob blocks).

    Returns list of dicts for tabular display.
    """
    rows = []
    ideal_H = Statevector([1, 0])
    ideal_V = Statevector([0, 1])
    for N in N_values:
        for M in M_range:
            comm = CounterfactualCommunication(M=M, N=N)
            _, _, sv_pass  = comm.run_simulation(bob_blocks=False)
            _, _, sv_block = comm.run_simulation(bob_blocks=True)
            fid_pass  = state_fidelity(sv_pass,  ideal_H)
            fid_block = state_fidelity(sv_block, ideal_V)
            rows.append({
                'M': M, 'N': N,
                'P_leak': comm.leakage_prob,
                'fidelity_pass': fid_pass,
                'fidelity_block': fid_block
            })
    return rows


# ────────────────────────────────────────────────────────────────────
# Visualisation
# ────────────────────────────────────────────────────────────────────

def create_enhanced_visualizations(comm, counts_pass, counts_block,
                                   states_pass, labels_pass,
                                   states_block, labels_block,
                                   h_pass, v_pass, h_block, v_block,
                                   shots):
    """Create the multi-panel result figure (saved as counterfactual_results_v2.png)."""

    fig = plt.figure(figsize=(22, 28))
    gs = GridSpec(5, 2, hspace=0.38, wspace=0.30, figure=fig)

    # ── Row 0: Detection histogram comparison ─────────────────────
    ax0 = fig.add_subplot(gs[0, :])
    labels_sc = ['Bob Passes\n(bit = 0)', 'Bob Blocks\n(bit = 1)']
    h_counts = [h_pass, h_block]
    v_counts = [v_pass, v_block]
    x = np.arange(2)
    w = 0.32
    bars1 = ax0.bar(x - w/2, h_counts, w, label='D₃ : |H⟩ (|0⟩)', color='#2563eb', alpha=0.85)
    bars2 = ax0.bar(x + w/2, v_counts, w, label='D₁/D₂ : |V⟩ (|1⟩)', color='#dc2626', alpha=0.85)
    ax0.set_ylabel('Detection Count', fontsize=13, fontweight='bold')
    ax0.set_title(f'Counterfactual Communication  (M={comm.M}, N={comm.N}, shots={shots})',
                  fontsize=15, fontweight='bold')
    ax0.set_xticks(x); ax0.set_xticklabels(labels_sc, fontsize=12)
    ax0.legend(fontsize=11); ax0.grid(axis='y', alpha=0.25)
    for bars in (bars1, bars2):
        for bar in bars:
            h = bar.get_height()
            ax0.text(bar.get_x() + bar.get_width()/2, h + shots*0.005,
                     f'{int(h)}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    # ── Row 1a: State evolution — Bob passes ──────────────────────
    ax1 = fig.add_subplot(gs[1, 0])
    steps = np.arange(len(states_pass))
    pH_p = [abs(s.data[0])**2 for s in states_pass]
    pV_p = [abs(s.data[1])**2 for s in states_pass]
    ax1.plot(steps, pH_p, 'b-o', lw=2, ms=4, label='P(|H⟩)')
    ax1.plot(steps, pV_p, 'r-s', lw=2, ms=4, label='P(|V⟩)')
    ax1.axhline(1, color='grey', ls='--', alpha=0.4)
    ax1.axhline(0, color='grey', ls='--', alpha=0.4)
    ax1.set_xlabel('Circuit Step'); ax1.set_ylabel('Probability')
    ax1.set_title('State Evolution: Bob Passes', fontweight='bold')
    ax1.legend(); ax1.grid(alpha=0.25); ax1.set_ylim(-0.05, 1.1)

    # ── Row 1b: State evolution — Bob blocks ──────────────────────
    ax2 = fig.add_subplot(gs[1, 1])
    pH_b = [abs(s.data[0])**2 for s in states_block]
    pV_b = [abs(s.data[1])**2 for s in states_block]
    ax2.plot(steps, pH_b, 'b-o', lw=2, ms=4, label='P(|H⟩)')
    ax2.plot(steps, pV_b, 'r-s', lw=2, ms=4, label='P(|V⟩)')
    ax2.axhline(1, color='grey', ls='--', alpha=0.4)
    ax2.axhline(0, color='grey', ls='--', alpha=0.4)
    ax2.set_xlabel('Circuit Step'); ax2.set_ylabel('Probability')
    ax2.set_title('State Evolution: Bob Blocks', fontweight='bold')
    ax2.legend(); ax2.grid(alpha=0.25); ax2.set_ylim(-0.05, 1.1)

    # ── Row 2a: P_leak vs M (theoretical) ────────────────────────
    ax3 = fig.add_subplot(gs[2, 0])
    M_range = np.arange(2, 21)
    N_values = [2, 4, 8, 16]
    leak_data = sweep_leakage(M_range, N_values)
    for N, (Ms, Ps) in leak_data.items():
        ax3.semilogy(Ms, Ps*100, 'o-', ms=4, label=f'N = {N}')
    ax3.set_xlabel('M (outer cycles)', fontweight='bold')
    ax3.set_ylabel('P_leak  (%)', fontweight='bold')
    ax3.set_title('Channel Leakage Probability vs M', fontweight='bold')
    ax3.legend(fontsize=9); ax3.grid(True, which='both', alpha=0.25)

    # ── Row 2b: Success probability vs M (simulated) ─────────────
    ax4 = fig.add_subplot(gs[2, 1])
    print("\n  ⏳  Running success-probability sweep (this may take a moment)...")
    M_sweep = [2, 3, 4, 6, 8, 10]
    N_sweep = [2, 4, 8]
    success_data = sweep_success(M_sweep, N_sweep, shots=2048)
    for N in N_sweep:
        d = success_data[N]
        ax4.plot(d['M'], d['block_V'], 's--', ms=5,
                 label=f'P(V | block) N={N}')
    ax4.axhline(1, color='grey', ls=':', alpha=0.4)
    ax4.set_xlabel('M (outer cycles)', fontweight='bold')
    ax4.set_ylabel('Success Probability', fontweight='bold')
    ax4.set_title('Alice Detection Probability vs M\n(Bob blocks — should approach 1)',
                  fontweight='bold')
    ax4.legend(fontsize=9); ax4.grid(alpha=0.25); ax4.set_ylim(0.4, 1.05)

    # ── Row 3a: Fidelity table as plot ───────────────────────────
    ax5 = fig.add_subplot(gs[3, 0])
    ax5.axis('off')
    fid_rows = compute_fidelity_table([2, 4, 8, 12], [2, 4, 8])
    col_labels = ['M', 'N', 'P_leak (%)', 'Fid (pass)', 'Fid (block)']
    table_data = []
    for r in fid_rows:
        table_data.append([
            str(r['M']), str(r['N']),
            f"{r['P_leak']*100:.4f}",
            f"{r['fidelity_pass']:.6f}",
            f"{r['fidelity_block']:.6f}"
        ])
    tbl = ax5.table(cellText=table_data, colLabels=col_labels,
                    loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(9)
    tbl.scale(1, 1.5)
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_facecolor('#4a1942')
            cell.set_text_props(color='white', fontweight='bold')
        elif row % 2 == 0:
            cell.set_facecolor('#f3e8ff')
    ax5.set_title('Fidelity & Leakage Table  (simulated statevector)',
                  fontweight='bold', fontsize=12, pad=20)

    # ── Row 3b: Bloch sphere phase diagram ───────────────────────
    ax6 = fig.add_subplot(gs[3, 1])
    ax6.axis('off')
    # Show key state amplitudes at each major stage
    labels_key = ['Init', 'After Outer', 'After Inner', 'After Bob', 'After Ret-Inner', 'Final']
    indices = [0, comm.M, comm.M+comm.N, comm.M+comm.N, comm.M+2*comm.N, len(states_block)-1]
    amp_text = "Amplitude Walk-through (Bob Blocks)\n" + "="*50 + "\n"
    amp_text += f"{'Stage':<18} {'α (|H⟩)':<16} {'β (|V⟩)':<16} {'P(H)':<8} {'P(V)':<8}\n"
    amp_text += "-"*66 + "\n"
    for lbl, idx in zip(labels_key, indices):
        if idx < len(states_block):
            s = states_block[idx]
            a, b = s.data[0], s.data[1]
            amp_text += (f"{lbl:<18} {a.real:+.4f}{a.imag:+.4f}j   "
                         f"{b.real:+.4f}{b.imag:+.4f}j   "
                         f"{abs(a)**2:.4f}  {abs(b)**2:.4f}\n")
    ax6.text(0.02, 0.5, amp_text, fontsize=9, family='monospace',
             va='center',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    ax6.set_title('Amplitude Walk-Through (Bob Blocks)', fontweight='bold', pad=15)

    # ── Row 4: Circuit structure summary ─────────────────────────
    ax7 = fig.add_subplot(gs[4, :])
    ax7.axis('off')
    circuit_text = f"""
    QUANTUM CIRCUIT STRUCTURE  (M={comm.M}, N={comm.N})
    ══════════════════════════════════════════════════════════════════════════════════════

    |0⟩=|H⟩ ── [RY(2θ_M)]×{comm.M}  ── [RY(2θ_N)]×{comm.N}  ── Bob (X or I) ── [RY(-2θ_N)]×{comm.N}  ── [RY(-2θ_M)]×{comm.M}  ── Measure
                   │                  │                │                   │                      │
             Outer Cycle          Inner Cycle      Transmission         Return Path            Detection
            (Alice's QZE)       (Channel QZE)      (Bob acts)           (Reverse)            (D₁/D₂/D₃)

    θ_M = π/(4M) = {np.degrees(comm.theta_M):.2f}°     θ_N = π/(4N) = {np.degrees(comm.theta_N):.2f}°
    P_leak = (π/(4MN))² = {comm.leakage_prob*100:.4f}%

    GATESET:  RY(θ) = rotation around Y axis  |  X = Pauli-X  (|0⟩↔|1⟩ flip, models Pockels cell blocking)
    RESULT :  Alice learns Bob's bit value without photon traveling through transmission channel
    """
    ax7.text(0.02, 0.5, circuit_text, fontsize=9.5, family='monospace',
             va='center',
             bbox=dict(boxstyle='round', facecolor='#e0f2fe', alpha=0.7))

    fig.suptitle('Counterfactual Quantum Communication — Enhanced Analysis',
                 fontsize=18, fontweight='bold', y=0.995)
    plt.savefig('counterfactual_results_v2.png', dpi=250, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: counterfactual_results_v2.png")


def create_leakage_standalone():
    """Standalone high-res leakage plot (useful for presentation slide)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    M_range = np.arange(2, 31)
    for N in [2, 4, 8, 16]:
        P = (np.pi / (4 * M_range * N))**2 * 100
        ax.semilogy(M_range, P, 'o-', ms=3, label=f'N = {N}')
    ax.set_xlabel('M (outer cycles)', fontsize=13, fontweight='bold')
    ax.set_ylabel('P_leak  (%)', fontsize=13, fontweight='bold')
    ax.set_title('Channel Leakage Probability\n'
                 r'$P_{\mathrm{leak}} = \left(\frac{\pi}{4MN}\right)^2$',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10); ax.grid(True, which='both', alpha=0.3)
    plt.tight_layout()
    plt.savefig('leakage_vs_M.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: leakage_vs_M.png")


def create_success_standalone():
    """Standalone success-probability plot for presentation."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    M_sweep = [2, 3, 4, 6, 8, 10, 12]
    N_sweep = [2, 4, 8]

    data = sweep_success(M_sweep, N_sweep, shots=2048)

    for N in N_sweep:
        d = data[N]
        ax1.plot(d['M'], d['pass_H'], 'o-', ms=5, label=f'N = {N}')
        ax2.plot(d['M'], d['block_V'], 's--', ms=5, label=f'N = {N}')

    ax1.set_title("Bob Passes → P(Alice detects |H⟩)", fontweight='bold')
    ax1.set_xlabel('M'); ax1.set_ylabel('P(detect |H⟩)')
    ax1.legend(); ax1.grid(alpha=0.3); ax1.set_ylim(0.85, 1.02)

    ax2.set_title("Bob Blocks → P(Alice detects |V⟩)", fontweight='bold')
    ax2.set_xlabel('M'); ax2.set_ylabel('P(detect |V⟩)')
    ax2.legend(); ax2.grid(alpha=0.3); ax2.set_ylim(0.4, 1.02)

    fig.suptitle('Alice Success Probability vs M  (simulated)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('success_vs_M.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: success_vs_M.png")


# ────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("COUNTERFACTUAL QUANTUM COMMUNICATION — IBM QUANTUM HARDWARE")
    print("Qiskit Runtime V2  |  Chained Quantum Zeno Effect (CQZE)")
    print("=" * 65)

    M, N, shots = 4, 4, 8192
    comm = CounterfactualCommunication(M=M, N=N)

    print(f"\nParameters:")
    print(f"  M = {M}   (outer cycles)")
    print(f"  N = {N}   (inner cycles)")
    print(f"  θ_M = π/{4*M} = {np.degrees(comm.theta_M):.2f}°")
    print(f"  θ_N = π/{4*N} = {np.degrees(comm.theta_N):.2f}°")
    print(f"  P_leak (theory) = {comm.leakage_prob*100:.4f}%")
    print(f"  Shots = {shots}\n")

    # ── Send to IBM Quantum ───────────────────────────────────────
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    print("─" * 65)
    print("📡 CONNECTING TO IBM QUANTUM HARDWARE...")
    print("─" * 65)
    service = get_ibm_service()
    backend = service.least_busy(simulator=False, operational=True)
    print(f"  Selected Backend: {backend.name}")

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    sampler = Sampler(mode=backend)
    sampler.options.default_shots = shots

    qc_p = comm.create_circuit(bob_blocks=False, measure=True)
    qc_b = comm.create_circuit(bob_blocks=True, measure=True)

    print("  Transpiling circuits...")
    isa_p = pm.run(qc_p)
    isa_b = pm.run(qc_b)

    print("  Submitting batch job to IBM Quantum...")
    job = sampler.run([isa_p, isa_b])
    print(f"  > Job ID: {job.job_id()}")
    print("  > Waiting for hardware results (may take a few minutes)...")
    result = job.result()

    counts_p = result[0].data.detector.get_counts()
    counts_b = result[1].data.detector.get_counts()

    # Hardware only returns counts; compute statevectors locally for fidelity plotting
    qc_p_no_m = comm.create_circuit(bob_blocks=False, measure=False)
    qc_b_no_m = comm.create_circuit(bob_blocks=True, measure=False)
    sv_p = Statevector.from_instruction(qc_p_no_m)
    sv_b = Statevector.from_instruction(qc_b_no_m)

    # ── Scenario 1: Bob passes ────────────────────────────────────
    print("\n─" * 65)
    print("📡 SCENARIO 1: Bob passes  (PC OFF, bit = 0)")
    print("─" * 65)
    h_p, v_p = comm.analyze_results(counts_p, shots)
    print(f"  Final statevector (theory): {sv_p}\n")

    # ── Scenario 2: Bob blocks ────────────────────────────────────
    print("─" * 65)
    print("🚫 SCENARIO 2: Bob blocks  (PC ON, bit = 1)")
    print("─" * 65)
    h_b, v_b = comm.analyze_results(counts_b, shots)
    print(f"  Final statevector (theory): {sv_b}\n")

    # ── State evolution ───────────────────────────────────────────
    print("  Computing state evolution …")
    states_p, labels_p = comm.get_state_evolution(bob_blocks=False)
    states_b, labels_b = comm.get_state_evolution(bob_blocks=True)

    # ── Fidelity ──────────────────────────────────────────────────
    ideal_H = Statevector([1, 0])
    ideal_V = Statevector([0, 1])
    fid_pass  = state_fidelity(sv_p, ideal_H)
    fid_block = state_fidelity(sv_b, ideal_V)
    print(f"\n  Fidelity (Bob passes)  F(ψ, |H⟩) = {fid_pass:.8f}")
    print(f"  Fidelity (Bob blocks)  F(ψ, |V⟩) = {fid_block:.8f}")

    # ── Generate plots ────────────────────────────────────────────
    print("\n  Generating enhanced visualisations …")
    create_enhanced_visualizations(
        comm, counts_p, counts_b,
        states_p, labels_p, states_b, labels_b,
        h_p, v_p, h_b, v_b, shots
    )
    create_leakage_standalone()
    create_success_standalone()

    # ── Print circuits ────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("QISKIT CIRCUIT: Bob Passes (bit = 0)")
    print("=" * 65)
    print(qc_p.draw(output='text', fold=100))
    print("\n" + "=" * 65)
    print("QISKIT CIRCUIT: Bob Blocks (bit = 1)")
    print("=" * 65)
    print(qc_b.draw(output='text', fold=100))

    print("\n" + "=" * 65)
    print("✓ All simulations complete!")
    print("  Files created:")
    print("    • counterfactual_results_v2.png  (multi-panel overview)")
    print("    • leakage_vs_M.png               (P_leak sweep)")
    print("    • success_vs_M.png               (success probability sweep)")
    print("=" * 65)


if __name__ == "__main__":
    main()
