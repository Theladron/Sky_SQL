import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_delay_heatmap_by_airports(delay_data):
    """
    Plots a heatmap of flight delays by origin and destination airports and saves it.
    :param delay_data: List of dicts with keys 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'DELAY_PERCENTAGE'
    """
    # Extract unique airports
    origin_airports = sorted(set(entry['ORIGIN_AIRPORT'] for entry in delay_data))
    destination_airports = sorted(set(entry['DESTINATION_AIRPORT'] for entry in delay_data))

    # Create a dictionary to map airports to indices
    origin_index = {airport: idx for idx, airport in enumerate(origin_airports)}
    dest_index = {airport: idx for idx, airport in enumerate(destination_airports)}

    # Initialize a delay matrix
    delay_matrix = np.zeros((len(origin_airports), len(destination_airports)))

    # Populate the delay matrix with delay percentages
    for entry in delay_data:
        try:
            origin = entry['ORIGIN_AIRPORT']
            destination = entry['DESTINATION_AIRPORT']
            delay = float(entry['DELAY_PERCENTAGE'])

            origin_idx = origin_index.get(origin)
            dest_idx = dest_index.get(destination)

            if origin_idx is not None and dest_idx is not None:
                delay_matrix[origin_idx, dest_idx] = delay
        except (KeyError, ValueError, TypeError) as e:
            print(f"Skipping invalid entry: {entry} ({e})")

    # Create color palette
    cmap = sns.color_palette("Reds", as_cmap=True)

    # Set up the plot
    plt.figure(figsize=(10, 7))
    ax = sns.heatmap(
        delay_matrix, cmap=cmap, annot=False, fmt=".1f", cbar=True,
        xticklabels=destination_airports, yticklabels=origin_airports,
        cbar_kws={'label': 'Delay Percentage (%)'}, linewidths=0.5
    )

    ax.set_title("Flight Delay Percentage by Origin and Destination Airport")
    ax.set_xlabel("Destination Airport")
    ax.set_ylabel("Origin Airport")

    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("data/output/delay_by_airports.png")
    print("Diagram saved in data/output folder as delay_by_airports.png")
    plt.close()
