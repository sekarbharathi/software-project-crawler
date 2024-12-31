import json
import csv

def json_to_csv(json_file_path, csv_file_path):
    """
    Converts a JSON file to a CSV, dynamically extracting columns from `other_attributes`
    and ensuring that each unique key appears as a column in the CSV. It also dynamically 
    splits categories into category levels (Level1, Level2, etc.).
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Define the base headers (fields that are consistent across products)
    base_headers = [
        "name", "url", "product_id", "image_url", "brand", "delivery", "price",
        "discount", "description", "stock", "categories", "star_rating",
        "reviews", "name_en", "descrption_en", "categories_en"
    ]
    
    # Collect unique keys from all products' `other_attributes`
    unique_keys = set()
    max_categories_count = 0  # Track the maximum number of category levels
    
    for product in data:
        # Parse `other_attributes` if it's a string that looks like JSON
        other_attributes_str = product.get("other_attributes", "")
        if isinstance(other_attributes_str, str):
            try:
                # Parse the string as JSON to get it as a dictionary
                other_attributes = json.loads(other_attributes_str)
                if isinstance(other_attributes, dict):
                    unique_keys.update(other_attributes.keys())
            except json.JSONDecodeError:
                # Handle the case where the string is not valid JSON
                print(f"Invalid JSON in 'other_attributes' for product {product.get('name', 'Unknown')}")
        
        # Count the number of categories (split by ';')
        categories = product.get("categories", [])
        if categories:
            max_categories_count = max(max_categories_count, len(categories))  # Update max count

    # Dynamically create category level columns based on the maximum number of categories
    level_columns = [f"Level{i + 1}" for i in range(max_categories_count)]
    
    # Sort and add the unique keys from `other_attributes` to the headers
    all_headers = base_headers + level_columns + sorted(unique_keys)

    # Write the CSV file
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(all_headers)  # Write the header row
        
        # Iterate through the JSON data and write each row
        for product in data:
            # Start with the base fields
            row = [
                product.get("name", ""),
                product.get("url", ""),
                product.get("product_id", ""),
                product.get("image_url", ""),
                product.get("brand", ""),
                product.get("delivery", ""),
                product.get("price", ""),
                product.get("discount", ""),
                product.get("description", "").replace('\n', ' '),
                product.get("stock", ""),
                "; ".join(product.get("categories", [])),
                product.get("star_rating", 0),
                product.get("reviews", ""),
                product.get("name_en", ""),
                product.get("descrption_en", "").replace('\n', ' '),
                "; ".join(product.get("categories_en", []))
            ]
            
            # Process categories and split into levels
            categories = product.get("categories", [])
            # Fill in the category level columns dynamically
            for i in range(max_categories_count):
                row.append(categories[i] if i < len(categories) else "")  # Add category level or empty
            
            # Parse `other_attributes` if it's a string that looks like JSON
            other_attributes_str = product.get("other_attributes", "")
            if isinstance(other_attributes_str, str):
                try:
                    other_attributes = json.loads(other_attributes_str)
                    # Add values from `other_attributes` for each unique key
                    for key in sorted(unique_keys):  # Ensure the order is consistent
                        row.append(other_attributes.get(key, ""))  # Add value or empty string
                except json.JSONDecodeError:
                    row.extend([""] * len(unique_keys))  # If invalid, add empty values
            else:
                row.extend([""] * len(unique_keys))  # If no `other_attributes`, add empty values
            
            writer.writerow(row)

    print(f"JSON data has been successfully converted to CSV with expanded other_attributes and category levels saved to {csv_file_path}")

def main():
    # Define file paths
    json_file_path = "merged_file.json"  # Replace with your JSON file path
    csv_file_path = "new_converted_output_with_levels.csv"  # Desired output CSV file path

    # Convert JSON to CSV
    json_to_csv(json_file_path, csv_file_path)

if __name__ == "__main__":
    main()
