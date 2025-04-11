import pandas as pd

# Load the CSV file
input_file = "redits.csv"
data = pd.read_csv(input_file)

data_sorted = data.sort_values(by="size", ascending=False).head(2000)

user_files = {f"user_{i+1}.csv": [] for i in range(4)}

for index, row in data_sorted.iterrows():
    user_index = index % 4  # Determine which user to assign to (0, 1, 2, 3)
    user_files[f"user_{user_index+1}.csv"].append(row)

for user_file, rows in user_files.items():
    user_data = pd.DataFrame(rows, columns=["subreddit"])
    user_data.to_csv(user_file, index=False,header=False)

print("Subreddits have been assigned and saved to user CSV files.")