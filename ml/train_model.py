import pandas as pd
import pickle
import numpy as np
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
import os

warnings.filterwarnings('ignore')

print("=" * 60)
print("🌾 AgroPulse - ML Model Training Pipeline")
print("=" * 60)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("\n📂 Loading data...")

try:
    df = pd.read_csv("ml/data/mandi_prices.csv")
    print(f"✅ Loaded {len(df):,} records")
except FileNotFoundError:
    print("❌ Error: ml/data/mandi_prices.csv not found")
    print("   Please ensure the file exists in ml/data/ directory")
    exit(1)
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit(1)

# ============================================================
# 2. DATA PREPROCESSING
# ============================================================
print("\n🔧 Preprocessing data...")

# Clean column names
df.columns = df.columns.str.strip()

# Display data info
print(f"\n   📊 Dataset Information:")
print(f"   - Total Records: {len(df):,}")
print(f"   - Columns: {list(df.columns)}")
print(f"   - Shape: {df.shape}")

# Check for missing values in required columns
required_cols = ['state', 'district', 'crop', 'modal_price']
missing = df[required_cols].isnull().sum()
if missing.any():
    print(f"\n   ⚠️  Missing values detected in required columns:")
    for col, count in missing[missing > 0].items():
        print(f"   - {col}: {count} missing")
    
    print(f"\n   🧹 Cleaning data...")
    original_len = len(df)
    df = df.dropna(subset=required_cols)
    print(f"   - Removed {original_len - len(df):,} rows with missing values")
    print(f"   - New dataset size: {len(df):,} records")

# Show data distribution
print(f"\n   📈 Data Distribution:")
print(f"   - Unique States: {df['state'].nunique()}")
print(f"   - Unique Districts: {df['district'].nunique()}")
print(f"   - Unique Crops: {df['crop'].nunique()}")
print(f"\n   Top 5 States:")
for state, count in df['state'].value_counts().head(5).items():
    print(f"   - {state}: {count} records")

print(f"\n   Top 10 Crops:")
for crop, count in df['crop'].value_counts().head(10).items():
    print(f"   - {crop}: {count} records")

# ============================================================
# 3. FEATURE ENGINEERING
# ============================================================
print("\n🔨 Engineering features...")

# Initialize encoders
state_enc = LabelEncoder()
district_enc = LabelEncoder()
crop_enc = LabelEncoder()

# Encode categorical features
df["state_enc"] = state_enc.fit_transform(df["state"])
df["district_enc"] = district_enc.fit_transform(df["district"])
df["crop_enc"] = crop_enc.fit_transform(df["crop"])

print(f"   ✅ Encoded categorical features")
print(f"   - States encoded: {len(state_enc.classes_)}")
print(f"   - Districts encoded: {len(district_enc.classes_)}")
print(f"   - Crops encoded: {len(crop_enc.classes_)}")

# Feature columns for the model
feature_cols = ["state_enc", "district_enc", "crop_enc"]

# ============================================================
# 4. PREPARE TRAINING DATA
# ============================================================
print("\n📊 Preparing training data...")

X = df[feature_cols]
y = df["modal_price"]

print(f"   Features: {feature_cols}")
print(f"   Target: Modal Price")
print(f"   Price Statistics:")
print(f"   - Minimum: ₹{y.min():.2f}")
print(f"   - Maximum: ₹{y.max():.2f}")
print(f"   - Mean: ₹{y.mean():.2f}")
print(f"   - Median: ₹{y.median():.2f}")

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

print(f"\n   📦 Data Split:")
print(f"   - Training samples: {len(X_train):,} ({len(X_train)/len(X)*100:.1f}%)")
print(f"   - Testing samples: {len(X_test):,} ({len(X_test)/len(X)*100:.1f}%)")

# ============================================================
# 5. TRAIN MODEL
# ============================================================
print("\n🤖 Training Random Forest model...")
print("   ⏳ This may take a minute...")

model = RandomForestRegressor(
    n_estimators=300,      # Number of trees
    max_depth=12,          # Maximum tree depth
    min_samples_split=5,   # Minimum samples to split
    min_samples_leaf=2,    # Minimum samples per leaf
    random_state=42,
    n_jobs=-1,             # Use all CPU cores
    verbose=0
)

model.fit(X_train, y_train)
print("   ✅ Model trained successfully!")

# ============================================================
# 6. EVALUATE MODEL
# ============================================================
print("\n📈 Evaluating model performance...")

# Predictions
train_preds = model.predict(X_train)
test_preds = model.predict(X_test)

# Metrics
train_mae = mean_absolute_error(y_train, train_preds)
test_mae = mean_absolute_error(y_test, test_preds)
train_rmse = np.sqrt(mean_squared_error(y_train, train_preds))
test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
train_r2 = r2_score(y_train, train_preds)
test_r2 = r2_score(y_test, test_preds)

print("\n   📊 Training Set Performance:")
print(f"   - MAE:  ₹{train_mae:.2f}")
print(f"   - RMSE: ₹{train_rmse:.2f}")
print(f"   - R² Score: {train_r2:.4f}")

print("\n   📊 Testing Set Performance:")
print(f"   - MAE:  ₹{test_mae:.2f}")
print(f"   - RMSE: ₹{test_rmse:.2f}")
print(f"   - R² Score: {test_r2:.4f}")

# Interpret results
print("\n   💡 Model Quality Assessment:")
if test_mae < 100:
    print(f"   ✅ EXCELLENT - Average error of ₹{test_mae:.2f} is very good!")
elif test_mae < 200:
    print(f"   ✅ GOOD - Average error of ₹{test_mae:.2f} is acceptable")
else:
    print(f"   ⚠️  FAIR - Average error of ₹{test_mae:.2f} could be improved")

if test_r2 > 0.8:
    print(f"   ✅ Model explains {test_r2*100:.1f}% of price variation")
elif test_r2 > 0.6:
    print(f"   ⚠️  Model explains {test_r2*100:.1f}% of price variation")
else:
    print(f"   ⚠️  Model explains only {test_r2*100:.1f}% of price variation")
    print(f"   💡 Consider adding more features or data")

# Cross-validation
print("\n   🔄 Running 5-fold cross-validation...")
cv_scores = cross_val_score(
    model, X, y, cv=5, 
    scoring='neg_mean_absolute_error',
    n_jobs=-1
)
cv_mae = -cv_scores.mean()
cv_std = cv_scores.std()
print(f"   - Cross-validation MAE: ₹{cv_mae:.2f} (±₹{cv_std:.2f})")

# Feature importance
print("\n   🎯 Feature Importance:")
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for _, row in feature_importance.iterrows():
    bar_length = int(row['importance'] * 50)
    bar = '█' * bar_length
    print(f"   {row['feature']:<15} {bar} {row['importance']:.4f}")

# ============================================================
# 7. TEST WITH SAMPLE PREDICTIONS
# ============================================================
print("\n🧪 Testing with sample predictions...")

# Get random samples
sample_indices = np.random.choice(len(X_test), min(5, len(X_test)), replace=False)

print("\n   Sample Predictions vs Actual:")
print("   " + "-" * 70)
for idx in sample_indices:
    actual = y_test.iloc[idx]
    predicted = test_preds[idx]
    error = abs(actual - predicted)
    
    # Get original values
    orig_idx = X_test.index[idx]
    state = df.loc[orig_idx, 'state']
    district = df.loc[orig_idx, 'district']
    crop = df.loc[orig_idx, 'crop']
    
    print(f"   {crop[:30]:<30} | {district[:15]:<15}")
    print(f"   Actual: ₹{actual:>7.2f} | Predicted: ₹{predicted:>7.2f} | Error: ₹{error:.2f}")
    print("   " + "-" * 70)

# ============================================================
# 8. SAVE MODEL & ARTIFACTS
# ============================================================
print("\n💾 Saving model and encoders...")

# Create ml directory if it doesn't exist
os.makedirs("ml", exist_ok=True)

# Save model
with open("ml/trained_model.pkl", "wb") as f:
    pickle.dump(model, f)
print("   ✅ Model saved: ml/trained_model.pkl")

# Save encoders
with open("ml/state_encoder.pkl", "wb") as f:
    pickle.dump(state_enc, f)
print("   ✅ State encoder saved: ml/state_encoder.pkl")

with open("ml/district_encoder.pkl", "wb") as f:
    pickle.dump(district_enc, f)
print("   ✅ District encoder saved: ml/district_encoder.pkl")

with open("ml/crop_encoder.pkl", "wb") as f:
    pickle.dump(crop_enc, f)
print("   ✅ Crop encoder saved: ml/crop_encoder.pkl")

# Save feature columns
with open("ml/feature_cols.pkl", "wb") as f:
    pickle.dump(feature_cols, f)
print("   ✅ Feature columns saved: ml/feature_cols.pkl")

# Save model metadata
metadata = {
    'train_date': datetime.now().isoformat(),
    'n_samples': len(df),
    'n_states': df['state'].nunique(),
    'n_districts': df['district'].nunique(),
    'n_crops': df['crop'].nunique(),
    'feature_cols': feature_cols,
    'test_mae': float(test_mae),
    'test_rmse': float(test_rmse),
    'test_r2': float(test_r2),
    'cv_mae': float(cv_mae),
    'model_params': model.get_params(),
    'supported_crops': list(crop_enc.classes_),
    'supported_states': list(state_enc.classes_),
    'supported_districts': list(district_enc.classes_)
}

with open("ml/model_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)
print("   ✅ Metadata saved: ml/model_metadata.pkl")

# ============================================================
# 9. FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("✅ MODEL TRAINING COMPLETE!")
print("=" * 60)
print(f"📊 Dataset Size: {len(df):,} records")
print(f"📊 Test MAE: ₹{test_mae:.2f}")
print(f"📊 Test RMSE: ₹{test_rmse:.2f}")
print(f"📊 Test R²: {test_r2:.4f}")
print(f"📊 CV MAE: ₹{cv_mae:.2f} (±₹{cv_std:.2f})")
print(f"\n🌾 Supported Crops: {len(crop_enc.classes_)}")
print(f"📍 Supported Districts: {len(district_enc.classes_)}")
print(f"🗺️  Supported States: {len(state_enc.classes_)}")
print("\n📁 All files saved in: ml/")
print("=" * 60)

print("\n💡 Next Steps:")
print("   1. Test the model: python ml/predict.py")
print("   2. Start Flask app: python app.py")
print("   3. Make predictions via API or web interface")
print("\n🎉 Happy Predicting!")