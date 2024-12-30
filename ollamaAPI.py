import json
import asyncio
import ollama

async def handle_products_translation():
    with open("tukku_products_detail_category.json", "r", encoding="utf-8") as f:
        products = json.load(f)
        pointer = [0]
        item_per_file = 100
        tasks = [translate_attributes(product, pointer, item_per_file, len(products), products) for product in products[0:3759]]
        await asyncio.gather(*tasks)
        with open("final_data/final.json", "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

async def translate_attributes(product, pointer, item_per_file,  products_num, products):
    try:
        product["name_en"] = await translate(product["name"])
        product["descrption_en"] = await translate(product["description"])
        product["categories_en"] = (await translate(",".join(product["categories"]))).split(",")
        product["other_attributes"] = await get_dynamic_attributes(product)
        pointer[0] += 1
        print(f"{pointer[0]}/{products_num} ({(pointer[0] / products_num) * 100:.2f}%)")
    except Exception as e:
        print(f"error: {e}")

    if pointer[0] % item_per_file == 0:
        with open(f"final_data/{pointer[0]-item_per_file}-{pointer[0]}.json", "w", encoding="utf-8") as f:
            json.dump(products[pointer[0]-item_per_file:pointer[0]], f, ensure_ascii=False, indent=2)
        print(f"Progress saved at {pointer[0]} products")


async def get_dynamic_attributes(product):
    product_description = product["description"]
    product_name = product["name"]

    prompt = f"""
        Analyze the following product description and name to identify and extract useful attributes of the product, 
        such as " "size", "color", "height", "weight", you don't have to include all of what I mentioned attributes,
    for e.g. If there's no height, don't list this. and any other relevant details. You don't have to list attributes
    with not mentioned value.Make sure the output contains only the JSON object with key-value pairs, without escape
    characters or extra formatting.Respond with the extracted attributes in compact JSON format, with no line breaks 
    or extra spaces.Make sure clean, unescaped JSON format without any backslashes or special characters.Provide the
    extracted information in with English attribute version.
    Product description:
    "{product_description}" 
    Product name:
    "{product_name}"
    """

    return await generate_response_from_ollama(prompt)

async def translate(originalText):
    return await generate_response_from_ollama('Translate the following Finnish text into English directly, and respond with only the translated text. Do not add any introductory words or phrases:' + originalText)

async def generate_response_from_ollama(prompt):
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    return response['message']['content']
