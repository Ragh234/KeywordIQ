import json

with open("output/products.json") as f:
    data = json.load(f)

print(f"Total products: {len(data)}\n")
print(f"{'Rating':7} {'Reviews':>8}  {'URL (first 60)'}")
print("-" * 80)
for p in data[:10]:
    url = p["product_url"][:60] if p["product_url"] != "N/A" else "N/A"
    print(f"{p['rating']:7} {p['review_count']:>8}  {url}")
