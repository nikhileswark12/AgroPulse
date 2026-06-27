from datetime import datetime, timedelta
import math

def get_date_range(days_back=90):
    """Get date range for historical data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates (Haversine formula)"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R * c, 1)

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

def get_page(args):
    """Extract pagination parameters from request arguments"""
    try:
        # args could be request.args (dict-like) or a plain dict
        page = int(args.get('page', 1))
        per_page = int(args.get('per_page', 20))
        page = max(1, page)
        per_page = max(1, min(100, per_page))
    except (ValueError, TypeError, AttributeError):
        page = 1
        per_page = 20
        
    return {
        'skip': (page - 1) * per_page,
        'limit': per_page,
        'page': page,
        'per_page': per_page
    }

def paginated_response(data, total, page, per_page):
    """Format paginated response"""
    return {
        'success': True,
        'data': data,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': math.ceil(total / per_page) if per_page else 0
    }

def validate_origin(request, allowed_origins):
    """Validate Origin or Referer header against allowed origins"""
    origin = request.headers.get('Origin')
    referer = request.headers.get('Referer')
    
    check_url = origin or referer
    if not check_url:
        return False
        
    for allowed in allowed_origins:
        if check_url.startswith(allowed):
            return True
            
    return False