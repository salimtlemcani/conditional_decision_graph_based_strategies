
import matplotlib.pyplot as plt
import pandas as pd

def plot_performance(performance):
    # Ensure the index is datetime
    performance.index = pd.to_datetime(performance.index)

    # Get the dynamic column name
    performance_column = performance.columns[0]

    # Create a Matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the performance data using the dynamic column name
    ax.plot(performance.index, performance[performance_column], label=performance_column, color='blue')

    # Set axis labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Strategy NAV')
    ax.set_title('Strategy Performance Over Time')

    # Adjust x-axis date formatting
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    plt.xticks(rotation=45)

    # Adjust y-axis scaling
    y_min = performance[performance_column].min() * 0.99
    y_max = performance[performance_column].max() * 1.01
    ax.set_ylim([y_min, y_max])

    # Enable grid
    ax.grid(True)

    # Tight layout to prevent clipping
    plt.tight_layout()

    return fig
