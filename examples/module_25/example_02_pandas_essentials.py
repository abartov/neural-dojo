#!/usr/bin/env python3
"""
Module 25 Example 2: pandas Essentials

Demonstrates pandas DataFrame operations essential for
machine learning data preparation and analysis.

pandas is your Swiss Army knife for data manipulation.
"""

import pandas as pd
import numpy as np
from io import StringIO


# =============================================================================
# Part 1: Creating DataFrames
# =============================================================================

def demo_creating_dataframes():
    """Demonstrate various ways to create pandas DataFrames."""
    print("\n" + "="*60)
    print("Part 1: Creating DataFrames")
    print("="*60)

    # From dictionary
    print("\n--- From Dictionary ---")
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'age': [25, 30, 35, 28],
        'salary': [50000, 60000, 70000, 55000],
        'department': ['Engineering', 'Sales', 'Engineering', 'Marketing']
    })
    print(df)

    # From lists
    print("\n--- From Lists ---")
    data = [
        ['Alice', 25, 50000],
        ['Bob', 30, 60000],
        ['Charlie', 35, 70000]
    ]
    df2 = pd.DataFrame(data, columns=['name', 'age', 'salary'])
    print(df2)

    # From NumPy array
    print("\n--- From NumPy Array ---")
    np_data = np.random.randn(5, 3)
    df3 = pd.DataFrame(np_data, columns=['feature_1', 'feature_2', 'feature_3'])
    print(df3.round(3))

    # From CSV string (simulating file read)
    print("\n--- From CSV Data ---")
    csv_data = """name,age,salary
Alice,25,50000
Bob,30,60000
Charlie,35,70000"""
    df4 = pd.read_csv(StringIO(csv_data))
    print(df4)

    return df


# =============================================================================
# Part 2: Exploring Data
# =============================================================================

def demo_exploring_data():
    """Demonstrate data exploration techniques."""
    print("\n" + "="*60)
    print("Part 2: Exploring Data")
    print("="*60)

    # Create a more complex dataset
    np.random.seed(42)
    n = 100

    df = pd.DataFrame({
        'id': range(1, n + 1),
        'age': np.random.randint(18, 65, n),
        'salary': np.random.normal(60000, 15000, n).round(2),
        'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR'], n),
        'experience': np.random.randint(0, 20, n),
        'rating': np.random.uniform(1, 5, n).round(1),
        'is_manager': np.random.choice([True, False], n, p=[0.2, 0.8])
    })

    # Add some missing values
    df.loc[np.random.choice(df.index, 5), 'salary'] = np.nan
    df.loc[np.random.choice(df.index, 3), 'rating'] = np.nan

    print("\n--- Quick Overview ---")
    print(f"Shape: {df.shape} (rows, columns)")
    print(f"\nFirst 5 rows:")
    print(df.head())

    print(f"\nLast 3 rows:")
    print(df.tail(3))

    print("\n--- Data Types ---")
    print(df.dtypes)

    print("\n--- Info ---")
    df.info()

    print("\n--- Statistical Summary ---")
    print(df.describe().round(2))

    print("\n--- Categorical Column Summary ---")
    print(df['department'].value_counts())

    print("\n--- Missing Values ---")
    print(df.isnull().sum())

    print("\n--- Memory Usage ---")
    print(df.memory_usage(deep=True))

    return df


# =============================================================================
# Part 3: Selecting Data
# =============================================================================

def demo_selecting_data(df: pd.DataFrame):
    """Demonstrate various data selection methods."""
    print("\n" + "="*60)
    print("Part 3: Selecting Data")
    print("="*60)

    print(f"\nDataFrame shape: {df.shape}")

    # Column selection
    print("\n--- Column Selection ---")
    print("Single column (df['age']):")
    print(df['age'].head())

    print("\nMultiple columns (df[['age', 'salary']]):")
    print(df[['age', 'salary']].head())

    # Row selection with .loc (label-based)
    print("\n--- Row Selection with .loc (label-based) ---")
    print("df.loc[0] (first row):")
    print(df.loc[0])

    print("\ndf.loc[0:3] (rows 0 to 3, inclusive):")
    print(df.loc[0:3])

    print("\ndf.loc[0:3, 'age':'salary'] (rows and columns slice):")
    print(df.loc[0:3, 'age':'salary'])

    # Row selection with .iloc (integer-based)
    print("\n--- Row Selection with .iloc (integer-based) ---")
    print("df.iloc[0] (first row):")
    print(df.iloc[0])

    print("\ndf.iloc[0:3] (first 3 rows, exclusive end):")
    print(df.iloc[0:3])

    print("\ndf.iloc[:, 0:3] (first 3 columns):")
    print(df.iloc[:5, 0:3])

    # Boolean selection
    print("\n--- Boolean Selection (Very Powerful!) ---")
    print("Engineers:")
    print(df[df['department'] == 'Engineering'].head())

    print("\nHigh earners (salary > 70000):")
    print(df[df['salary'] > 70000].head())

    print("\nEngineers with salary > 60000:")
    print(df[(df['department'] == 'Engineering') & (df['salary'] > 60000)].head())

    # Query method (cleaner syntax)
    print("\n--- Query Method ---")
    print("df.query('age > 40 and salary > 50000'):")
    print(df.query('age > 40 and salary > 50000').head())


# =============================================================================
# Part 4: Data Cleaning
# =============================================================================

def demo_data_cleaning():
    """Demonstrate data cleaning operations."""
    print("\n" + "="*60)
    print("Part 4: Data Cleaning")
    print("="*60)

    # Create messy data
    df = pd.DataFrame({
        'name': ['  Alice  ', 'BOB', 'Charlie', 'alice', 'Bob', np.nan],
        'age': [25, 30, np.nan, 25, 30, 40],
        'salary': [50000, np.nan, 70000, 50000, 60000, 80000],
        'email': ['alice@email.com', 'bob@email.com', 'charlie@', 'alice@email.com', 'bob@email.com', '']
    })

    print("Original (messy) data:")
    print(df)

    # Handle missing values
    print("\n--- Handling Missing Values ---")
    print(f"Missing values per column:\n{df.isnull().sum()}")

    # Fill missing values
    df_filled = df.copy()
    df_filled['age'] = df_filled['age'].fillna(df_filled['age'].median())
    df_filled['salary'] = df_filled['salary'].fillna(df_filled['salary'].mean())
    df_filled['name'] = df_filled['name'].fillna('Unknown')

    print("\nAfter filling missing values:")
    print(df_filled)

    # String cleaning
    print("\n--- String Cleaning ---")
    df_clean = df_filled.copy()
    df_clean['name'] = df_clean['name'].str.strip().str.title()
    print("After strip and title case:")
    print(df_clean['name'])

    # Remove duplicates
    print("\n--- Removing Duplicates ---")
    print(f"Before: {len(df_clean)} rows")
    df_clean = df_clean.drop_duplicates(subset=['name', 'age'])
    print(f"After: {len(df_clean)} rows")
    print(df_clean)

    # Data type conversion
    print("\n--- Data Type Conversion ---")
    df_types = pd.DataFrame({
        'date_str': ['2024-01-01', '2024-02-01', '2024-03-01'],
        'value_str': ['100', '200', '300'],
        'category': ['A', 'B', 'A']
    })

    print("Original types:")
    print(df_types.dtypes)

    df_types['date'] = pd.to_datetime(df_types['date_str'])
    df_types['value'] = df_types['value_str'].astype(int)
    df_types['category'] = df_types['category'].astype('category')

    print("\nAfter conversion:")
    print(df_types.dtypes)


# =============================================================================
# Part 5: Transforming Data
# =============================================================================

def demo_transformations():
    """Demonstrate data transformation operations."""
    print("\n" + "="*60)
    print("Part 5: Transforming Data")
    print("="*60)

    np.random.seed(42)
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 42],
        'salary': [50000, 60000, 70000, 55000, 90000],
        'department': ['Engineering', 'Sales', 'Engineering', 'Marketing', 'Sales']
    })

    print("Original data:")
    print(df)

    # Create new columns
    print("\n--- Creating New Columns ---")
    df['salary_k'] = df['salary'] / 1000
    df['years_to_retire'] = 65 - df['age']
    df['monthly_salary'] = df['salary'] / 12

    print(df[['name', 'salary', 'salary_k', 'monthly_salary']])

    # Apply functions
    print("\n--- Apply Functions ---")
    df['age_category'] = df['age'].apply(lambda x: 'Young' if x < 30 else 'Senior')
    print(df[['name', 'age', 'age_category']])

    # Map values
    print("\n--- Map Values ---")
    dept_codes = {'Engineering': 'ENG', 'Sales': 'SAL', 'Marketing': 'MKT'}
    df['dept_code'] = df['department'].map(dept_codes)
    print(df[['name', 'department', 'dept_code']])

    # Binning
    print("\n--- Binning (cut) ---")
    df['age_bin'] = pd.cut(df['age'], bins=[0, 25, 35, 50, 100],
                           labels=['Junior', 'Mid', 'Senior', 'Executive'])
    print(df[['name', 'age', 'age_bin']])

    # One-hot encoding
    print("\n--- One-Hot Encoding ---")
    df_encoded = pd.get_dummies(df[['name', 'department']], columns=['department'])
    print(df_encoded)

    # Apply to entire DataFrame
    print("\n--- Apply to Multiple Columns ---")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df_normalized = df[numeric_cols].apply(lambda x: (x - x.mean()) / x.std())
    print("Z-score normalized:")
    print(df_normalized.round(3))


# =============================================================================
# Part 6: Grouping and Aggregation
# =============================================================================

def demo_groupby():
    """Demonstrate groupby operations for aggregation."""
    print("\n" + "="*60)
    print("Part 6: Grouping and Aggregation")
    print("="*60)

    np.random.seed(42)
    df = pd.DataFrame({
        'department': np.random.choice(['Engineering', 'Sales', 'Marketing'], 20),
        'level': np.random.choice(['Junior', 'Mid', 'Senior'], 20),
        'salary': np.random.normal(60000, 15000, 20).round(0),
        'bonus': np.random.uniform(0, 10000, 20).round(0),
        'rating': np.random.uniform(1, 5, 20).round(1)
    })

    print("Sample data:")
    print(df.head(10))

    # Basic groupby
    print("\n--- Basic Groupby ---")
    print("Mean salary by department:")
    print(df.groupby('department')['salary'].mean().round(0))

    print("\nMultiple aggregations:")
    print(df.groupby('department')['salary'].agg(['mean', 'min', 'max', 'count']))

    # Multiple grouping columns
    print("\n--- Multiple Grouping Columns ---")
    print("Mean salary by department and level:")
    print(df.groupby(['department', 'level'])['salary'].mean().round(0))

    # Multiple aggregations on multiple columns
    print("\n--- Complex Aggregations ---")
    agg_result = df.groupby('department').agg({
        'salary': ['mean', 'median', 'std'],
        'bonus': 'sum',
        'rating': 'mean'
    }).round(0)
    print(agg_result)

    # Transform (return same shape as input)
    print("\n--- Transform (Z-score within department) ---")
    df['salary_zscore'] = df.groupby('department')['salary'].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    print(df[['department', 'salary', 'salary_zscore']].head(10).round(2))

    # Filter groups
    print("\n--- Filter Groups (departments with > 5 employees) ---")
    filtered = df.groupby('department').filter(lambda x: len(x) > 5)
    print(f"Departments remaining: {filtered['department'].unique()}")
    print(f"Employees remaining: {len(filtered)}")


# =============================================================================
# Part 7: Merging and Joining
# =============================================================================

def demo_merging():
    """Demonstrate merging and joining DataFrames."""
    print("\n" + "="*60)
    print("Part 7: Merging and Joining")
    print("="*60)

    # Create sample DataFrames
    employees = pd.DataFrame({
        'emp_id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'dept_id': [101, 102, 101, 103, 102]
    })

    departments = pd.DataFrame({
        'dept_id': [101, 102, 104],
        'dept_name': ['Engineering', 'Sales', 'Marketing']
    })

    salaries = pd.DataFrame({
        'emp_id': [1, 2, 3, 4, 6],
        'salary': [50000, 60000, 70000, 55000, 80000]
    })

    print("Employees:")
    print(employees)
    print("\nDepartments:")
    print(departments)
    print("\nSalaries:")
    print(salaries)

    # Inner join
    print("\n--- Inner Join ---")
    inner = pd.merge(employees, departments, on='dept_id')
    print(inner)

    # Left join
    print("\n--- Left Join ---")
    left = pd.merge(employees, departments, on='dept_id', how='left')
    print(left)

    # Right join
    print("\n--- Right Join ---")
    right = pd.merge(employees, departments, on='dept_id', how='right')
    print(right)

    # Outer join
    print("\n--- Outer Join ---")
    outer = pd.merge(employees, departments, on='dept_id', how='outer')
    print(outer)

    # Multiple merges
    print("\n--- Chained Merges ---")
    full_data = (employees
                 .merge(departments, on='dept_id', how='left')
                 .merge(salaries, on='emp_id', how='left'))
    print(full_data)

    # Concat (stacking DataFrames)
    print("\n--- Concat (Vertical Stack) ---")
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
    stacked = pd.concat([df1, df2], ignore_index=True)
    print(stacked)


# =============================================================================
# Part 8: Pivot Tables and Reshaping
# =============================================================================

def demo_pivot_and_reshape():
    """Demonstrate pivot tables and data reshaping."""
    print("\n" + "="*60)
    print("Part 8: Pivot Tables and Reshaping")
    print("="*60)

    # Create sales data
    np.random.seed(42)
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=12, freq='M'),
        'region': ['North', 'South'] * 6,
        'product': ['A', 'B', 'A', 'B'] * 3,
        'sales': np.random.randint(100, 500, 12),
        'quantity': np.random.randint(10, 50, 12)
    })

    print("Sales data:")
    print(df)

    # Pivot table
    print("\n--- Pivot Table ---")
    pivot = df.pivot_table(
        values='sales',
        index='region',
        columns='product',
        aggfunc='sum'
    )
    print("Sales by region and product:")
    print(pivot)

    # More complex pivot
    print("\n--- Multiple Aggregations ---")
    pivot2 = df.pivot_table(
        values=['sales', 'quantity'],
        index='region',
        columns='product',
        aggfunc={'sales': 'sum', 'quantity': 'mean'}
    )
    print(pivot2.round(1))

    # Melt (unpivot)
    print("\n--- Melt (Unpivot) ---")
    wide_df = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'math_score': [90, 85],
        'english_score': [88, 92],
        'science_score': [95, 88]
    })
    print("Wide format:")
    print(wide_df)

    melted = pd.melt(wide_df, id_vars=['name'],
                     value_vars=['math_score', 'english_score', 'science_score'],
                     var_name='subject', value_name='score')
    print("\nLong format (melted):")
    print(melted)


# =============================================================================
# Part 9: Time Series Operations
# =============================================================================

def demo_time_series():
    """Demonstrate time series operations."""
    print("\n" + "="*60)
    print("Part 9: Time Series Operations")
    print("="*60)

    # Create time series data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=365, freq='D')
    df = pd.DataFrame({
        'date': dates,
        'value': np.cumsum(np.random.randn(365)) + 100,
        'category': np.random.choice(['A', 'B'], 365)
    })
    df = df.set_index('date')

    print("Time series data (first 10 rows):")
    print(df.head(10))

    # Date/time components
    print("\n--- Date Components ---")
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['day_of_week'] = df.index.dayofweek
    df['is_weekend'] = df.index.dayofweek >= 5
    print(df[['value', 'year', 'month', 'day_of_week', 'is_weekend']].head())

    # Resampling
    print("\n--- Resampling (Weekly Mean) ---")
    weekly = df['value'].resample('W').mean()
    print(weekly.head(10).round(2))

    print("\n--- Resampling (Monthly Stats) ---")
    monthly = df['value'].resample('M').agg(['mean', 'min', 'max'])
    print(monthly.head().round(2))

    # Rolling windows
    print("\n--- Rolling Window (7-day moving average) ---")
    df['rolling_mean'] = df['value'].rolling(window=7).mean()
    df['rolling_std'] = df['value'].rolling(window=7).std()
    print(df[['value', 'rolling_mean', 'rolling_std']].head(15).round(2))

    # Shift (lag features)
    print("\n--- Lag Features ---")
    df['value_lag1'] = df['value'].shift(1)
    df['value_lag7'] = df['value'].shift(7)
    df['value_diff'] = df['value'].diff()
    print(df[['value', 'value_lag1', 'value_lag7', 'value_diff']].head(10).round(2))


# =============================================================================
# Part 10: ML Preprocessing Pipeline
# =============================================================================

def demo_ml_preprocessing():
    """Demonstrate a complete ML preprocessing pipeline."""
    print("\n" + "="*60)
    print("Part 10: ML Preprocessing Pipeline")
    print("="*60)

    # Create a realistic dataset
    np.random.seed(42)
    n = 1000

    df = pd.DataFrame({
        'age': np.random.normal(35, 10, n).clip(18, 70),
        'income': np.random.lognormal(10.5, 0.5, n),
        'credit_score': np.random.normal(650, 100, n).clip(300, 850),
        'num_accounts': np.random.poisson(3, n),
        'employment_type': np.random.choice(['Full-time', 'Part-time', 'Self-employed', 'Unemployed'], n),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n),
        'default': np.random.choice([0, 1], n, p=[0.8, 0.2])
    })

    # Add some missing values
    df.loc[np.random.choice(df.index, 50), 'income'] = np.nan
    df.loc[np.random.choice(df.index, 30), 'credit_score'] = np.nan

    print("Raw data info:")
    print(f"Shape: {df.shape}")
    print(f"\nMissing values:\n{df.isnull().sum()}")
    print(f"\nData types:\n{df.dtypes}")

    # Step 1: Handle missing values
    print("\n--- Step 1: Handle Missing Values ---")
    df['income'] = df['income'].fillna(df['income'].median())
    df['credit_score'] = df['credit_score'].fillna(df['credit_score'].median())
    print(f"Missing values after: {df.isnull().sum().sum()}")

    # Step 2: Feature engineering
    print("\n--- Step 2: Feature Engineering ---")
    df['income_per_account'] = df['income'] / (df['num_accounts'] + 1)
    df['credit_age_ratio'] = df['credit_score'] / df['age']
    df['is_employed'] = df['employment_type'] != 'Unemployed'
    print("New features created: income_per_account, credit_age_ratio, is_employed")

    # Step 3: Encode categorical variables
    print("\n--- Step 3: Encode Categorical Variables ---")
    df_encoded = pd.get_dummies(df, columns=['employment_type', 'education'], drop_first=True)
    print(f"Shape after encoding: {df_encoded.shape}")
    print(f"New columns: {[c for c in df_encoded.columns if '_' in c and c not in df.columns][:5]}...")

    # Step 4: Scale numerical features
    print("\n--- Step 4: Scale Numerical Features ---")
    numerical_cols = ['age', 'income', 'credit_score', 'num_accounts',
                      'income_per_account', 'credit_age_ratio']

    for col in numerical_cols:
        mean = df_encoded[col].mean()
        std = df_encoded[col].std()
        df_encoded[f'{col}_scaled'] = (df_encoded[col] - mean) / std

    print("Scaled feature stats:")
    scaled_cols = [c for c in df_encoded.columns if '_scaled' in c]
    print(df_encoded[scaled_cols].describe().round(2))

    # Step 5: Split features and target
    print("\n--- Step 5: Prepare Train/Test Split ---")
    feature_cols = [c for c in df_encoded.columns
                    if c != 'default' and c not in numerical_cols]  # Use scaled versions
    X = df_encoded[feature_cols]
    y = df_encoded['default']

    # Simple train/test split (80/20)
    train_size = int(0.8 * len(df_encoded))
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    print(f"Training set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
    print(f"Target distribution (train): {y_train.value_counts().to_dict()}")

    print("\n✅ Data ready for ML!")


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Module 25: pandas Essentials")
    print("Data Manipulation for Machine Learning")
    print("="*60)

    # Run all demonstrations
    df = demo_creating_dataframes()
    df_explore = demo_exploring_data()
    demo_selecting_data(df_explore)
    demo_data_cleaning()
    demo_transformations()
    demo_groupby()
    demo_merging()
    demo_pivot_and_reshape()
    demo_time_series()
    demo_ml_preprocessing()

    print("\n" + "="*60)
    print("pandas Essentials Complete!")
    print("="*60)
    print("""
Key Takeaways:
1. DataFrames are your primary data structure for ML
2. .loc for labels, .iloc for integers, boolean for filters
3. Handle missing data before training models
4. Groupby enables powerful aggregations
5. One-hot encode categorical variables for ML

Next: example_03_visualization.py
    """)
