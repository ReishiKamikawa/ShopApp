from bson import ObjectId
try:
    oid = ObjectId("507f1f77bcf86cd799439099")
    print(f"Valid: {oid}")
except Exception as e:
    print(f"Invalid: {e}")
