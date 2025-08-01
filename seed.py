# seed.py

from app import db, FoodItem

# Create all tables
db.create_all()

# Clear existing records (optional: use this if you want to reset data each time)
FoodItem.query.delete()

# Sample food data
sample_foods = [
    {"name": "Grilled Chicken", "suitable_for": "Low BP,High BP,Diabetes"},
    {"name": "Oatmeal", "suitable_for": "High BP,Diabetes"},
    {"name": "Banana", "suitable_for": "Low BP,Fever,Cold"},
    {"name": "Green Tea", "suitable_for": "Migraine,Thyroid"},
    {"name": "Soup", "suitable_for": "Fever,Cold,Cough"},
    {"name": "Steamed Veggies", "suitable_for": "Diabetes,Heart Disease"},
    {"name": "Fruit Salad", "suitable_for": "Cold,Low BP"},
    {"name": "Brown Rice", "suitable_for": "Thyroid,Diabetes"},
    {"name": "Turmeric Milk", "suitable_for": "Cough,Fever"},
    {"name": "Boiled Eggs", "suitable_for": "Low BP,Migraine"},
    {"name": "Avocado Toast", "suitable_for": "High BP,Thyroid"},
    {"name": "Quinoa Bowl", "suitable_for": "Diabetes,Migraine"},
    {"name": "Vegetable Khichdi", "suitable_for": "Fever,Cold"},
    {"name": "Baked Fish", "suitable_for": "Heart Disease,Low BP"},
    {"name": "Coconut Water", "suitable_for": "Fever,Low BP"},
    {"name": "Carrot Soup", "suitable_for": "Cold,Cough"},
    {"name": "Herbal Tea", "suitable_for": "Migraine,Cold"},
    {"name": "Sprouts", "suitable_for": "Thyroid,High BP"},
    {"name": "Sweet Potato", "suitable_for": "Diabetes,Low BP"},
    {"name": "Whole Wheat Bread", "suitable_for": "Thyroid,Heart Disease"}
]

# Add to database
for food in sample_foods:
    item = FoodItem(name=food['name'], suitable_for=food['suitable_for'])
    db.session.add(item)

# Save to DB
db.session.commit()
print("✅ Database seeded successfully!")
