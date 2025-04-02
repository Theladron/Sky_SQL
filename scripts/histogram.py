import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_delayed_flights(data):
    """
    Plots a histogram for the percentage of delayed flights per airline and saves it.

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
    plt.savefig("data/output/delay_by_airline.png")
    print("Diagram saved in data/output folder as delay_by_airline.png")


def plot_delay_by_hour(delay_data):
    """
    Plots a histogram-like visualization of flight delays by hour with color scale and saves it.

    :param delay_data: List of tuples (hour, delay_percentage)
    """
    # Extract hours and delay percentages from the data
    hours, delay_percentages = zip(*delay_data)

    # Create an array for storing delay percentages by hour
    delay_array = np.zeros(24)  # Default to 0% for all hours (0-23)

    # Fill the delay array with percentages, ensuring valid hours
    for hour, percentage in zip(hours, delay_percentages):
        if isinstance(hour, int) and 0 <= hour < 24:  # Validate the hour is within range
            delay_array[hour] = percentage if isinstance(percentage, (int, float)) else 0

    # Define color map from light colors for low delay to dark colors for high delay
    cmap = sns.color_palette("YlGnBu", as_cmap=True)

    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Add color bar
    norm = plt.Normalize(vmin=0, vmax=100)  # Normalize for the color scale
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Delay Percentage (%)")

    # Label the axes
    ax.set_xlabel("Hour of the Day")
    ax.set_ylabel("Percentage of Delayed Flights (%)")
    ax.set_title("Flight Delay Percentage by Hour")

    # Set the ticks and labels for the x-axis (hours 0 to 23)
    ax.set_xticks(np.arange(24))
    ax.set_xticklabels([str(i) for i in range(24)])

    # Set the y-axis range from 0 to 80% with step size of 20
    ax.set_ylim(0, 80)
    ax.set_yticks(np.arange(0, 101, 20))

    # Plot the delay percentages across hours
    ax.bar(np.arange(24), delay_array, color=cmap(norm(delay_array)))

    # Save the plot as an image file
    plt.savefig("data/output/delay_by_hour.png")
    print("Diagram saved in data/output folder as delay_by_hour.png")

    # Close the plot after saving
    plt.close()
