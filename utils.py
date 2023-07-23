def convert_to_seconds(time_str):
    """
    time_str = "3d 12h 50m 10s"
    total_seconds = convert_to_seconds(time_str)
    ----------
    result:
        The total seconds for '3d 12h 50m 10s' is: 305410 seconds.
    """
    # Define the time units and their respective multipliers in seconds
    time_units = {
        'd': 86400,  # 1 day = 24 hours * 60 minutes * 60 seconds
        'h': 3600,   # 1 hour = 60 minutes * 60 seconds
        'm': 60,     # 1 minute = 60 seconds
        's': 1       # 1 second
    }

    # Split the input string into individual time units
    time_parts = time_str.split()

    # Initialize variables to store the converted values
    seconds = 0

    for part in time_parts:
        # Get the unit (e.g., 'd', 'h', 'm', or 's')
        unit = part[-1]
        # Get the numeric value of the unit
        value = int(part[:-1])
        # Convert the value to seconds using the appropriate multiplier
        seconds += value * time_units[unit]

    return seconds
