import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.animation import FuncAnimation

def read_temperature_data(filename):
    """Read temperature data from text file"""
    try:
        data = np.loadtxt(filename)
        print(f"Loaded data from {filename}, shape: {data.shape}")
        return data
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def create_heatmap(T, step, output_dir="plots"):
    """Create and save a heatmap for a given time step"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.figure(figsize=(12, 10))
    
    # Create the heatmap
    im = plt.imshow(T, cmap='hot', origin='lower', 
                   extent=[0, T.shape[1], 0, T.shape[0]],
                   vmin=0, vmax=100)
    
    plt.colorbar(im, label='Temperature (°C)')
    
    # Handle both integer and string step values
    if isinstance(step, int):
        plt.title(f'2D Heat Distribution - Step {step}')
        output_file = f"{output_dir}/heatmap_step_{step:04d}.png"
    else:
        plt.title(f'2D Heat Distribution - {step}')
        output_file = f"{output_dir}/heatmap_{step}.png"
    
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    
    # Add grid for better visualization
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved plot: {output_file}")

def create_animation():
    """Create an animation from all the output files"""
    print("Creating animation...")
    
    # Find all output files
    output_files = []
    for file in os.listdir('.'):
        if file.startswith('output_step_') and file.endswith('.txt'):
            output_files.append(file)
    
    # Sort files by step number
    output_files.sort()
    
    if not output_files:
        print("No output files found!")
        return
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    def animate(frame):
        filename = output_files[frame]
        step_num = filename.split('_')[2].split('.')[0]
        T = read_temperature_data(filename)
        
        if T is not None:
            ax.clear()
            im = ax.imshow(T, cmap='hot', origin='lower', 
                          extent=[0, T.shape[1], 0, T.shape[0]],
                          vmin=0, vmax=100)
            ax.set_title(f'2D Heat Distribution - Step {step_num}')
            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.grid(True, alpha=0.3)
            
            # Add colorbar only once
            if frame == 0:
                plt.colorbar(im, ax=ax, label='Temperature (°C)')
    
    # Create animation
    anim = FuncAnimation(fig, animate, frames=len(output_files), 
                        interval=200, repeat=True)
    
    # Save animation
    anim.save('heat_simulation.gif', writer='pillow', fps=5)
    print("Animation saved as 'heat_simulation.gif'")
    
    plt.close()

def plot_final_results():
    """Display and save the final results"""
    T_final = read_temperature_data('output_final.txt')
    if T_final is not None:
        # Final heatmap
        plt.figure(figsize=(12, 10))
        plt.imshow(T_final, cmap='hot', origin='lower', 
                  extent=[0, T_final.shape[1], 0, T_final.shape[0]],
                  vmin=0, vmax=100)
        plt.colorbar(label='Temperature (°C)')
        plt.title('Final Temperature Distribution')
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.grid(True, alpha=0.3)
        plt.savefig('final_temperature.png', dpi=150, bbox_inches='tight')
        plt.show()

def plot_temperature_slices():
    """Plot temperature profiles at specific slices"""
    T_final = read_temperature_data('output_final.txt')
    if T_final is None:
        return
    
    plt.figure(figsize=(15, 5))
    
    # Middle row
    middle_row = T_final[T_final.shape[0]//2, :]
    
    plt.subplot(1, 2, 1)
    plt.plot(middle_row)
    plt.title('Temperature along middle row (Final)')
    plt.xlabel('X Position')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)
    
    # Middle column
    middle_col = T_final[:, T_final.shape[1]//2]
    
    plt.subplot(1, 2, 2)
    plt.plot(middle_col)
    plt.title('Temperature along middle column (Final)')
    plt.xlabel('Y Position')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('temperature_slices_final.png', dpi=150, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("2D Heat Equation Visualization")
    print("=" * 40)
    
    # Create individual plots for important steps
    steps_to_plot = [0, 100, 500, 1000]
    
    for step in steps_to_plot:
        filename = f"output_step_{step:04d}.txt"
        
        if os.path.exists(filename):
            T = read_temperature_data(filename)
            if T is not None:
                create_heatmap(T, step)
    
    # Create plot for final result
    if os.path.exists("output_final.txt"):
        T_final = read_temperature_data("output_final.txt")
        if T_final is not None:
            create_heatmap(T_final, "final")
    
    # Create animation
    create_animation()
    
    # Create final analysis plots
    plot_temperature_slices()
    plot_final_results()
    
    print("\nVisualization completed!")
    print("Check the 'plots' directory for individual heatmaps")
    print("Check 'heat_simulation.gif' for the animation")
    print("Check 'final_temperature.png' for the final result")
    print("Check 'temperature_slices_final.png' for cross-sectional views")
