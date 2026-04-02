"""
Counterfactual Quantum Communication Simulation
================================================

Implementation of the Chained Quantum Zeno Effect (CQZE) protocol for
counterfactual communication using Qiskit and Aer simulator.

Reference: Salih et al., Phys. Rev. Lett. 110, 170502 (2013)

Author: Adhyantha Chandrasekaran
Date: February 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector


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
    
    def __init__(self, M=4, N=4):
        self.M = M
        self.N = N
        self.theta_M = np.pi / (4 * M)  # Outer cycle rotation angle
        self.theta_N = np.pi / (4 * N)  # Inner cycle rotation angle
        
        # Calculate theoretical leakage probability
        self.leakage_prob = (np.pi / (16 * M * N)) ** 2
        
    def create_circuit(self, bob_blocks=False, measure=True):
        """
        Create quantum circuit for counterfactual communication.
        
        Parameters
        ----------
        bob_blocks : bool
            If True, Bob blocks (PC on, rotates to V)
            If False, Bob passes (PC off, reflects H)
        measure : bool
            If True, add measurement at end of circuit
            
        Returns
        -------
        QuantumCircuit
            Qiskit circuit implementing the protocol
        """
        qr = QuantumRegister(1, 'photon')
        cr = ClassicalRegister(1, 'detector')
        qc = QuantumCircuit(qr, cr)
        
        # Initial state: |H⟩ = |0⟩ (horizontal polarization)
        
        # ===== OUTER CYCLE (M cycles) - Alice's interferometer =====
        for cycle in range(self.M):
            qc.ry(2 * self.theta_M, qr[0])
            qc.barrier(label=f'Outer{cycle+1}')
        
        # ===== INNER CYCLE (N cycles) - Transmission channel =====
        for cycle in range(self.N):
            qc.ry(2 * self.theta_N, qr[0])
            
            # Bob's Pockels Cell acts at mid-transmission
            if cycle == self.N // 2:
                if bob_blocks:
                    qc.x(qr[0])  # Pauli-X: H ↔ V flip
                    qc.barrier(label='Bob_BLOCKS')
                else:
                    qc.barrier(label='Bob_PASS')
            else:
                qc.barrier(label=f'Inner{cycle+1}')
        
        # ===== RETURN PATH - Reverse inner cycle =====
        for cycle in range(self.N):
            qc.ry(-2 * self.theta_N, qr[0])
            qc.barrier(label=f'RetInner{cycle+1}')
        
        # ===== RETURN PATH - Reverse outer cycle =====
        for cycle in range(self.M):
            qc.ry(-2 * self.theta_M, qr[0])
            qc.barrier(label=f'RetOuter{cycle+1}')
        
        # Measurement at detectors
        if measure:
            qc.measure(qr[0], cr[0])
        
        return qc
    
    def run_simulation(self, bob_blocks=False, shots=1000):
        """
        Run the counterfactual communication simulation.
        
        Parameters
        ----------
        bob_blocks : bool
            Bob's bit (0=pass, 1=block)
        shots : int
            Number of measurement repetitions
            
        Returns
        -------
        tuple
            (circuit, measurement_counts, final_statevector)
        """
        # Create circuit with measurement
        qc = self.create_circuit(bob_blocks, measure=True)
        
        # Use Aer simulator
        simulator = AerSimulator()
        
        # Execute circuit
        job = simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Get final statevector (without measurement)
        qc_no_measure = self.create_circuit(bob_blocks, measure=False)
        statevector = Statevector.from_instruction(qc_no_measure)
        
        return qc, counts, statevector
    
    def get_state_evolution(self, bob_blocks=False):
        """
        Track quantum state evolution through each gate.
        
        Parameters
        ----------
        bob_blocks : bool
            Bob's bit (0=pass, 1=block)
            
        Returns
        -------
        list
            List of Statevector objects at each circuit step
        """
        states = []
        
        # Build circuit incrementally
        qc = QuantumCircuit(1)
        states.append(Statevector.from_instruction(qc))
        
        # Outer cycle
        for cycle in range(self.M):
            qc.ry(2 * self.theta_M, 0)
            states.append(Statevector.from_instruction(qc))
        
        # Inner cycle (forward)
        for cycle in range(self.N):
            qc.ry(2 * self.theta_N, 0)
            if cycle == self.N // 2 and bob_blocks:
                qc.x(0)
            states.append(Statevector.from_instruction(qc))
        
        # Return path - inner
        for cycle in range(self.N):
            qc.ry(-2 * self.theta_N, 0)
            states.append(Statevector.from_instruction(qc))
        
        # Return path - outer
        for cycle in range(self.M):
            qc.ry(-2 * self.theta_M, 0)
            states.append(Statevector.from_instruction(qc))
        
        return states
    
    def analyze_results(self, counts, shots=1000):
        """
        Analyze and print measurement results.
        
        Parameters
        ----------
        counts : dict
            Measurement counts from Qiskit
        shots : int
            Total number of shots
        """
        h_count = counts.get('0', 0)
        v_count = counts.get('1', 0)
        
        print(f"  D₃ (|H⟩ = |0⟩): {h_count} ({100*h_count/shots:.1f}%)")
        print(f"  D₁/D₂ (|V⟩ = |1⟩): {v_count} ({100*v_count/shots:.1f}%)")
        
        return h_count, v_count


def main():
    """Main function to run the simulation and generate plots."""
    
    print("="*60)
    print("COUNTERFACTUAL QUANTUM COMMUNICATION SIMULATION")
    print("Using Qiskit + Aer Simulator")
    print("Chained Quantum Zeno Effect (CQZE)")
    print("="*60)
    
    # Initialize protocol
    comm = CounterfactualCommunication(M=4, N=4)
    
    print(f"\nParameters:")
    print(f"  M (outer cycles): {comm.M}")
    print(f"  N (inner cycles): {comm.N}")
    print(f"  θ_M = π/{4*comm.M} = {np.degrees(comm.theta_M):.2f}°")
    print(f"  θ_N = π/{4*comm.N} = {np.degrees(comm.theta_N):.2f}°")
    print(f"  Theoretical leakage: {comm.leakage_prob*100:.3f}%")
    
    # Scenario 1: Bob passes
    print("\n" + "="*60)
    print("📡 SCENARIO 1: Bob's PC is OFF (Bob passes photon back)")
    print("="*60)
    qc_pass, counts_pass, state_pass = comm.run_simulation(bob_blocks=False, shots=1000)
    
    print("Detection Results:")
    h_pass, v_pass = comm.analyze_results(counts_pass, shots=1000)
    print(f"Final state: {state_pass}")
    
    # Scenario 2: Bob blocks
    print("\n" + "="*60)
    print("🚫 SCENARIO 2: Bob's PC is ON (Bob blocks photon)")
    print("="*60)
    qc_block, counts_block, state_block = comm.run_simulation(bob_blocks=True, shots=1000)
    
    print("Detection Results:")
    h_block, v_block = comm.analyze_results(counts_block, shots=1000)
    print(f"Final state: {state_block}")
    
    # Get state evolution
    print("\nComputing state evolution...")
    states_pass = comm.get_state_evolution(bob_blocks=False)
    states_block = comm.get_state_evolution(bob_blocks=True)
    
    # Create visualizations
    print("Generating visualizations...")
    create_visualizations(comm, counts_pass, counts_block, 
                         states_pass, states_block,
                         h_pass, v_pass, h_block, v_block,
                         qc_pass, qc_block)
    
    print("\n" + "="*60)
    print("✓ Simulation complete!")
    print("  Results saved to: counterfactual_results.png")
    print("="*60)


def create_visualizations(comm, counts_pass, counts_block, 
                         states_pass, states_block,
                         h_pass, v_pass, h_block, v_block,
                         qc_pass, qc_block):
    """Create and save comprehensive visualization plots."""
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(4, 2, hspace=0.4, wspace=0.3)
    
    # Plot 1: Detection histogram comparison
    ax1 = fig.add_subplot(gs[0, :])
    labels = ['Bob Passes\n(bit=0)', 'Bob Blocks\n(bit=1)']
    h_counts = [h_pass, h_block]
    v_counts = [v_pass, v_block]
    
    x = np.arange(len(labels))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, h_counts, width, label='D₃: |H⟩ (|0⟩) detected', 
                     color='blue', alpha=0.7)
    bars2 = ax1.bar(x + width/2, v_counts, width, label='D₁/D₂: |V⟩ (|1⟩) detected', 
                     color='red', alpha=0.7)
    
    ax1.set_xlabel('Scenario', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Detection Count', fontsize=12, fontweight='bold')
    ax1.set_title('Counterfactual Communication Results', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    # Plot 2: Qiskit histogram - Bob passes
    ax2 = fig.add_subplot(gs[1, 0])
    plot_histogram(counts_pass, ax=ax2, color='blue', 
                   title='Bob Passes: Measurement Results')
    
    # Plot 3: Qiskit histogram - Bob blocks
    ax3 = fig.add_subplot(gs[1, 1])
    plot_histogram(counts_block, ax=ax3, color='red', 
                   title='Bob Blocks: Measurement Results')
    
    # Plot 4: State evolution (Bob passes)
    ax4 = fig.add_subplot(gs[2, 0])
    steps = np.arange(len(states_pass))
    probs_H_pass = [abs(s.data[0])**2 for s in states_pass]
    probs_V_pass = [abs(s.data[1])**2 for s in states_pass]
    
    ax4.plot(steps, probs_H_pass, 'b-', linewidth=2, label='P(|H⟩)', marker='o', markersize=4)
    ax4.plot(steps, probs_V_pass, 'r-', linewidth=2, label='P(|V⟩)', marker='s', markersize=4)
    ax4.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax4.axhline(y=0.0, color='gray', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Circuit Step', fontweight='bold')
    ax4.set_ylabel('Probability', fontweight='bold')
    ax4.set_title('State Evolution: Bob Passes', fontweight='bold')
    ax4.legend()
    ax4.grid(alpha=0.3)
    ax4.set_ylim(-0.1, 1.1)
    
    # Plot 5: State evolution (Bob blocks)
    ax5 = fig.add_subplot(gs[2, 1])
    probs_H_block = [abs(s.data[0])**2 for s in states_block]
    probs_V_block = [abs(s.data[1])**2 for s in states_block]
    
    ax5.plot(steps, probs_H_block, 'b-', linewidth=2, label='P(|H⟩)', marker='o', markersize=4)
    ax5.plot(steps, probs_V_block, 'r-', linewidth=2, label='P(|V⟩)', marker='s', markersize=4)
    ax5.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax5.axhline(y=0.0, color='gray', linestyle='--', alpha=0.5)
    ax5.set_xlabel('Circuit Step', fontweight='bold')
    ax5.set_ylabel('Probability', fontweight='bold')
    ax5.set_title('State Evolution: Bob Blocks', fontweight='bold')
    ax5.legend()
    ax5.grid(alpha=0.3)
    ax5.set_ylim(-0.1, 1.1)
    
    # Plot 6: Circuit diagram and parameters
    ax6 = fig.add_subplot(gs[3, :])
    ax6.axis('off')
    
    circuit_text = f"""
    QUANTUM CIRCUIT STRUCTURE
    ═════════════════════════════════════════════════════════════════════════════
    
    |0⟩=|H⟩ ─── [RY]^{comm.M} ─── [RY]^{comm.N} ─── Bob's PC ─── [RY†]^{comm.N} ─── [RY†]^{comm.M} ─── Measure
               │              │                │              │                │
            Outer Cycle   Inner Cycle   Transmission    Return Path      Detection
           (Alice's QZE) (Channel QZE)   (Bob acts)      (Reverse)       (D₁/D₂/D₃)
    
    GATES: RY(θ) = Y-axis rotation | X = Pauli-X (polarization flip)
    
    PARAMETERS: M={comm.M}, N={comm.N} | θ_M={np.degrees(comm.theta_M):.2f}°, θ_N={np.degrees(comm.theta_N):.2f}°
    Leakage Probability: {comm.leakage_prob*100:.3f}%
    
    RESULT: Alice learns Bob's bit without photon traveling through channel!
    """
    
    ax6.text(0.05, 0.5, circuit_text, fontsize=9, family='monospace',
             verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('counterfactual_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Print circuits to console
    print("\n" + "="*60)
    print("QISKIT CIRCUIT: Bob Passes (bit=0)")
    print("="*60)
    print(qc_pass.draw(output='text', fold=100))
    
    print("\n" + "="*60)
    print("QISKIT CIRCUIT: Bob Blocks (bit=1)")
    print("="*60)
    print(qc_block.draw(output='text', fold=100))


if __name__ == "__main__":
    main()
