# THIS WAS DONE BY CHAT I NEED TO DO THIS MYSELF


import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

df = pd.read_csv('habit_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday

# Weekday pattern
weekday_data = df[df['day_of_week'] < 5]
avg_minutes = (weekday_data['timestamp'].dt.hour * 60 + 
               weekday_data['timestamp'].dt.minute).mean()

# Convert back to time
avg_hour = int(avg_minutes // 60)
avg_min = int(avg_minutes % 60)

print(f"Weekday average wake time: {avg_hour:02d}:{avg_min:02d}")

# Calculate standard deviation
std_minutes = (weekday_data['timestamp'].dt.hour * 60 + 
               weekday_data['timestamp'].dt.minute).std()
print(f"Standard deviation: ±{std_minutes:.0f} minutes")

# Show time range (mean ± 1 std dev)
early = avg_minutes - std_minutes
late = avg_minutes + std_minutes
early_hour, early_min = int(early // 60), int(early % 60)
late_hour, late_min = int(late // 60), int(late % 60)

print(f"Typical range: {early_hour:02d}:{early_min:02d} - {late_hour:02d}:{late_min:02d}")

# Prepare data for clustering
df['minutes'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute
X = df[['minutes']].values

# K-means clustering
kmeans = KMeans(n_clusters=3, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# Cluster centers (mean times)
print("\nCluster Analysis:")
for i, center_min in enumerate(kmeans.cluster_centers_):
    hour = int(center_min[0] // 60)
    minute = int(center_min[0] % 60)
    cluster_size = (df['cluster'] == i).sum()
    print(f"Cluster {i}: {hour:02d}:{minute:02d} ({cluster_size} events)")

# PLOTTING
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Time vs Day (colored by cluster)
scatter = ax1.scatter(df['day_of_week'], df['minutes'], 
                      c=df['cluster'], cmap='viridis', s=100, alpha=0.6)
ax1.set_xlabel('Day of Week (0=Mon, 6=Sun)')
ax1.set_ylabel('Time (minutes after midnight)')
ax1.set_title('Lamp Turn-On Times by Day and Cluster')
ax1.grid(True, alpha=0.3)

# Convert y-axis to readable times
y_ticks = [0, 360, 420, 480, 540]  # 12am, 6am, 7am, 8am, 9am
y_labels = ['12:00 AM', '6:00 AM', '7:00 AM', '8:00 AM', '9:00 AM']
ax1.set_yticks(y_ticks)
ax1.set_yticklabels(y_labels)

# Plot 2: Distribution by cluster
for i in range(3):
    cluster_data = df[df['cluster'] == i]['minutes']
    ax2.hist(cluster_data, bins=10, alpha=0.5, label=f'Cluster {i}')
    
    # Mark cluster center
    center = kmeans.cluster_centers_[i][0]
    ax2.axvline(center, color=f'C{i}', linestyle='--', linewidth=2)

ax2.set_xlabel('Time (minutes after midnight)')
ax2.set_ylabel('Frequency')
ax2.set_title('Distribution of Times by Cluster')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Convert x-axis to readable times
ax2.set_xticks(y_ticks)
ax2.set_xticklabels(y_labels)

plt.tight_layout()
plt.show()