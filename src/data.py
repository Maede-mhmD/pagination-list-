# لیست تستی ساده
DATA = [
    {"id": i, "name": f"Item {i}", "category": "Category A" if i % 2 == 0 else "Category B"}
    for i in range(1, 101)
]
