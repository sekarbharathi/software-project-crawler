import json

import time

from deep_translator import GoogleTranslator
 
def translate_product_data(file_path):

    # Load product data from the JSON file

    with open(file_path, "r", encoding="utf-8") as f:

        products = json.load(f)
 
    translator = GoogleTranslator(source='fi', target='en')
 
    for product in products:

        # Translate the name if it exists

        if "name" in product and product["name"]:

            try:

                product["name_en"] = translator.translate(product["name"])

            except Exception as e:

                print(f"Error translating name for product ID {product.get('product_id', 'unknown')}: {e}")

        # Translate the description if it exists

        if "description" in product and product["description"]:

            try:

                product["description_en"] = translator.translate(product["description"])

            except Exception as e:

                print(f"Error translating description for product ID {product.get('product_id', 'unknown')}: {e}")
 
        # Pause to avoid hitting API rate limits

        time.sleep(1)
 
    # Save the translated data back to a JSON file

    output_file_path = file_path.replace(".json", "_translated.json")

    with open(output_file_path, "w", encoding="utf-8") as f:

        json.dump(products, f, ensure_ascii=False, indent=2)
 
if __name__ == "__main__":

    translate_product_data("tukku_one.json")

 