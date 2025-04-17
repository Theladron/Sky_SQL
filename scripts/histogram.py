import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_delayed_flights(data):
    """
    Plots a histogram for the percentage of delayed flights per airline and saves it.

    :param data: List of dicts containing 'AIRLINE_NAME' and 'DELAY_PERCENTAGE'
    """
    try:
        airlines = [entry['AIRLINE_NAME'] for entry in data]
        percentages = [float(entry['DELAY_PERCENTAGE']) for entry in data]
    except (KeyError, TypeError, ValueError) as e:
        print(f"Error parsing delayed flight data: {e}")
        return

    plt.figure(figsize=(12, 6))
    plt.bar(airlines, percentages, color='skyblue')

    plt.xlabel("Airline")
    plt.ylabel("Percentage of Delayed Flights")
    plt.title("Percentage of Delayed Flights by Airline")

    plt.xticks(rotation=30, ha="right")  # Rotate airline names for better readability
    plt.tight_layout()

    plt.savefig("data/output/delay_by_airline.png")
    print("Diagram saved in data/output folder as delay_by_airline.png")
    plt.close()


def plot_delay_by_hour(delay_data):
    """
    Plots a histogram-like visualization of flight delays by hour with color scale and saves it.

    :param delay_data: List of dicts with keys 'HOUR' and 'DELAY_PERCENTAGE'
    """
    delay_array = np.zeros(24)  # Default to 0% for all hours (0-23)

    for entry in delay_data:
        try:
            hour = int(entry['HOUR'])
            percentage = float(entry['DELAY_PERCENTAGE'])
            if 0 <= hour < 24:
                delay_array[hour] = percentage
        except (KeyError, ValueError, TypeError) as e:
            print(f"Skipping invalid entry: {entry} ({e})")

    # Define color map from light colors for low delay to dark colors for high delay
    cmap = sns.color_palette("YlGnBu", as_cmap=True)

    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    norm = plt.Normalize(vmin=0, vmax=100)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Delay Percentage (%)")

    ax.set_xlabel("Hour of the Day")
    ax.set_ylabel("Percentage of Delayed Flights (%)")
    ax.set_title("Flight Delay Percentage by Hour")

    ax.set_xticks(np.arange(24))
    ax.set_xticklabels([str(i) for i in range(24)])
    ax.set_ylim(0, 80)
    ax.set_yticks(np.arange(0, 101, 20))

    # Plot the bar chart with color-mapped bars
    ax.bar(np.arange(24), delay_array, color=cmap(norm(delay_array)))

    plt.savefig("data/output/delay_by_hour.png")
    print("Diagram saved in data/output folder as delay_by_hour.png")
    plt.close()
