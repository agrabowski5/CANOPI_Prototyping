"""
Generate realistic renewable availability profiles for solar and wind generators
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Solar generators (IDs 10-13, 31-33, 45)
solar_gens = [10, 11, 12, 13, 31, 32, 33, 45]

# Wind generators (IDs 14-16, 34, 37, 38, 39)
wind_gens = [14, 15, 16, 34, 37, 38, 39]

# Generate timestamps for one week (168 hours)
start_date = datetime(2024, 7, 1, 0, 0, 0)
timestamps = [start_date + timedelta(hours=i) for i in range(168)]

rows = []

for ts in timestamps:
    hour = ts.hour

    # Solar availability (0 at night, peak around noon)
    if hour < 6 or hour >= 20:
        # No solar at night
        solar_availability = 0.0
    elif 6 <= hour < 8:
        # Morning ramp up
        solar_availability = 0.15 + (hour - 6) * 0.20
    elif 8 <= hour < 12:
        # Morning to midday
        solar_availability = 0.55 + (hour - 8) * 0.10
    elif 12 <= hour < 14:
        # Peak solar
        solar_availability = 0.95 - abs(hour - 13) * 0.02
    elif 14 <= hour < 18:
        # Afternoon decline
        solar_availability = 0.93 - (hour - 14) * 0.15
    else:  # 18-19
        # Evening decline
        solar_availability = 0.33 - (hour - 18) * 0.15

    # Add some variability
    solar_availability += np.random.uniform(-0.05, 0.05)
    solar_availability = max(0.0, min(1.0, solar_availability))

    # Add all solar generators
    for gen_id in solar_gens:
        # Add site-specific variation
        site_factor = 0.95 + (gen_id % 3) * 0.025
        rows.append({
            'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'generator_id': gen_id,
            'availability_factor': round(solar_availability * site_factor, 4)
        })

    # Wind availability (more variable, not as correlated with time of day)
    base_wind = 0.35  # Base capacity factor
    # Add diurnal pattern (wind often picks up in afternoon/evening)
    if 14 <= hour < 22:
        diurnal_factor = 0.15
    elif 2 <= hour < 8:
        diurnal_factor = -0.10
    else:
        diurnal_factor = 0.0

    # Add substantial random variation
    wind_availability = base_wind + diurnal_factor + np.random.uniform(-0.20, 0.25)
    wind_availability = max(0.05, min(0.95, wind_availability))

    # Add all wind generators with site-specific characteristics
    for gen_id in wind_gens:
        # Different sites have different wind patterns
        if gen_id in [15, 38]:  # Pacific Northwest - higher capacity factors
            site_wind = wind_availability * 1.15
        elif gen_id in [39]:  # Wyoming - very high wind resource
            site_wind = wind_availability * 1.25
        else:
            site_wind = wind_availability

        # Add uncorrelated noise for each site
        site_wind += np.random.uniform(-0.10, 0.10)
        site_wind = max(0.05, min(0.95, site_wind))

        rows.append({
            'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'generator_id': gen_id,
            'availability_factor': round(site_wind, 4)
        })

# Create DataFrame and save
df = pd.DataFrame(rows)
df = df.sort_values(['timestamp', 'generator_id'])
df.to_csv('renewable_profiles.csv', index=False)
print(f"Generated {len(df)} renewable availability records")
print(f"Solar generators: {solar_gens}")
print(f"Wind generators: {wind_gens}")
