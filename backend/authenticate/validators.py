# authenticate/validators.py
import re
from rest_framework import serializers

def validate_name(value):
    # nume simple: doar litere + spații
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$', value):
        raise serializers.ValidationError("Name must contain only letters and spaces.")
    return value

def validate_email_format(value):
    # validare simplă de email
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
        raise serializers.ValidationError("Invalid email format.")
    return value
