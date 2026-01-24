from config import Config
from datetime import datetime

def validate_crop(crop):
    """Validate crop name"""
    if not crop:
        return False, "Crop name is required"
    
    if crop not in Config.SUPPORTED_CROPS:
        return False, f"Crop '{crop}' not supported. Supported crops: {', '.join(Config.SUPPORTED_CROPS)}"
    
    return True, None

def validate_location(location):
    """Validate location (district)"""
    if not location:
        return False, "Location is required"
    
    if len(location) < 2:
        return False, "Location name too short"
    
    return True, None

def validate_quantity(quantity):
    """Validate quantity"""
    if quantity is None:
        return True, None  # Quantity is optional
    
    try:
        qty = float(quantity)
        if qty <= 0:
            return False, "Quantity must be greater than 0"
        if qty > 10000:
            return False, "Quantity too large (max: 10000 quintals)"
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid quantity format"

def validate_date(date_str):
    """Validate date string"""
    if not date_str:
        return False, "Date is required"
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"

def validate_price_request(data):
    """Validate price request data"""
    errors = []
    
    # Validate crop
    valid, error = validate_crop(data.get('crop'))
    if not valid:
        errors.append(error)
    
    # Validate location
    valid, error = validate_location(data.get('location'))
    if not valid:
        errors.append(error)
    
    # Validate quantity (optional)
    if 'quantity' in data:
        valid, error = validate_quantity(data.get('quantity'))
        if not valid:
            errors.append(error)
    
    if errors:
        return False, errors
    
    return True, None

def validate_prediction_request(data):
    """Validate prediction request data"""
    errors = []
    
    # Validate crop
    valid, error = validate_crop(data.get('crop'))
    if not valid:
        errors.append(error)
    
    # Validate location
    valid, error = validate_location(data.get('location'))
    if not valid:
        errors.append(error)
    
    if errors:
        return False, errors
    
    return True, None