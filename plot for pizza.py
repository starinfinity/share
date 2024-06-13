import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure and axes
fig, ax = plt.subplots(figsize=(12, 8))

# Define the boxes and their coordinates
boxes = {
    "A": (0.1, 0.8, "User sends POST request to /order/<count>"),
    "B": (0.1, 0.6, "pizza_service creates PizzaOrder and sends to 'pizza' topic"),
    "C": (0.5, 0.6, "main_sauce consumes from 'pizza' and publishes to 'pizza-with-sauce'"),
    "D": (0.5, 0.4, "main_cheese consumes from 'pizza-with-sauce' and publishes to 'pizza-with-cheese'"),
    "E": (0.5, 0.2, "main_meats consumes from 'pizza-with-cheese' and publishes to 'pizza-with-meats'"),
    "F": (0.5, 0.0, "main_veggies consumes from 'pizza-with-meats' and publishes to 'pizza-with-veggies'"),
    "A1": (0.1, 0.4, "User sends GET request to /order/<order_id>"),
    "G": (0.1, 0.2, "pizza_service retrieves order details"),
    "A2": (0.1, 0.0, "User sends GET request to /report"),
    "H": (0.1, -0.2, "report_service generates report")
}

# Add boxes to the plot
for box, (x, y, text) in boxes.items():
    ax.add_patch(patches.Rectangle((x, y), 0.3, 0.1, edgecolor='black', facecolor='white'))
    ax.text(x + 0.15, y + 0.05, text, horizontalalignment='center', verticalalignment='center', fontsize=10)

# Draw arrows
arrows = [
    ("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"), 
    ("A1", "G"), ("A2", "H")
]

for start, end in arrows:
    start_x, start_y, _ = boxes[start]
    end_x, end_y, _ = boxes[end]
    if start_x == end_x:
        ax.arrow(start_x + 0.15, start_y, 0, end_y - start_y - 0.1, head_width=0.02, head_length=0.02, fc='black', ec='black')
    else:
        ax.arrow(start_x + 0.3, start_y + 0.05, end_x - start_x - 0.3, 0, head_width=0.02, head_length=0.02, fc='black', ec='black')

# Set limits and remove axes
ax.set_xlim(0, 1)
ax.set_ylim(-0.3, 1)
ax.axis('off')

# Save and display the diagram
plt.savefig("/mnt/data/pizza_order_flow_diagram.png")
plt.show()
