"""
Network Flow Visualization for Counterfactual Communication
============================================================

Visualizes the physical path information takes through the 
counterfactual communication system, showing Alice's apparatus,
transmission channel, and Bob's apparatus.

Author: Your Name
Date: February 2025
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Polygon
import numpy as np


def draw_component(ax, x, y, width, height, label, color, alpha=0.3):
    """Draw a component box."""
    rect = FancyBboxPatch((x-width/2, y-height/2), width, height,
                          boxstyle="round,pad=0.05", 
                          edgecolor=color, facecolor=color,
                          alpha=alpha, linewidth=2)
    ax.add_patch(rect)
    ax.text(x, y, label, ha='center', va='center', 
           fontsize=10, fontweight='bold')


def draw_arrow(ax, x1, y1, x2, y2, color='black', style='solid', 
               label='', linewidth=2):
    """Draw an arrow between components."""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=20,
                           color=color, linestyle=style, linewidth=linewidth)
    ax.add_patch(arrow)
    
    if label:
        mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
        ax.text(mid_x, mid_y+0.2, label, ha='center', 
               fontsize=9, color=color, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))


def draw_detector(ax, x, y, label, detected=False):
    """Draw a detector."""
    color = 'red' if detected else 'gray'
    alpha = 0.8 if detected else 0.3
    circle = Circle((x, y), 0.15, facecolor=color, alpha=alpha, linewidth=2,
                   edgecolor='black')
    ax.add_patch(circle)
    ax.text(x, y-0.4, label, ha='center', fontsize=9, fontweight='bold')


def visualize_bob_passes(ax):
    """Create visualization for Bob passes scenario (bit=0)."""
    ax.set_xlim(-1, 12)
    ax.set_ylim(-1, 8)
    ax.axis('off')
    ax.set_title("Bob Passes (Bit = 0): Photon Path", 
                fontsize=14, fontweight='bold', pad=20)
    
    # Alice's section
    draw_component(ax, 1.5, 6, 2, 1.2, 'Source\n& PBS', 'yellow')
    
    # Outer cycle components
    draw_component(ax, 3, 4, 1.5, 1, 'SM₁', 'purple')
    draw_component(ax, 3, 2.5, 1.5, 1, 'SPR₁', 'green')
    draw_component(ax, 5, 3.25, 1.5, 1, 'PBS₃', 'lightblue')
    
    # Transmission channel
    channel_x = [5.5, 8.5, 8.5, 5.5]
    channel_y = [4.5, 4.5, 1.5, 1.5]
    channel = Polygon(list(zip(channel_x, channel_y)), 
                     edgecolor='orange', facecolor='orange', 
                     alpha=0.15, linewidth=3, linestyle='--')
    ax.add_patch(channel)
    ax.text(7, 5.2, 'Transmission Channel', fontsize=11, 
           fontweight='bold', ha='center', color='orange')
    
    # Inner cycle components
    draw_component(ax, 6.5, 3.5, 1.5, 1, 'SM₂', 'purple')
    draw_component(ax, 6.5, 2, 1.5, 1, 'SPR₂', 'green')
    
    # Bob's section
    draw_component(ax, 9, 3, 1.5, 1.5, "Bob's PC\n(OFF)", 'lightgreen')
    draw_component(ax, 9, 1, 1.5, 0.8, 'Mirror', 'gray')
    
    # Detectors
    draw_detector(ax, 1, 7, 'D₁', detected=False)
    draw_detector(ax, 2, 7, 'D₂', detected=False)
    draw_detector(ax, 1, 1, 'D₃', detected=True)  # This fires!
    
    # Draw photon path (forward - passes through)
    draw_arrow(ax, 1.5, 5.4, 1.5, 4.5, 'blue', 'solid', '|H⟩', 3)
    draw_arrow(ax, 1.5, 4, 3, 4, 'blue', 'solid')
    draw_arrow(ax, 3, 3.5, 3, 3, 'blue', 'solid')
    draw_arrow(ax, 3.7, 2.5, 5, 2.8, 'blue', 'solid')
    draw_arrow(ax, 5, 3.7, 6.5, 3.9, 'blue', 'solid')
    draw_arrow(ax, 6.5, 3, 6.5, 2.5, 'blue', 'solid')
    draw_arrow(ax, 7.2, 2, 9, 2.5, 'blue', 'solid')
    draw_arrow(ax, 9, 2.5, 9, 1.5, 'blue', 'solid', 'Reflects')
    
    # Return path (dashed)
    draw_arrow(ax, 8.3, 1, 7.2, 2, 'blue', 'dashed')
    draw_arrow(ax, 6.5, 2.5, 6.5, 3, 'blue', 'dashed')
    draw_arrow(ax, 5.8, 3.5, 5, 3.7, 'blue', 'dashed')
    draw_arrow(ax, 3.7, 2.5, 3, 3, 'blue', 'dashed')
    draw_arrow(ax, 3, 3.5, 3, 4, 'blue', 'dashed')
    draw_arrow(ax, 3, 4, 1.5, 4, 'blue', 'dashed')
    draw_arrow(ax, 1.5, 3.5, 1.5, 1.5, 'blue', 'dashed', '|H⟩→D₃')
    
    # Result annotation
    ax.text(7, 0.3, '✓ Photon stays |H⟩\n✓ Detected at D₃\n✓ Alice knows: Bob passed (0)',
           fontsize=10, ha='center', 
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))


def visualize_bob_blocks(ax):
    """Create visualization for Bob blocks scenario (bit=1)."""
    ax.set_xlim(-1, 12)
    ax.set_ylim(-1, 8)
    ax.axis('off')
    ax.set_title("Bob Blocks (Bit = 1): Photon Path", 
                fontsize=14, fontweight='bold', pad=20)
    
    # Alice's section
    draw_component(ax, 1.5, 6, 2, 1.2, 'Source\n& PBS', 'yellow')
    
    # Outer cycle components
    draw_component(ax, 3, 4, 1.5, 1, 'SM₁', 'purple')
    draw_component(ax, 3, 2.5, 1.5, 1, 'SPR₁', 'green')
    draw_component(ax, 5, 3.25, 1.5, 1, 'PBS₃', 'lightblue')
    
    # Transmission channel (red for blocked)
    channel_x = [5.5, 8.5, 8.5, 5.5]
    channel_y = [4.5, 4.5, 1.5, 1.5]
    channel = Polygon(list(zip(channel_x, channel_y)), 
                     edgecolor='red', facecolor='red', 
                     alpha=0.15, linewidth=3, linestyle='--')
    ax.add_patch(channel)
    ax.text(7, 5.2, 'Transmission Channel', fontsize=11, 
           fontweight='bold', ha='center', color='red')
    
    # Inner cycle components
    draw_component(ax, 6.5, 3.5, 1.5, 1, 'SM₂', 'purple')
    draw_component(ax, 6.5, 2, 1.5, 1, 'SPR₂', 'green')
    
    # Bob's section (PC ON - blocking)
    draw_component(ax, 9, 3, 1.5, 1.5, "Bob's PC\n(ON)", 'salmon')
    
    # Detectors
    draw_detector(ax, 1, 7, 'D₁', detected=True)  # This fires!
    draw_detector(ax, 2, 7, 'D₂', detected=False)
    draw_detector(ax, 1, 1, 'D₃', detected=False)
    
    # Draw photon path (forward - blocked)
    draw_arrow(ax, 1.5, 5.4, 1.5, 4.5, 'blue', 'solid', '|H⟩', 3)
    draw_arrow(ax, 1.5, 4, 3, 4, 'blue', 'solid')
    draw_arrow(ax, 3, 3.5, 3, 3, 'blue', 'solid')
    draw_arrow(ax, 3.7, 2.5, 5, 2.8, 'blue', 'solid')
    draw_arrow(ax, 5, 3.7, 6.5, 3.9, 'blue', 'solid')
    draw_arrow(ax, 6.5, 3, 6.5, 2.5, 'blue', 'solid')
    draw_arrow(ax, 7.2, 2, 9, 2.5, 'blue', 'solid')
    
    # Bob blocks (PC rotates to V)
    ax.text(9, 1.5, '✗ BLOCKED\n|H⟩→|V⟩', fontsize=9, ha='center',
           fontweight='bold', color='red',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    # Return path (now as |V⟩, shown in red)
    draw_arrow(ax, 8.3, 3, 7.2, 2, 'red', 'dashed', '|V⟩')
    draw_arrow(ax, 6.5, 2.5, 6.5, 3, 'red', 'dashed')
    draw_arrow(ax, 5.8, 3.5, 5, 3.7, 'red', 'dashed')
    draw_arrow(ax, 3.7, 2.5, 3, 3, 'red', 'dashed')
    draw_arrow(ax, 3, 3.5, 3, 4, 'red', 'dashed')
    draw_arrow(ax, 3, 4.5, 1.5, 5.5, 'red', 'dashed')
    draw_arrow(ax, 1.5, 6.5, 1, 6.8, 'red', 'dashed', '|V⟩→D₁')
    
    # Result annotation
    ax.text(7, 0.3, '✓ Photon rotated to |V⟩\n✓ Detected at D₁/D₂\n✓ Alice knows: Bob blocked (1)',
           fontsize=10, ha='center',
           bbox=dict(boxstyle='round', facecolor='salmon', alpha=0.7))


def create_schematic():
    """Create simplified conceptual schematic diagram."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Title
    ax.text(5, 5.5, 'Counterfactual Communication: Conceptual Overview', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Alice box
    alice_box = FancyBboxPatch((0.5, 2.5), 1.5, 2, 
                               boxstyle="round,pad=0.1",
                               edgecolor='blue', facecolor='lightblue',
                               alpha=0.5, linewidth=2)
    ax.add_patch(alice_box)
    ax.text(1.25, 3.5, 'ALICE', fontsize=12, fontweight='bold', ha='center')
    ax.text(1.25, 3, 'Outer\nCycle\n(M)', fontsize=9, ha='center')
    
    # Channel box
    channel_box = patches.Rectangle((2.5, 2.5), 5, 2, 
                                   edgecolor='orange', facecolor='orange',
                                   alpha=0.2, linewidth=3, linestyle='--')
    ax.add_patch(channel_box)
    ax.text(5, 4.7, 'Transmission Channel (QZE)', fontsize=11, 
           fontweight='bold', ha='center', color='orange')
    
    # Inner cycle box
    inner_box = FancyBboxPatch((3, 3), 1.5, 1, 
                              boxstyle="round,pad=0.05",
                              edgecolor='green', facecolor='lightgreen',
                              alpha=0.4, linewidth=2)
    ax.add_patch(inner_box)
    ax.text(3.75, 3.5, 'Inner\nCycle\n(N)', fontsize=9, ha='center')
    
    # Bob box
    bob_box = FancyBboxPatch((8, 2.5), 1.5, 2,
                            boxstyle="round,pad=0.1",
                            edgecolor='red', facecolor='lightcoral',
                            alpha=0.5, linewidth=2)
    ax.add_patch(bob_box)
    ax.text(8.75, 3.5, 'BOB', fontsize=12, fontweight='bold', ha='center')
    ax.text(8.75, 3, 'Pockels\nCell\n(bit)', fontsize=9, ha='center')
    
    # Arrows
    arrow1 = FancyArrowPatch((2, 3.5), (2.5, 3.5),
                            arrowstyle='->', mutation_scale=15,
                            color='blue', linewidth=2)
    ax.add_patch(arrow1)
    ax.text(2.25, 3.8, '|H⟩', fontsize=10, ha='center', color='blue')
    
    arrow2 = FancyArrowPatch((4.5, 3.5), (5.5, 3.5),
                            arrowstyle='->', mutation_scale=15,
                            color='blue', linewidth=2, linestyle='--')
    ax.add_patch(arrow2)
    ax.text(5, 3.8, 'QZE', fontsize=9, ha='center', color='blue')
    
    arrow3 = FancyArrowPatch((7.5, 3.5), (8, 3.5),
                            arrowstyle='->', mutation_scale=15,
                            color='blue', linewidth=2, linestyle='--')
    ax.add_patch(arrow3)
    
    # Return arrow
    arrow4 = FancyArrowPatch((8, 3), (4.5, 3),
                            arrowstyle='->', mutation_scale=15,
                            color='purple', linewidth=2, linestyle=':')
    ax.add_patch(arrow4)
    ax.text(6.25, 2.7, 'Return (|H⟩ or |V⟩)', fontsize=9, 
           ha='center', color='purple')
    
    arrow5 = FancyArrowPatch((2.5, 3), (2, 3),
                            arrowstyle='->', mutation_scale=15,
                            color='purple', linewidth=2, linestyle=':')
    ax.add_patch(arrow5)
    
    # Key insight
    insight_text = """
    KEY POINTS:
    • Photon probability in channel → 0 (Quantum Zeno Effect)
    • Bob's PC changes polarization state
    • Alice detects: D₃ (|H⟩) = bit 0, D₁/D₂ (|V⟩) = bit 1
    • Information transmitted WITHOUT photon travel!
    
    P_leak = π²/(16M²N²) → 0 as M,N → ∞
    """
    ax.text(5, 1.2, insight_text, fontsize=9, ha='center',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
           family='monospace')
    
    plt.tight_layout()
    plt.savefig('schematic_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Generate all network visualizations."""
    print("="*60)
    print("GENERATING NETWORK VISUALIZATIONS")
    print("="*60)
    
    # Main network diagram
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    visualize_bob_passes(axes[0])
    visualize_bob_blocks(axes[1])
    
    # Legend
    fig.text(0.5, 0.02, 
             'Solid arrows: Forward path  |  Dashed arrows: Return path  |  '
             'Blue: |H⟩ (horizontal)  |  Red: |V⟩ (vertical)',
             ha='center', fontsize=11, 
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    plt.savefig('network_visualization.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Network visualization saved: network_visualization.png")
    
    # Schematic diagram
    create_schematic()
    print("✓ Schematic diagram saved: schematic_diagram.png")
    
    print("\n" + "="*60)
    print("VISUALIZATION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
