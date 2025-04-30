import random
import math
import pandas as pd
import matplotlib.pyplot as plt

# Parameters
room_size = 9
center = (0, 0)
distances = [3, 6]
trials = 3
waypoints_per_trial = 6

# Egocentric direction offsets relative to "forward = 90°"
# Index 0 = forward, 1 = forward-right, ..., 7 = forward-left
egocentric_offsets_from_90 = [0, 45, 90, 135, 180, -135, -90, -45]

def is_within_room(x, y, size=room_size):
    return -size / 2 <= x <= size / 2 and -size / 2 <= y <= size / 2

def compute_egocentric_angle(global_angle, heading):
    # Rotate so heading becomes 90° (egocentric forward)
    return (global_angle - heading + 90) % 360

all_data = []
all_paths = []

for trial in range(trials):
    current_pos = list(center)
    current_heading = 90  # Start facing +Y
    trial_data = []
    trial_path = [tuple(current_pos)]

    for _ in range(waypoints_per_trial):
        valid_moves = []

        for ego_idx, offset in enumerate(egocentric_offsets_from_90):
            global_angle = (current_heading + offset - 90) % 360
            angle_rad = math.radians(global_angle)
            for dist in distances:
                dx = dist * math.cos(angle_rad)
                dy = dist * math.sin(angle_rad)
                new_x = current_pos[0] + dx
                new_y = current_pos[1] + dy
                if is_within_room(new_x, new_y):
                    valid_moves.append((ego_idx, dist, global_angle, new_x, new_y))

        if not valid_moves:
            break

        ego_idx, dist, global_angle, new_x, new_y = random.choice(valid_moves)
        ego_angle = compute_egocentric_angle(global_angle, current_heading)
        trial_data.append([trial, ego_angle, dist])

        current_pos = [new_x, new_y]
        current_heading = global_angle  # Update heading to new movement direction
        trial_path.append(tuple(current_pos))

    while len(trial_data) < waypoints_per_trial:
        trial_data.append([trial, "", "", ""])

    all_data.append(trial_data)
    all_paths.append(trial_path)

# Create DataFrame
columns = ["Trial"]
for i in range(waypoints_per_trial):
    columns.extend([f"EgocentricAngle_{i}", f"Distance_{i}"])

flattened_data = []
for trial_data in all_data:
    row = [trial_data[0][0]]
    for entry in trial_data:
        row.extend(entry[1:])
    flattened_data.append(row)

df = pd.DataFrame(flattened_data, columns=columns)
df.to_csv("generated_path.csv", index=False)

# Plotting
colors = plt.cm.tab10.colors

plt.figure(figsize=(8, 8))
for i, path in enumerate(all_paths):
    for j in range(len(path) - 1):
        x0, y0 = path[j]
        x1, y1 = path[j + 1]
        dx = x1 - x0
        dy = y1 - y0
        plt.arrow(x0, y0, dx, dy,
                  color=colors[i % len(colors)], linewidth=1.5,
                  head_width=0.2, head_length=0.2, length_includes_head=True)
        plt.scatter(x1, y1, color=colors[i % len(colors)], s=40)

    plt.scatter(path[0][0], path[0][1], color=colors[i % len(colors)], s=60, edgecolors='black', label=f'Trial {i} Start')
    plt.scatter(path[-1][0], path[-1][1], color=colors[i % len(colors)], s=60, marker='X', edgecolors='black', label=f'Trial {i} End')

plt.title("Generated Path")
plt.xlim(-room_size / 2, room_size / 2)
plt.ylim(-room_size / 2, room_size / 2)
plt.grid(True)
plt.gca().set_aspect('equal', adjustable='box')
plt.xlabel("X (meters)")
plt.ylabel("Y (meters)")
plt.legend()
plt.show()
