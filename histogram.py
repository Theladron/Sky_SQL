import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_delayed_flights(data):
    """
    Plots a histogram for the percentage of delayed flights per airline.

    :param data: List of tuples containing (airline_name, delay_percentage)
    """
    airlines, percentages = zip(*data)  # Unpacking airline names and delay percentages

    plt.figure(figsize=(12, 6))
    plt.bar(airlines, percentages)

    plt.xlabel("Airline")
    plt.ylabel("Percentage of Delayed Flights")
    plt.title("Percentage of Delayed Flights by Airline")

    plt.xticks(rotation=30, ha="right")  # Rotate airline names for better readability
    plt.tight_layout()

    plt.show()


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_delay_histogram(delay_data):
    """
    Plots a histogram-like visualization of flight delays by hour with color scale.

    :param delay_data: List of tuples (hour, delay_percentage)
    """
    hours, delay_percentages = zip(*delay_data)

    # Create an array for storing delay percentages by hour
    delay_array = np.zeros(24)

    # Fill the delay array with percentages
    for hour, percentage in zip(hours, delay_percentages):
        if 0 <= hour < 24:
            delay_array[hour] = percentage

    # Define color map from light colors for low delay to dark colors for high delay
    cmap = sns.color_palette("YlGnBu", as_cmap=True)

    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create bars with color corresponding to the delay percentages
    bars = ax.bar(np.arange(24), delay_array,
                  color=cmap((delay_array - 20) / 60))  # Normalizing from 20 to 80

    # Add color bar
    norm = plt.Normalize(vmin=20, vmax=80)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Delay Percentage (%)")

    # Label the axes
    ax.set_xlabel("Hour of the Day")
    ax.set_ylabel("Percentage of Delayed Flights (%)")
    ax.set_title("Flight Delay Percentage by Hour")

    # Set the ticks and labels for the x-axis
    ax.set_xticks(np.arange(24))
    ax.set_xticklabels([str(i) for i in range(24)])

    # Set the y-axis range from 0 to 80% with step size of 20
    ax.set_ylim(0, 80)
    ax.set_yticks(np.arange(0, 101, 20))

    plt.savefig("delay_by_hour.png")
    print("diagram saved in data as as delay_by_hour.png")
    plt.close()