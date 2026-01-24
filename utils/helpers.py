from datetime import datetime, timedelta
import math

def get_date_range(days_back=90):
    """Get date range for historical data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates (Haversine formula)"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return round(distance, 2)

def format_price(price):
    """Format price with currency symbol"""
    return f"₹{price:,.2f}"

def calculate_percentage_change(old_value, new_value):
    """Calculate percentage change"""
    if old_value == 0:
        return 0
    
    change = ((new_value - old_value) / old_value) * 100
    return round(change, 2)

def get_future_dates(days=7):
    """Get list of future dates"""
    dates = []
    current_date = datetime.now()
    
    for i in range(1, days + 1):
        future_date = current_date + timedelta(days=i)
        dates.append(future_date.strftime('%Y-%m-%d'))
    
    return dates

def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

def format_response(success, data=None, message=None, errors=None):
    """Format API response"""
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if errors:
        response['errors'] = errors
    
    return response

def get_season(date):
    """Get crop season based on date"""
    month = date.month
    
    if month in [10, 11, 12, 1, 2, 3]:
        return 'Rabi'  # Winter crops
    elif month in [4, 5, 6]:
        return 'Zaid'  # Summer crops
    else:
        return 'Kharif'  # Monsoon crops

def safe_divide(numerator, denominator, default=0):
    """Safe division with default value"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default