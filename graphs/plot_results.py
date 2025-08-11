import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D


def create_bar_chart(exam_name):
    """Create a bar chart showing model performance for a specific exam."""
    # Read the CSV file
    df = pd.read_csv('results_as_percent.csv')
    
    # Get the model names from the percentage columns (columns 14-23, which are the actual percentages)
    model_columns = df.columns[14:24]  # Percentage columns (0-indexed as 14-23)
    
    # Get just one "All" row for the specified exam
    all_row = df[(df['Domain Number'] == 'All') & (df['Exam'] == exam_name)].iloc[0]
    
    # Extract model names and their performance percentages
    models = []
    percentages = []
    
    for col in model_columns:
        # Extract the percentage value (remove % sign and convert to float)
        value = str(all_row[col])
        if '%' in value:
            value = float(value.replace('%', ''))
        else:
            value = float(value)
        
        # Clean up the model name by removing .1 suffix
        model_name = col.replace('.1', '')
        models.append(model_name)
        percentages.append(value)
    
    # Create the bar chart
    plt.figure(figsize=(15, 8))
    bars = plt.bar(range(len(models)), percentages, color='skyblue', edgecolor='navy', alpha=0.7)
    
    # Customize the chart
    plt.title(f'LLM Performance - {exam_name} Exam', fontsize=16, fontweight='bold')
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('Performance Percentage (%)', fontsize=12)
    
    # Rotate x-axis labels for better readability
    plt.xticks(range(len(models)), models, rotation=45, ha='right')
    
    # Set y-axis limits to go from 0 to 100
    plt.ylim(0, 100)
    
    # Add value labels on top of each bar
    for i, (bar, percentage) in enumerate(zip(bars, percentages)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                 f'{percentage:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Add horizontal lines for passing thresholds
    plt.axhline(y=62.2, color='orange', linestyle='--', linewidth=2, alpha=0.8, label='May Pass (62.2%)')
    plt.axhline(y=84.4, color='green', linestyle='--', linewidth=2, alpha=0.8, label='Will Pass (84.4%)')
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)
    
    # Add legend
    plt.legend()
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()
    
    # Also save the plot
    plt.savefig(f'{exam_name}_model_performance_chart.png', dpi=300, bbox_inches='tight')
    print(f"Chart saved as '{exam_name}_model_performance_chart.png'")


def make_radar_axes(fig, rect, n_vars, frame='circle'):
    """Create a radar chart (spider chart) with the given number of variables."""
    # Calculate angles for each variable
    angles = [n / float(n_vars) * 2 * np.pi for n in range(n_vars)]
    angles += angles[:1]
    
    # Create the polar axes
    ax = fig.add_axes(rect, projection='polar')
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    # Draw one axis per variable and add labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([])
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"], color="grey", size=8)
    plt.ylim(0, 100)
    
    return ax


def create_star_chart(exam_name):
    """Create a star/radar chart showing subdomain performance for all models on a specific exam."""
    # Read the CSV file
    df = pd.read_csv('results_as_percent.csv')
    
    # Get all model columns (percentage columns 14-23)
    model_columns = df.columns[14:24]  # Percentage columns (0-indexed as 14-23)
    
    # Filter data for the specific exam (excluding 'All' and 'Aggregate' rows)
    exam_data = df[(df['Exam'] == exam_name) & 
                   (df['Domain Number'] != 'All') & 
                   (df['Domain Number'] != '')]
    
    # Function to convert number to Roman numeral
    def to_roman(num):
        roman_numerals = {
            1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 
            6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X'
        }
        return roman_numerals.get(num, str(num))
    
    # Get domain numbers and convert to Roman numerals
    subdomains = []
    for _, row in exam_data.iterrows():
        domain_num = row['Domain Number']
        if pd.notna(domain_num) and domain_num != '' and str(domain_num).isdigit():
            roman_num = to_roman(int(domain_num))
            subdomains.append(f"Domain {roman_num}")
    
    if not subdomains:
        print(f"No subdomain data found for {exam_name} exam")
        return
    
    # Create the radar chart
    fig = plt.figure(figsize=(15, 12))
    ax = make_radar_axes(fig, [0.1, 0.1, 0.8, 0.8], len(subdomains))
    
    # Calculate angles for plotting
    angles = [n / float(len(subdomains)) * 2 * np.pi for n in range(len(subdomains))]
    angles += angles[:1]  # Complete the circle
    
    # Colors for different models
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Plot data for each model
    for i, col in enumerate(model_columns):
        # Clean up the model name by removing .1 suffix
        model_name = col.replace('.1', '')
        
        # Get percentages for this model
        percentages = []
        for _, row in exam_data.iterrows():
            domain_name = row['Domain Name']
            if pd.notna(domain_name) and domain_name != '':
                # Extract percentage value
                value = str(row[col])
                if '%' in value:
                    value = float(value.replace('%', ''))
                else:
                    value = float(value)
                percentages.append(value)
        
        percentages += percentages[:1]  # Complete the circle
        
        # Plot the data for this model
        ax.plot(angles, percentages, 'o-', linewidth=2, label=model_name, color=colors[i % len(colors)])
    
    # Add subdomain labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(subdomains, size=10)
    
    # Customize the chart
    plt.title(f'All Models - {exam_name} Exam Subdomain Performance', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Get the handles and labels from the current plot for the model legend
    handles, labels = ax.get_legend_handles_labels()
    
    # Create custom legend elements for the CIPT subdomain titles (text only)
    from matplotlib.lines import Line2D
    custom_legend_elements = [
        Line2D([0], [0], marker='', color='none', label='Domain I: Foundational Principles'),
        Line2D([0], [0], marker='', color='none', label='Domain II: The Privacy Technologist\'s Role in the Context of the Organization'),
        Line2D([0], [0], marker='', color='none', label='Domain III: Privacy Risks, Threats and Violations'),
        Line2D([0], [0], marker='', color='none', label='Domain IV: Privacy-Enhancing Strategies, Techniques and Technologies'),
        Line2D([0], [0], marker='', color='none', label='Domain V: Privacy by Design'),
        Line2D([0], [0], marker='', color='none', label='Domain VI: Privacy Engineering'),
        Line2D([0], [0], marker='', color='none', label='Domain VII: Evolving or Emerging Technologies in Privacy')
    ]
    
    # Add the model legend on the right
    ax.legend(handles=handles, labels=labels, loc='center left', bbox_to_anchor=(1.05, 0.5), fontsize=10)
    
    # Add the custom legend in the bottom left using the figure
    fig.legend(handles=custom_legend_elements, loc='lower left', bbox_to_anchor=(0.02, 0.02), 
               fontsize=9, frameon=True, fancybox=True, shadow=True)
    
    # Add grid
    ax.grid(True)
    
    # Adjust layout
    plt.tight_layout()
    
    # Show the plot
    plt.show()
    
    # Save the plot
    plt.savefig(f'{exam_name}_all_models_subdomain_chart.png', dpi=300, bbox_inches='tight')
    print(f"Chart saved as '{exam_name}_all_models_subdomain_chart.png'")


def create_exam_comparison_star_chart():
    """Create a star/radar chart showing how all models perform across the 4 different exams."""
    # Read the CSV file
    df = pd.read_csv('results_as_percent.csv')
    
    # Get all model columns (percentage columns 14-23)
    model_columns = df.columns[14:24]  # Percentage columns (0-indexed as 14-23)
    
    # Get the 4 exam names (excluding 'Aggregate')
    exam_names = ['AIGP', 'CIPM', 'CIPP/US', 'CIPT']
    
    # Get "All" rows for each exam
    exam_data = {}
    for exam in exam_names:
        all_row = df[(df['Domain Number'] == 'All') & (df['Exam'] == exam)]
        if not all_row.empty:
            exam_data[exam] = all_row.iloc[0]
    
    if not exam_data:
        print("No exam data found")
        return
    
    # Create the radar chart
    fig = plt.figure(figsize=(15, 12))
    ax = make_radar_axes(fig, [0.1, 0.1, 0.8, 0.8], len(exam_names))
    
    # Calculate angles for plotting
    angles = [n / float(len(exam_names)) * 2 * np.pi for n in range(len(exam_names))]
    angles += angles[:1]  # Complete the circle
    
    # Colors for different models
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Plot data for each model
    for i, col in enumerate(model_columns):
        # Clean up the model name by removing .1 suffix
        model_name = col.replace('.1', '')
        
        # Get percentages for this model across all exams
        percentages = []
        for exam in exam_names:
            if exam in exam_data:
                # Extract percentage value
                value = str(exam_data[exam][col])
                if '%' in value:
                    value = float(value.replace('%', ''))
                else:
                    value = float(value)
                percentages.append(value)
        
        percentages += percentages[:1]  # Complete the circle
        
        # Plot the data for this model
        ax.plot(angles, percentages, 'o-', linewidth=2, label=model_name, color=colors[i % len(colors)])
    
    # Add exam labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(exam_names, size=12)
    
    # Customize the chart
    plt.title('LLM Performance Across Privacy Exams', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add legend
    plt.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), fontsize=10)
    
    # Add grid
    ax.grid(True)
    
    # Adjust layout
    plt.tight_layout()
    
    # Show the plot
    plt.show()
    
    # Save the plot
    plt.savefig('all_models_exam_comparison_chart.png', dpi=300, bbox_inches='tight')
    print("Chart saved as 'all_models_exam_comparison_chart.png'")


def create_aggregate_bar_chart():
    """Create a bar chart showing aggregate model performance across all exams."""
    # Read the CSV file
    df = pd.read_csv('results_as_percent.csv')
    
    # Get the model names from the percentage columns (columns 14-23, which are the actual percentages)
    model_columns = df.columns[14:24]  # Percentage columns (0-indexed as 14-23)
    
    # Get the Aggregate row
    aggregate_row = df[df['Exam'] == 'Aggregate'].iloc[0]
    
    # Extract model names and their performance percentages
    models = []
    percentages = []
    
    for col in model_columns:
        # Extract the percentage value (remove % sign and convert to float)
        value = str(aggregate_row[col])
        if '%' in value:
            value = float(value.replace('%', ''))
        else:
            value = float(value)
        
        # Clean up the model name by removing .1 suffix
        model_name = col.replace('.1', '')
        models.append(model_name)
        percentages.append(value)
    
    # Create the bar chart
    plt.figure(figsize=(15, 8))
    bars = plt.bar(range(len(models)), percentages, color='skyblue', edgecolor='navy', alpha=0.7)
    
    # Customize the chart
    plt.title('LLM Performance - Aggregate Across Exams', fontsize=16, fontweight='bold')
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('Performance Percentage (%)', fontsize=12)
    
    # Rotate x-axis labels for better readability
    plt.xticks(range(len(models)), models, rotation=45, ha='right')
    
    # Set y-axis limits to go from 0 to 100
    plt.ylim(0, 100)
    
    # Add value labels on top of each bar
    for i, (bar, percentage) in enumerate(zip(bars, percentages)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                 f'{percentage:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()
    
    # Also save the plot
    plt.savefig('Aggregate_model_performance_chart.png', dpi=300, bbox_inches='tight')
    print("Chart saved as 'Aggregate_model_performance_chart.png'")


# Set Exam Name
# exam_name = 'AIGP'
# exam_name = 'CIPM'
# exam_name = 'CIPP/US'
# exam_name = 'CIPT'
exam_name = 'Aggregate'

# Create the bar chart
# create_bar_chart(exam_name)

# Create star chart for all models
# create_star_chart(exam_name)

# Create exam comparison star chart
create_exam_comparison_star_chart()

# create_aggregate_bar_chart()