# Product Requirement Document (PRD) - AgroPulse

## 1. Introduction
Agricultural markets in India often suffer from high price volatility and lack of transparent information channels. Farmers rely on middlemen or manual checks to decide where to sell their crops. AgroPulse bridges this gap by providing an intelligent platform for real-time price monitoring, market comparison, and AI-powered 7-day price forecasts.

## 2. Target Personas
- **Ram Singh (Farmer)**: Owns 5 acres of land in Indore. Wants to check wheat prices across nearby mandis and know if prices will rise in the next few days to optimize his harvest sales.
- **Sunita Patel (FPO Lead)**: Coordinates crop sales for 150 local farmers in Dewas. Needs to compare different mandi categories (APMC vs FPOs) quickly to organize bulk sales.
- **Rohan Verma (Agri-trader / Analyst)**: Monitors pricing trends to hedge trade positions. Uses price history logs to gauge volatility.

## 3. Core Features & Scope
- **User Authentication & Verification**: Signup, login, password resets, and verification emails to ensure only registered users save records.
- **Interactive Price Predictions**: Form input (State, District, Crop) providing a 7-day predicted price range (with margins based on Mean Absolute Error) and dynamic recommendation advice (Sell/Wait).
- **Mandi Comparisons**: Crop price listings sorted by value and distance, identifying the best available market rate.
- **Historical Query Log**: Authenticated dashboard tab enabling users to review and manage previous prediction calls.
- **Dynamic Price Database Updates**: Background ingestion scripts syncing fresh Agmarknet market logs with local price history tables.

## 4. Key Product Metrics (KPIs)
- **Prediction Accuracy**: MAE < ₹150 for Wheat and Soybean.
- **User Engagement**: Number of weekly prediction queries saved per active user.
- **System Load**: Prediction page load times (< 1.5 seconds under cache hits).
- **Data Integrity**: Zero duplicates across the `prices` and `markets` collections.
