#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

def ensure_dir(file_path):
    """Ensure directory exists for the file"""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_teslaphoresis_diagram(output_path):
    """Create a diagram illustrating teslaphoresis concept"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw Tesla coil (simplified)
    coil_x = np.linspace(0, 2, 100)
    coil_y1 = np.sin(2 * np.pi * coil_x) * 0.2 + 2
    coil_y2 = np.sin(2 * np.pi * coil_x) * 0.2 + 1.5
    coil_y3 = np.sin(2 * np.pi * coil_x) * 0.2 + 1
    
    ax.plot(coil_x, coil_y1, 'b-', linewidth=2)
    ax.plot(coil_x, coil_y2, 'b-', linewidth=2)
    ax.plot(coil_x, coil_y3, 'b-', linewidth=2)
    
    # Draw base
    ax.plot([0, 2], [0.7, 0.7], 'b-', linewidth=3)
    ax.plot([1, 1], [0.7, 1], 'b-', linewidth=3)
    
    # Draw electric field lines
    x = np.linspace(2.5, 8, 20)
    y = np.linspace(-1, 3, 20)
    X, Y = np.meshgrid(x, y)
    
    # Define a simple electric field
    source_x, source_y = 1, 1.5
    dx = X - source_x
    dy = Y - source_y
    r = np.sqrt(dx**2 + dy**2)
    Ex = dx / r**3
    Ey = dy / r**3
    
    # Normalize vectors for better visualization
    E_norm = np.sqrt(Ex**2 + Ey**2)
    Ex = Ex / E_norm
    Ey = Ey / E_norm
    
    # Plot electric field lines
    ax.streamplot(X, Y, Ex, Ey, color='royalblue', linewidth=1, density=1.5, arrowsize=1.2)
    
    # Draw carbon nanotubes aligning with the field
    cnt_positions = [(3, 0), (4, 1), (5, 0.5), (6, 1.5), (7, 0.8)]
    
    for i, (x, y) in enumerate(cnt_positions):
        # Calculate local field direction
        dx_local = x - source_x
        dy_local = y - source_y
        r_local = np.sqrt(dx_local**2 + dy_local**2)
        ex_local = dx_local / r_local**3
        ey_local = dy_local / r_local**3
        
        # Normalize and use as orientation for CNT
        magnitude = np.sqrt(ex_local**2 + ey_local**2)
        ex_local = ex_local / magnitude * 0.4
        ey_local = ey_local / magnitude * 0.4
        
        # Draw CNT as a line oriented along the field
        ax.plot([x - ex_local/2, x + ex_local/2], 
                [y - ey_local/2, y + ey_local/2], 
                'k-', linewidth=2)
    
    # Add annotations
    ax.annotate('Tesla Coil', xy=(1, 1.5), xytext=(0.2, 2.5),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    ax.annotate('Electric Field', xy=(5, 2), xytext=(5.5, 2.5),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    ax.annotate('Carbon Nanotubes\nAligning with Field', xy=(6, 0.8), xytext=(6.5, -0.5),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    # Set plot limits and remove axes
    ax.set_xlim(-0.5, 9)
    ax.set_ylim(-1, 3)
    ax.axis('off')
    
    plt.title('Teslaphoresis: Control of Carbon Nanotubes with Tesla Coil-Generated Electric Fields')
    
    # Save the figure
    ensure_dir(output_path)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def create_cnt_biosensor(output_path):
    """Create a diagram illustrating CNT-based biosensor concept"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw cell membrane
    membrane_x = np.linspace(0, 10, 1000)
    membrane_y = np.sin(membrane_x * 1.5) * 0.1 + 2
    ax.plot(membrane_x, membrane_y, 'b-', linewidth=2)
    ax.fill_between(membrane_x, membrane_y, 0, color='lightblue', alpha=0.3)
    
    # Draw CNT biosensor
    cnt_x = np.linspace(3, 7, 100)
    cnt_y1 = np.sin(cnt_x * 3) * 0.05 + 2.2
    cnt_y2 = np.sin(cnt_x * 3) * 0.05 + 2.3
    
    ax.plot(cnt_x, cnt_y1, 'k-', linewidth=2)
    ax.plot(cnt_x, cnt_y2, 'k-', linewidth=2)
    
    # Add receptors/binding sites on CNT
    receptor_positions = [3.5, 4.2, 5.0, 5.8, 6.5]
    for pos in receptor_positions:
        circle = plt.Circle((pos, 2.25), 0.07, color='red')
        ax.add_patch(circle)
    
    # Add target molecules
    for i, pos in enumerate(receptor_positions):
        if i % 2 == 0:  # Only show some bound to illustrate binding process
            molecule = plt.Circle((pos, 2.25), 0.05, color='green')
            ax.add_patch(molecule)
            # Add movement lines for molecules
            ax.plot([pos, pos - 0.2], [2.25, 2.6], 'g--', linewidth=1)
            ax.plot([pos, pos + 0.2], [2.25, 2.6], 'g--', linewidth=1)
    
    # Add electric circuit
    ax.plot([2, 8], [1.5, 1.5], 'k-', linewidth=1)
    ax.plot([2, 2], [1.5, 2.2], 'k-', linewidth=1)
    ax.plot([8, 8], [1.5, 2.3], 'k-', linewidth=1)
    
    # Add battery
    bat_x = [3.5, 3.5, 3.7, 3.7, 3.9, 3.9, 4.1]
    bat_y = [1.5, 1.3, 1.3, 1.5, 1.5, 1.3, 1.3]
    ax.plot(bat_x, bat_y, 'k-', linewidth=1.5)
    
    # Add display/measurement device
    ax.add_patch(plt.Rectangle((5, 1.1), 1.5, 0.8, fill=True, color='gray', alpha=0.7))
    
    # Signal lines illustrating detection
    signal_x = np.linspace(5.5, 6, 50)
    signal_y = np.sin(signal_x * 20) * 0.1 + 1.5
    ax.plot(signal_x, signal_y, 'r-', linewidth=1)
    
    # Add annotations
    ax.annotate('Cell Membrane', xy=(1, 2), xytext=(0.5, 2.5),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    ax.annotate('Carbon Nanotube\nwith Recognition Sites', xy=(5, 2.25), xytext=(3, 3),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    ax.annotate('Target Molecules', xy=(5.8, 2.6), xytext=(6.5, 3),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    ax.annotate('Electrical\nSignal', xy=(5.8, 1.5), xytext=(7, 1),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    # Set plot limits and remove axes
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')
    
    plt.title('Carbon Nanotube-Based Biosensor with Fluorescent Detection')
    
    # Save the figure
    ensure_dir(output_path)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def create_neural_interface(output_path):
    """Create a diagram illustrating CNT neural interface concept"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw neurons
    neuron_positions = [(1, 3), (2, 1), (4, 3.5), (6, 1.5), (8, 3), (9, 1)]
    
    for i, (x, y) in enumerate(neuron_positions):
        # Cell body
        circle = plt.Circle((x, y), 0.4, color='lightblue', alpha=0.8)
        ax.add_patch(circle)
        
        # Dendrites
        for j in range(5):
            angle = np.random.uniform(0, 2*np.pi)
            length = np.random.uniform(0.3, 0.6)
            ax.plot([x, x + length * np.cos(angle)], 
                    [y, y + length * np.sin(angle)], 
                    'blue', linewidth=0.8)
        
        # Axon (longer projection)
        if i < len(neuron_positions) - 1:
            next_x, next_y = neuron_positions[i+1]
            # Create curved path for axon
            axon_x = np.linspace(x, next_x, 50)
            axon_y = np.sin((axon_x - x) * np.pi / (next_x - x)) * 0.5 + y + (next_y - y) * (axon_x - x) / (next_x - x)
            ax.plot(axon_x, axon_y, 'blue', linewidth=1)
    
    # Draw carbon nanotube bridges
    cnt_bridges = [((2.2, 1.2), (3.8, 3.3)), ((4.2, 3.3), (5.8, 1.7)), ((6.2, 1.7), (7.8, 2.8))]
    
    for (start_x, start_y), (end_x, end_y) in cnt_bridges:
        # Create array of points for the bridge
        bridge_x = np.linspace(start_x, end_x, 50)
        bridge_y = np.linspace(start_y, end_y, 50)
        
        # Add small random variations to make it look like a CNT
        bridge_y += np.sin(bridge_x * 15) * 0.05
        
        ax.plot(bridge_x, bridge_y, 'k-', linewidth=2)
        
        # Add small markers to indicate CNT structure
        for i in range(5, len(bridge_x), 10):
            ax.plot(bridge_x[i], bridge_y[i], 'ko', markersize=2)
    
    # Draw electrical stimulation
    stim_x = 5
    stim_y = 2.5
    
    # Draw electrode
    ax.plot([stim_x, stim_x], [stim_y, stim_y - 1], 'gray', linewidth=3)
    ax.plot([stim_x - 0.5, stim_x + 0.5], [stim_y - 1, stim_y - 1], 'gray', linewidth=3)
    
    # Draw electrical field lines
    for angle in np.linspace(0, 2*np.pi, 12):
        for radius in np.linspace(0.3, 1, 3):
            circle = plt.Circle((stim_x, stim_y), radius, fill=False, color='red', alpha=0.3, linestyle='--')
            ax.add_patch(circle)
    
    # Add annotations
    ax.annotate('Neurons', xy=(1, 3), xytext=(0.5, 4),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    ax.annotate('Carbon Nanotube\nBridges', xy=(5, 2.3), xytext=(3, 4.2),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    ax.annotate('Electrical\nStimulation', xy=(5, 2), xytext=(7, 4),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    # Set plot limits and remove axes
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    plt.title('Neural Interface with Carbon Nanotube Bridges and Electrical Stimulation')
    
    # Save the figure
    ensure_dir(output_path)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate the images with absolute paths
    create_teslaphoresis_diagram(os.path.join(base_dir, 'pages/2/teslaphoresis_diagram.png'))
    create_cnt_biosensor(os.path.join(base_dir, 'pages/4/cnt_biosensor.png'))
    create_neural_interface(os.path.join(base_dir, 'pages/5/neural_interface.png'))
    
    print("All images generated successfully.")