import matplotlib.pyplot as plt

# Sample Data
# Assuming the data is collected like this:
episode_differences = [1.0, 0.8, 0.9, 0.7, 0.6, 0.8, 0.5, 0.4, 0.3, 0.2, 0.1]  # Data after each episode
test_differences = [0.9, 0.6, 0.4]  # Data after every 5 episodes (tests)

def createAverageDifferencePlot():
    # X-axis: Episode numbers (for both episode and test data)
    episodes = list(range(1, len(episode_differences) + 1))

    # X-axis: Test numbers (every 5th episode)
    tests = [i * 5 for i in range(1, len(test_differences) + 1)]

    # Create a plot
    plt.figure(figsize=(10, 6))

    # Plotting the average difference after each episode
    plt.plot(episodes, episode_differences, label="Episode Average Difference", color='blue', marker='o', linestyle='-', markersize=5)

    # Plotting the average difference after each test
    plt.plot(tests, test_differences, label="Test Average Difference", color='red', marker='x', linestyle='-', markersize=8)

    # Adding labels and title
    plt.title("Average Difference to Expected Results Over Episodes and Tests")
    plt.xlabel("Episode / Test Number")
    plt.ylabel("Average Difference to Expected Results")
    plt.legend()

    # Display grid
    plt.grid(True)

    return plt

createAverageDifferencePlot().show()
