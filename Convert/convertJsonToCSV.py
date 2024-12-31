import json
import csv

def parse_other_attributes(data):
    """
    Extracts keys and values from the 'other_attributes' field in JSON objects
    and converts them into a dictionary.
    If the 'other_attributes' field is malformed or empty, logs it and returns an empty dictionary.
    """
    try:
        # Attempt to parse the 'other_attributes' field as JSON
        other_attributes = json.loads(data.get("other_attributes", "{}"))
    except (json.JSONDecodeError, TypeError) as e:
        # Log the error and the problematic 'other_attributes' field
        print(f"Error decoding 'other_attributes': {e}")
        print(f"Problematic data: {data.get('other_attributes', '')}")
        return {}
    return {key: value for key, value in other_attributes.items()}

def categorize_levels(categories):
    """
    Categorizes the 'categories' list into different levels based on the index.
    """
    levels = {}
    for i, category in enumerate(categories):
        levels[f"level{i + 1}"] = category
    return levels

def json_to_csv(json_data, csv_file_path):
    """
    Converts JSON data into a CSV file, dynamically creating columns
    from keys in the 'other_attributes' field.

    :param json_data: List of JSON objects.
    :param csv_file_path: Path to the output CSV file.
    """
    # Collect all unique keys from 'other_attributes' across all items.
    all_other_keys = set()
    max_categories_count = 0  # To keep track of the maximum number of categories

    for item in json_data:
        other_attributes = parse_other_attributes(item)
        all_other_keys.update(other_attributes.keys())
        # Track the maximum number of categories
        max_categories_count = max(max_categories_count, len(item.get("categories", [])))

    # Define the main columns from the JSON structure
    main_columns = [
        "final_name", "final_url", "product_id", "image_url", "brand", "delivery",
        "discount", "description", "stock", "star_rating", "reviews",
        "name_en", "descrption_en", "categories_en"
    ]

    # Dynamically create level columns based on the maximum number of categories
    level_columns = [f"level{i + 1}" for i in range(max_categories_count)]

    # Combine main columns with dynamic columns from 'other_attributes' and category levels
    columns = main_columns + list(all_other_keys) + level_columns

    # Write to CSV
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()

        for item in json_data:
            # Explicitly handle final_url to ensure it's correctly extracted
            url = item.get("final_url", "").strip()  # Ensure it's extracted correctly and strip any extra spaces
            if not url:
                print(f"Warning: Missing URL for product: {item.get('name', 'Unnamed product')}")
                url = "URL Missing"  # Optionally set a placeholder value

            # Transform categories into level columns
            categories = item.get("categories", [])
            categorized_levels = categorize_levels(categories)

            row = {key: item.get(key, "") for key in main_columns}
            row["final_url"] = url  # Explicitly set the final_url
            row.update(parse_other_attributes(item))  # Include 'other_attributes'
            row.update(categorized_levels)  # Add categorized levels to the row

            writer.writerow(row)

if __name__ == "__main__":
    # Specify the input JSON file path
    json_file_path = "final.json"
    
    # Specify the output CSV file path
    csv_file_path = "output.csv"

    # Read JSON data from the file
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        # Convert JSON to CSV
        json_to_csv(json_data, csv_file_path)
        print(f"Data has been written to {csv_file_path}")
    except FileNotFoundError:
        print(f"Error: The file {json_file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_file_path}. Please check the file's format.")
