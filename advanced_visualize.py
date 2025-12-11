import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import json
import os
import glob
from scipy import ndimage

class HeatSimulationVisualizer:
    def __init__(self, config_file='config.json'):
        """Initialize the visualizer with configuration"""
        self.config = self.load_config(config_file)
        self.setup_plot_style()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "simulation": {
                "nx": 100,
                "ny": 100,
                "alpha": 0.1,
                "steps": 1000,
                "output_interval": 100
            },
            "boundary_conditions": {
                "top_temp": 100.0,
                "bottom_temp": 100.0,
                "left_temp": 0.0,
                "right_temp": 0.0
            },
            "visualization": {
                "colormap": "hot",
                "output_format": "png",
                "create_animation": True,
                "animation_fps": 10,
                "dpi": 150
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                # Merge with default config
                self.merge_configs(default_config, user_config)
        
        return default_config
    
    def merge_configs(self, default, user):
        """Recursively merge user config with default"""
        for key, value in user.items():
            if isinstance(value, dict) and key in default:
                self.merge_configs(default[key], value)
            else:
                default[key] = value
    
    def setup_plot_style(self):
        """Setup matplotlib style for better plots"""
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = [12, 8]
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.grid'] = True
    
    def read_temperature_data(self, filename):
        """Read temperature data with error handling"""
        try:
            data = np.loadtxt(filename)
            print(f"✓ Loaded {filename} - Shape: {data.shape}")
            return data
        except Exception as e:
            print(f"✗ Error reading {filename}: {e}")
            return None
    
    def create_comparison_plot(self, steps=[0, 100, 500, 1000, 'final']):
        """Create a comparison plot of multiple time steps"""
        print("Creating comparison plot...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        plots_created = 0
        for idx, step in enumerate(steps):
            if idx >= len(axes):
                break
                
            if step == 'final':
                filename = 'output_final.txt'
                title = 'Final State'
            else:
                filename = f'output_step_{step:04d}.txt'
                title = f'Step {step}'
            
            if os.path.exists(filename):
                T = self.read_temperature_data(filename)
                if T is not None:
                    im = axes[idx].imshow(T, cmap=self.config['visualization']['colormap'], 
                                        origin='lower', vmin=0, vmax=100)
                    axes[idx].set_title(title, fontweight='bold')
                    axes[idx].set_xlabel('X Position')
                    axes[idx].set_ylabel('Y Position')
                    
                    # Add colorbar for each subplot
                    plt.colorbar(im, ax=axes[idx], label='Temperature (°C)')
                    plots_created += 1
        
        # Hide unused subplots
        for idx in range(plots_created, len(axes)):
            axes[idx].set_visible(False)
        
        plt.suptitle('2D Heat Equation - Temperature Evolution', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('temperature_comparison.png', 
                   dpi=self.config['visualization']['dpi'], 
                   bbox_inches='tight')
        plt.show()
        print("✓ Comparison plot saved as 'temperature_comparison.png'")
    
    def create_3d_surface(self, step='final'):
        """Create a 3D surface plot of temperature"""
        print(f"Creating 3D surface plot for step {step}...")
        
        if step == 'final':
            filename = 'output_final.txt'
        else:
            filename = f'output_step_{step:04d}.txt'
        
        if not os.path.exists(filename):
            print(f"✗ File {filename} not found")
            return
        
        T = self.read_temperature_data(filename)
        if T is None:
            return
        
        # Create meshgrid
        x = np.arange(T.shape[1])
        y = np.arange(T.shape[0])
        X, Y = np.meshgrid(x, y)
        
        # Create 3D plot
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create surface plot
        surf = ax.plot_surface(X, Y, T, cmap=self.config['visualization']['colormap'],
                              linewidth=0, antialiased=True, alpha=0.8,
                              rstride=2, cstride=2)
        
        ax.set_title(f'3D Temperature Surface - Step {step}', fontweight='bold', fontsize=14)
        ax.set_xlabel('X Position', fontweight='bold')
        ax.set_ylabel('Y Position', fontweight='bold')
        ax.set_zlabel('Temperature (°C)', fontweight='bold')
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.6, aspect=20, label='Temperature (°C)')
        
        # Set viewing angle
        ax.view_init(elev=30, azim=45)
        
        plt.savefig(f'3d_surface_{step}.png', 
                   dpi=self.config['visualization']['dpi'], 
                   bbox_inches='tight')
        plt.show()
        print(f"✓ 3D surface plot saved as '3d_surface_{step}.png'")
    
    def create_convergence_analysis(self):
        """Analyze how temperature converges over time"""
        print("Creating convergence analysis...")
        
        center_temps = []
        max_temps = []
        min_temps = []
        steps = []
        
        # Find all output files
        output_files = glob.glob('output_step_*.txt')
        output_files.sort()
        
        if not output_files:
            print("✗ No output files found for convergence analysis")
            return
        
        for filename in output_files:
            step = int(filename.split('_')[2].split('.')[0])
            T = self.read_temperature_data(filename)
            if T is not None:
                center_temp = T[T.shape[0]//2, T.shape[1]//2]
                center_temps.append(center_temp)
                max_temps.append(np.max(T))
                min_temps.append(np.min(T))
                steps.append(step)
        
        # Create convergence plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot center temperature convergence
        ax1.plot(steps, center_temps, 'b-', linewidth=2, marker='o', markersize=4, label='Center Temperature')
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Temperature Convergence at Center Point', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot temperature range
        ax2.plot(steps, max_temps, 'r-', linewidth=2, label='Maximum Temperature')
        ax2.plot(steps, min_temps, 'b-', linewidth=2, label='Minimum Temperature')
        ax2.fill_between(steps, min_temps, max_temps, alpha=0.2, label='Temperature Range')
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Temperature (°C)')
        ax2.set_title('Temperature Range Evolution', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('convergence_analysis.png', 
                   dpi=self.config['visualization']['dpi'], 
                   bbox_inches='tight')
        plt.show()
        print("✓ Convergence analysis saved as 'convergence_analysis.png'")
    
    def create_heat_flux_visualization(self):
        """Visualize heat flux using temperature gradients"""
        print("Creating heat flux visualization...")
        
        T_final = self.read_temperature_data('output_final.txt')
        if T_final is None:
            return
        
        # Calculate temperature gradient (heat flux direction)
        grad_y, grad_x = np.gradient(T_final)
        heat_flux_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))
        
        # 1. Heat flux magnitude
        im1 = ax1.imshow(heat_flux_magnitude, cmap='viridis', origin='lower')
        ax1.set_title('Heat Flux Magnitude', fontweight='bold')
        ax1.set_xlabel('X Position')
        ax1.set_ylabel('Y Position')
        plt.colorbar(im1, ax=ax1, label='Flux Magnitude')
        
        # 2. Temperature gradient in X direction
        im2 = ax2.imshow(grad_x, cmap='coolwarm', origin='lower')
        ax2.set_title('Temperature Gradient (X-direction)', fontweight='bold')
        ax2.set_xlabel('X Position')
        ax2.set_ylabel('Y Position')
        plt.colorbar(im2, ax=ax2, label='∂T/∂X')
        
        # 3. Temperature gradient in Y direction
        im3 = ax3.imshow(grad_y, cmap='coolwarm', origin='lower')
        ax3.set_title('Temperature Gradient (Y-direction)', fontweight='bold')
        ax3.set_xlabel('X Position')
        ax3.set_ylabel('Y Position')
        plt.colorbar(im3, ax=ax3, label='∂T/∂Y')
        
        # 4. Streamplot of heat flux
        x = np.arange(T_final.shape[1])
        y = np.arange(T_final.shape[0])
        X, Y = np.meshgrid(x, y)
        
        # Plot temperature as background
        im4 = ax4.imshow(T_final, cmap='hot', origin='lower', alpha=0.7)
        # Overlay streamlines for heat flux
        ax4.streamplot(X, Y, -grad_x, -grad_y, color='white', 
                      linewidth=1, arrowsize=1, density=1.5)
        ax4.set_title('Heat Flux Streamlines', fontweight='bold')
        ax4.set_xlabel('X Position')
        ax4.set_ylabel('Y Position')
        plt.colorbar(im4, ax=ax4, label='Temperature (°C)')
        
        plt.suptitle('Heat Flux Analysis - Final State', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('heat_flux_analysis.png', 
                   dpi=self.config['visualization']['dpi'], 
                   bbox_inches='tight')
        plt.show()
        print("✓ Heat flux visualization saved as 'heat_flux_analysis.png'")
    
    def create_advanced_animation(self):
        """Create a professional animation with multiple elements"""
        print("Creating advanced animation...")
        
        output_files = glob.glob('output_step_*.txt')
        output_files.sort()
        
        if not output_files:
            print("✗ No output files found for animation")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        def animate(frame):
            filename = output_files[frame]
            step = int(filename.split('_')[2].split('.')[0])
            T = self.read_temperature_data(filename)
            
            if T is not None:
                # Clear axes
                ax1.clear()
                ax2.clear()
                
                # Left subplot: Temperature heatmap
                im1 = ax1.imshow(T, cmap=self.config['visualization']['colormap'], 
                               origin='lower', vmin=0, vmax=100)
                ax1.set_title(f'Temperature Distribution - Step {step}', fontweight='bold')
                ax1.set_xlabel('X Position')
                ax1.set_ylabel('Y Position')
                
                # Right subplot: Cross-section through center
                center_row = T[T.shape[0]//2, :]
                center_col = T[:, T.shape[1]//2]
                
                ax2.plot(center_row, 'r-', linewidth=2, label='Middle Row')
                ax2.plot(center_col, 'b-', linewidth=2, label='Middle Column')
                ax2.set_title(f'Cross-section Profiles - Step {step}', fontweight='bold')
                ax2.set_xlabel('Position')
                ax2.set_ylabel('Temperature (°C)')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                ax2.set_ylim(0, 100)
                
                # Add colorbar only once
                if frame == 0:
                    plt.colorbar(im1, ax=ax1, label='Temperature (°C)')
        
        # Create animation
        anim = FuncAnimation(fig, animate, frames=len(output_files), 
                           interval=200, repeat=True)
        
        # Save animation
        anim.save('advanced_simulation.gif', 
                 writer='pillow', 
                 fps=self.config['visualization']['animation_fps'],
                 dpi=100)
        
        plt.close()
        print("✓ Advanced animation saved as 'advanced_simulation.gif'")
    
    def run_all_visualizations(self):
        """Run all visualization methods"""
        print("=" * 50)
        print("Running Advanced Visualizations")
        print("=" * 50)
        
        self.create_comparison_plot()
        self.create_3d_surface('final')
        self.create_convergence_analysis()
        self.create_heat_flux_visualization()
        
        if self.config['visualization']['create_animation']:
            self.create_advanced_animation()
        
        print("=" * 50)
        print("All visualizations completed!")
        print("Generated files:")
        print("  - temperature_comparison.png")
        print("  - 3d_surface_final.png")
        print("  - convergence_analysis.png")
        print("  - heat_flux_analysis.png")
        print("  - advanced_simulation.gif")
        print("=" * 50)

# Main execution
if __name__ == "__main__":
    viz = HeatSimulationVisualizer()
    viz.run_all_visualizations()
