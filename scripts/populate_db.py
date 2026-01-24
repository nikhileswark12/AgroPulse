import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_connection import get_collection, db
from config import Config
from datetime import datetime, timedelta
import random

def generate_sample_prices():
    """Generate sample price data for testing"""
    
    crops = ['Wheat', 'Rice', 'Soybean', 'Cotton', 'Corn']
    
    markets = [
        {'name': 'Indore APMC', 'district': 'Indore', 'state': 'Madhya Pradesh'},
        {'name': 'Dewas APMC', 'district': 'Dewas', 'state': 'Madhya Pradesh'},
        {'name': 'Ujjain FPO', 'district': 'Ujjain', 'state': 'Madhya Pradesh'},
        {'name': 'Bhopal APMC', 'district': 'Bhopal', 'state': 'Madhya Pradesh'},
        {'name': 'Jabalpur Mandi', 'district': 'Jabalpur', 'state': 'Madhya Pradesh'}
    ]
    
    # Base prices for crops
    base_prices = {
        'Wheat': 2000,
        'Rice': 2500,
        'Soybean': 4000,
        'Cotton': 5500,
        'Corn': 1800
    }
    
    prices = []
    
    # Generate 90 days of historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for crop in crops:
        base_price = base_prices[crop]
        current_price = base_price
        
        for day in range(91):
            date = start_date + timedelta(days=day)
            
            # Add trend (slight upward trend with volatility)
            trend = day * 2  # +2 rupees per day trend
            volatility = random.randint(-50, 100)  # Daily volatility
            
            current_price = base_price + trend + volatility
            
            # Generate prices for each market
            for market in markets:
                # Each market has slightly different prices
                market_variation = random.randint(-100, 150)
                modal_price = current_price + market_variation
                
                price_doc = {
                    'crop': crop,
                    'mandi_name': market['name'],
                    'district': market['district'],
                    'state': market['state'],
                    'modal_price': max(modal_price, 100),  # Ensure positive price
                    'min_price': max(modal_price - 50, 50),
                    'max_price': modal_price + 100,
                    'date': date.strftime('%Y-%m-%d'),
                    'arrival_quantity': random.randint(100, 1000),
                    'type': 'FPO' if 'FPO' in market['name'] else 'APMC',
                    'created_at': datetime.now()
                }
                
                prices.append(price_doc)
    
    return prices

def generate_sample_markets():
    """Generate sample market data"""
    
    markets = [
        {
            'mandi_name': 'Indore APMC',
            'district': 'Indore',
            'state': 'Madhya Pradesh',
            'type': 'APMC',
            'location': {
                'type': 'Point',
                'coordinates': [75.8577, 22.7196]
            },
            'contact': {
                'phone': '0731-2234567',
                'email': 'indore.apmc@mp.gov.in'
            },
            'crops_accepted': ['Wheat', 'Rice', 'Soybean', 'Cotton', 'Corn'],
            'timings': '8 AM - 6 PM',
            'facilities': ['Storage', 'Quality Testing', 'Digital Payment']
        },
        {
            'mandi_name': 'Dewas APMC',
            'district': 'Dewas',
            'state': 'Madhya Pradesh',
            'type': 'APMC',
            'location': {
                'type': 'Point',
                'coordinates': [76.0534, 22.9676]
            },
            'contact': {
                'phone': '0731-8765432',
                'email': 'dewas.apmc@mp.gov.in'
            },
            'crops_accepted': ['Wheat', 'Soybean', 'Corn'],
            'timings': '8 AM - 6 PM',
            'facilities': ['Storage', 'Quality Testing', 'Digital Payment']
        },
        {
            'mandi_name': 'Ujjain FPO',
            'district': 'Ujjain',
            'state': 'Madhya Pradesh',
            'type': 'FPO',
            'location': {
                'type': 'Point',
                'coordinates': [75.7849, 23.1765]
            },
            'contact': {
                'phone': '0734-5551234',
                'email': 'ujjain.fpo@gmail.com'
            },
            'crops_accepted': ['Wheat', 'Soybean'],
            'timings': '9 AM - 5 PM',
            'facilities': ['Quality Testing']
        },
        {
            'mandi_name': 'Bhopal APMC',
            'district': 'Bhopal',
            'state': 'Madhya Pradesh',
            'type': 'APMC',
            'location': {
                'type': 'Point',
                'coordinates': [77.4126, 23.2599]
            },
            'contact': {
                'phone': '0755-1234567',
                'email': 'bhopal.apmc@mp.gov.in'
            },
            'crops_accepted': ['Wheat', 'Rice', 'Soybean', 'Cotton'],
            'timings': '8 AM - 6 PM',
            'facilities': ['Storage', 'Quality Testing', 'Digital Payment', 'Cold Storage']
        },
        {
            'mandi_name': 'Jabalpur Mandi',
            'district': 'Jabalpur',
            'state': 'Madhya Pradesh',
            'type': 'APMC',
            'location': {
                'type': 'Point',
                'coordinates': [79.9864, 23.1815]
            },
            'contact': {
                'phone': '0761-9876543',
                'email': 'jabalpur.mandi@mp.gov.in'
            },
            'crops_accepted': ['Rice', 'Wheat', 'Corn'],
            'timings': '8 AM - 6 PM',
            'facilities': ['Storage', 'Quality Testing']
        }
    ]
    
    return markets

def populate_database():
    """Populate database with sample data"""
    
    print("=" * 60)
    print("🌾 AgroPulse Database Population")
    print("=" * 60)
    print("\nConnecting to MongoDB...")
    
    # Connect to database first
    db.connect()
    
    prices_collection = get_collection(Config.PRICES_COLLECTION)
    markets_collection = get_collection(Config.MARKETS_COLLECTION)
    
    # Clear existing data
    print("Clearing existing data...")
    prices_collection.delete_many({})
    markets_collection.delete_many({})
    
    # Generate and insert prices
    print("\nGenerating sample price data...")
    prices = generate_sample_prices()
    print(f"Generated {len(prices)} price records")
    
    print("Inserting price records into MongoDB...")
    prices_collection.insert_many(prices)
    print(f"✅ Inserted {len(prices)} price records")
    
    # Generate and insert markets
    print("\nGenerating sample market data...")
    markets = generate_sample_markets()
    print(f"Generated {len(markets)} market records")
    
    print("Inserting market records into MongoDB...")
    markets_collection.insert_many(markets)
    print(f"✅ Inserted {len(markets)} market records")
    
    print("\n" + "=" * 60)
    print("✅ Database populated successfully!")
    print("=" * 60)
    print(f"\n📊 Data Summary:")
    print(f"   - Price records: {prices_collection.count_documents({})}")
    print(f"   - Market records: {markets_collection.count_documents({})}")
    print(f"   - Crops: Wheat, Rice, Soybean, Cotton, Corn")
    print(f"   - Districts: Indore, Dewas, Ujjain, Bhopal, Jabalpur")
    print(f"   - Date range: Last 90 days")
    print("\n🚀 Ready to run: python app.py")
    print("=" * 60)

if __name__ == '__main__':
    try:
        populate_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure MongoDB is running!")