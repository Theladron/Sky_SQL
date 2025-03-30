import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_delay_heatmap_by_airports(delay_data):
    """
    Plots a heatmap of flight delays by origin and destination airports.
    :param delay_data: List of tuples (origin_airport, destination_airport, delay_percentage)
    """
    # Extract unique airports
    origin_airports = list(set([entry[0] for entry in delay_data]))
    destination_airports = list(set([entry[1] for entry in delay_data]))

    # Create a dictionary to map airports to indices
    origin_index = {airport: idx for idx, airport in enumerate(origin_airports)}
    dest_index = {airport: idx for idx, airport in enumerate(destination_airports)}

    # Initialize a delay matrix
    delay_matrix = np.zeros((len(origin_airports), len(destination_airports)))

    # Populate the delay matrix with delay percentages
    for origin, destination, delay in delay_data:
        origin_idx = origin_index.get(origin)
        dest_idx = dest_index.get(destination)
        if origin_idx is not None and dest_idx is not None:
            delay_matrix[origin_idx, dest_idx] = delay

    # Define color scale
    cmap = sns.color_palette("Reds", as_cmap=True)

    # Set up the plot
    plt.figure(figsize=(10, 7))
    ax = sns.heatmap(delay_matrix, cmap=cmap, annot=False, fmt=".1f", cbar=True,
                     xticklabels=destination_airports, yticklabels=origin_airports,
                     cbar_kws={'label': 'Delay Percentage (%)'}, linewidths=0.5)

    # Add titles and labels
    ax.set_title("Flight Delay Percentage by Origin and Destination Airport")
    ax.set_xlabel("Destination Airport")
    ax.set_ylabel("Origin Airport")

    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("data/delay_by_airports.png")
    print("diagram saved in data as as delay_by_airports.png")
    plt.close()
