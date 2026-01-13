"""
Network Visualization Script

Visualizes the Western Interconnection sample network on a geographic map.

Requirements:
    pip install matplotlib numpy pandas

Usage:
    python visualize_network.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os


def load_network_data():
    """Load nodes and branches from CSV files"""
    nodes_df = pd.read_csv('nodes.csv')
    branches_df = pd.read_csv('branches.csv')
    generators_df = pd.read_csv('generators.csv')

    return nodes_df, branches_df, generators_df


def plot_network_map(nodes_df, branches_df, generators_df, save_path='network_map.png'):
    """
    Create a geographic visualization of the network

    Args:
        nodes_df: DataFrame with node data
        branches_df: DataFrame with branch data
        generators_df: DataFrame with generator data
        save_path: Path to save the figure
    """
    fig, ax = plt.subplots(figsize=(16, 12))

    # Plot branches (transmission lines)
    for _, branch in branches_df.iterrows():
        from_node = nodes_df[nodes_df['id'] == branch['from_node_id']].iloc[0]
        to_node = nodes_df[nodes_df['id'] == branch['to_node_id']].iloc[0]

        # Color by voltage level
        if branch['voltage_kv'] == 500:
            color = '#D32F2F'  # Red for 500kV
            linewidth = 2.0
            alpha = 0.7
        elif branch['voltage_kv'] == 345:
            color = '#1976D2'  # Blue for 345kV
            linewidth = 1.5
            alpha = 0.6
        else:  # 230kV
            color = '#388E3C'  # Green for 230kV
            linewidth = 1.0
            alpha = 0.5

        ax.plot(
            [from_node['longitude'], to_node['longitude']],
            [from_node['latitude'], to_node['latitude']],
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            zorder=1
        )

    # Define colors for node types
    type_colors = {
        'substation': '#757575',
        'nuclear': '#9C27B0',
        'coal': '#5D4037',
        'gas': '#FF6F00',
        'hydro': '#0288D1',
        'solar': '#FDD835',
        'wind': '#00ACC1',
        'load_center': '#E91E63',
        'storage': '#00E676'
    }

    # Plot nodes by type
    for node_type, color in type_colors.items():
        type_nodes = nodes_df[nodes_df['type'] == node_type]
        if len(type_nodes) > 0:
            # Size by voltage level
            sizes = type_nodes['voltage_kv'].apply(lambda v: 150 if v == 500 else (100 if v == 345 else 60))

            ax.scatter(
                type_nodes['longitude'],
                type_nodes['latitude'],
                c=color,
                s=sizes,
                alpha=0.8,
                edgecolors='black',
                linewidth=0.5,
                label=node_type.replace('_', ' ').title(),
                zorder=2
            )

    # Annotate major cities/nodes
    major_nodes = nodes_df[nodes_df['voltage_kv'] >= 345].sample(min(15, len(nodes_df)))
    for _, node in major_nodes.iterrows():
        ax.annotate(
            node['name'].split(' - ')[0],  # Just city name
            xy=(node['longitude'], node['latitude']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=7,
            alpha=0.7,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='none')
        )

    # Create custom legend for transmission lines
    line_legend_elements = [
        mpatches.Patch(color='#D32F2F', label='500 kV'),
        mpatches.Patch(color='#1976D2', label='345 kV'),
        mpatches.Patch(color='#388E3C', label='230 kV')
    ]

    # Add legends
    legend1 = ax.legend(loc='upper left', title='Node Types', fontsize=9, framealpha=0.9)
    ax.add_artist(legend1)

    legend2 = ax.legend(
        handles=line_legend_elements,
        loc='lower left',
        title='Transmission Lines',
        fontsize=9,
        framealpha=0.9
    )

    # Set labels and title
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('Western Interconnection Sample Network\n55 Nodes, 90 Branches', fontsize=16, fontweight='bold')

    # Set grid
    ax.grid(True, alpha=0.3, linestyle='--')

    # Adjust layout
    plt.tight_layout()

    # Save figure
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\nNetwork map saved to: {save_path}")

    # Show plot
    plt.show()


def print_network_statistics(nodes_df, branches_df, generators_df):
    """Print summary statistics about the network"""
    print("\n" + "=" * 70)
    print("WESTERN INTERCONNECTION SAMPLE NETWORK STATISTICS")
    print("=" * 70)

    print(f"\nTopology:")
    print(f"  Total nodes: {len(nodes_df)}")
    print(f"  Total branches: {len(branches_df)}")

    print(f"\nNodes by voltage level:")
    for voltage in sorted(nodes_df['voltage_kv'].unique(), reverse=True):
        count = len(nodes_df[nodes_df['voltage_kv'] == voltage])
        print(f"  {voltage} kV: {count} nodes")

    print(f"\nNodes by ISO/RTO:")
    for iso in nodes_df['iso_rto'].unique():
        count = len(nodes_df[nodes_df['iso_rto'] == iso])
        print(f"  {iso}: {count} nodes")

    print(f"\nNodes by type:")
    for node_type in sorted(nodes_df['type'].unique()):
        count = len(nodes_df[nodes_df['type'] == node_type])
        print(f"  {node_type}: {count} nodes")

    print(f"\nBranches by voltage level:")
    for voltage in sorted(branches_df['voltage_kv'].unique(), reverse=True):
        count = len(branches_df[branches_df['voltage_kv'] == voltage])
        total_capacity = branches_df[branches_df['voltage_kv'] == voltage]['capacity_mw'].sum()
        avg_length = branches_df[branches_df['voltage_kv'] == voltage]['length_km'].mean()
        print(f"  {voltage} kV: {count} lines, {total_capacity:.0f} MW total capacity, {avg_length:.0f} km avg length")

    print(f"\nTransmission capacity:")
    print(f"  Total: {branches_df['capacity_mw'].sum():.0f} MW")
    print(f"  Average per line: {branches_df['capacity_mw'].mean():.0f} MW")
    print(f"  Range: {branches_df['capacity_mw'].min():.0f} - {branches_df['capacity_mw'].max():.0f} MW")

    print(f"\nLine lengths:")
    print(f"  Total: {branches_df['length_km'].sum():.0f} km")
    print(f"  Average: {branches_df['length_km'].mean():.0f} km")
    print(f"  Range: {branches_df['length_km'].min():.0f} - {branches_df['length_km'].max():.0f} km")

    print(f"\nGenerators:")
    existing = generators_df[generators_df['capacity_mw'] > 0]
    candidate = generators_df[generators_df['capacity_mw'] == 0]
    print(f"  Existing: {len(existing)} generators, {existing['capacity_mw'].sum():.0f} MW")
    print(f"  Candidate: {len(candidate)} generators")

    print(f"\nExisting generation by type:")
    for gen_type in sorted(existing['type'].unique()):
        count = len(existing[existing['type'] == gen_type])
        capacity = existing[existing['type'] == gen_type]['capacity_mw'].sum()
        print(f"  {gen_type}: {count} units, {capacity:.0f} MW")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    # Load data
    print("Loading network data...")
    nodes_df, branches_df, generators_df = load_network_data()

    # Print statistics
    print_network_statistics(nodes_df, branches_df, generators_df)

    # Create visualization
    print("\nGenerating network visualization...")
    plot_network_map(nodes_df, branches_df, generators_df)

    print("\nVisualization complete!")
