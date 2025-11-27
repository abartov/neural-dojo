# Module 25: Python for Machine Learning
# Or: NumPy, Pandas, and Everything You Need to Crunch Numbers

**Last Updated**: 2025-11-26
**Status**: Complete
**Reading Time**: 5-6 hours
**Phase**: 6 - Deep Learning Foundations

---

## Learning Objectives

By the end of this module, you will:
- Master NumPy for high-performance numerical computing
- Manipulate data fluently with pandas DataFrames
- Create publication-quality visualizations with matplotlib and seaborn
- Understand WHY these tools are essential for machine learning
- Build a reusable ML data toolkit

---

## Introduction: The Scientific Python Ecosystem

You've spent 24 modules building AI applications using APIs, frameworks, and high-level tools. Now we're going deeper. **Phase 6** is about understanding how neural networks actually work—not just using them, but building them from scratch.

But before we can build neural networks, we need the right tools. Imagine trying to build a house with your bare hands versus having power tools. NumPy, pandas, and matplotlib are your power tools for machine learning.

### Why Python Dominates ML/AI

In 2024, Python handles:
- **92%** of machine learning projects
- **85%** of data science workflows
- **100%** of the top deep learning frameworks (PyTorch, TensorFlow, JAX)

But Python is slow! A naive Python loop is 10-100x slower than C. So how does it dominate computationally intensive ML?

**The answer**: Python is the glue, not the engine.

```
┌─────────────────────────────────────────────────┐
│                 Python Code                      │
│   (Easy to write, flexible, readable)           │
└──────────────────────┬──────────────────────────┘
                       │ calls
                       ▼
┌─────────────────────────────────────────────────┐
│    NumPy / BLAS / LAPACK / cuDNN / MKL         │
│   (Optimized C/Fortran/CUDA, blazing fast)     │
└─────────────────────────────────────────────────┘
```

You write simple Python. Behind the scenes, highly optimized native code does the heavy lifting. This is the genius of the Scientific Python ecosystem.

---

## Did You Know? The Origins of Scientific Python

### The Birth of NumPy: A Tale of Two Libraries

In the early 2000s, Python had a problem: TWO competing array libraries.

**Numeric** (1995): Created by Jim Hugunin at MIT. Fast but limited.

**Numarray** (2001): Created by Space Telescope Science Institute. More features but slower.

The community was split. Code written for one library wouldn't work with the other. It was chaos.

Enter **Travis Oliphant**, a grad student at the Mayo Clinic who needed both libraries' features. In 2005, he did something audacious: he merged them into **NumPy**.

> "I had about 3 months of time between finishing my PhD and starting my new job. I thought, 'How hard can it be?'" — Travis Oliphant

It took him those 3 months, working 80-hour weeks, rewriting both libraries into one cohesive package. NumPy 1.0 was released in 2006.

**The impact**: NumPy became the foundation for all of scientific Python. pandas, scikit-learn, TensorFlow, PyTorch—all built on NumPy arrays.

### The pandas Story: Wall Street Meets Open Source

In 2008, **Wes McKinney** was working at AQR Capital Management, a hedge fund. He was frustrated with the clunky tools for analyzing financial data.

> "I remember thinking, 'I cannot believe I have to suffer through this horrible, horrible R interface.'" — Wes McKinney

He started building a library for himself. It was so useful that AQR let him open-source it in 2009. He named it **pandas** (Panel Data System).

By 2012, pandas had revolutionized data analysis in Python. Wes left finance to work on pandas full-time, funded by various companies who depended on it.

**Fun fact**: AQR initially resisted open-sourcing pandas, fearing it would help competitors. Wes convinced them that the community contributions would far outweigh any competitive advantage they might lose. He was right—pandas now has over 2,000 contributors.

### matplotlib: The Scientist Who Needed Better Graphs

In 2002, **John Hunter** was a neurobiologist doing EEG analysis. He needed to visualize brain signals but found existing tools inadequate.

> "I was frustrated with the limited plotting capabilities of the tools available at the time and decided to write my own." — John Hunter

He created matplotlib to mimic MATLAB's plotting (hence the name). It became the standard plotting library in Python.

Tragically, John Hunter passed away in 2012 from cancer. The matplotlib project continues in his memory, maintained by a global community.

**His legacy**: Every plot in nearly every Jupyter notebook, every figure in thousands of scientific papers, traces back to his work.

---

## 🔢 NumPy: The Foundation of Numerical Python

### What is NumPy?

NumPy (Numerical Python) provides:
1. **ndarray**: A powerful N-dimensional array object
2. **Broadcasting**: Smart element-wise operations
3. **Linear algebra**: Matrix operations, decompositions
4. **Random numbers**: Statistical distributions
5. **C/Fortran integration**: For custom high-performance code

### Why Arrays, Not Lists?

Python lists are flexible but slow:

```python
# Python list: Each element is a full Python object
python_list = [1, 2, 3, 4, 5]
# Stored as: [ptr] → [PyObject: type, refcount, value]
#            [ptr] → [PyObject: type, refcount, value]
#            ...

# NumPy array: Contiguous block of raw memory
numpy_array = np.array([1, 2, 3, 4, 5])
# Stored as: [1][2][3][4][5] (just the numbers, packed tight)
```

**Memory comparison**:
- Python list of 1 million integers: ~28 MB
- NumPy array of 1 million integers: ~4 MB (7x smaller!)

**Speed comparison**:
```python
# Adding two lists element-wise
python_result = [a + b for a, b in zip(list1, list2)]  # ~500ms

# Adding two NumPy arrays
numpy_result = arr1 + arr2  # ~2ms (250x faster!)
```

### Core NumPy Concepts

#### 1. Creating Arrays

```python
import numpy as np

# From Python lists
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2, 3], [4, 5, 6]])

# Common initializations
zeros = np.zeros((3, 4))        # 3x4 array of zeros
ones = np.ones((2, 3))          # 2x3 array of ones
empty = np.empty((2, 2))        # Uninitialized (faster)
identity = np.eye(4)            # 4x4 identity matrix
range_arr = np.arange(0, 10, 2) # [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5) # [0, 0.25, 0.5, 0.75, 1]

# Random arrays
random_uniform = np.random.rand(3, 3)     # Uniform [0, 1)
random_normal = np.random.randn(3, 3)     # Standard normal
random_int = np.random.randint(0, 10, (3, 3))  # Random integers
```

#### 2. Array Attributes

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

arr.shape      # (2, 3) - 2 rows, 3 columns
arr.ndim       # 2 - number of dimensions
arr.size       # 6 - total number of elements
arr.dtype      # dtype('int64') - data type
arr.itemsize   # 8 - bytes per element
arr.nbytes     # 48 - total bytes (6 * 8)
```

#### 3. Reshaping and Manipulating

```python
arr = np.arange(12)  # [0, 1, 2, ..., 11]

# Reshape
reshaped = arr.reshape(3, 4)   # 3x4 matrix
reshaped = arr.reshape(2, -1)  # 2 rows, auto-calculate columns

# Flatten
flat = reshaped.flatten()      # Returns copy
raveled = reshaped.ravel()     # Returns view (faster)

# Transpose
transposed = reshaped.T        # Swap rows and columns

# Stacking
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.vstack([a, b])  # [[1,2,3], [4,5,6]]
np.hstack([a, b])  # [1, 2, 3, 4, 5, 6]
np.column_stack([a, b])  # [[1,4], [2,5], [3,6]]
```

#### 4. Indexing and Slicing

```python
arr = np.array([[1, 2, 3, 4],
                [5, 6, 7, 8],
                [9, 10, 11, 12]])

# Basic indexing
arr[0, 0]      # 1 (first element)
arr[1, 2]      # 7 (row 1, col 2)
arr[-1, -1]    # 12 (last element)

# Slicing (start:stop:step)
arr[0, :]      # [1, 2, 3, 4] (first row)
arr[:, 0]      # [1, 5, 9] (first column)
arr[0:2, 1:3]  # [[2,3], [6,7]] (submatrix)
arr[::2, :]    # Every other row

# Boolean indexing (POWERFUL!)
arr[arr > 5]   # [6, 7, 8, 9, 10, 11, 12]
arr[arr % 2 == 0]  # Even numbers

# Fancy indexing
arr[[0, 2], :]  # Rows 0 and 2
arr[:, [0, 3]]  # Columns 0 and 3
```

#### 5. Broadcasting

Broadcasting is NumPy's superpower—it lets arrays of different shapes work together:

```python
# Scalar broadcast
arr = np.array([1, 2, 3])
arr + 10  # [11, 12, 13] - 10 "broadcasts" to match arr

# 1D to 2D broadcast
matrix = np.array([[1, 2, 3],
                   [4, 5, 6]])
row = np.array([10, 20, 30])
matrix + row  # [[11,22,33], [14,25,36]]

# Column broadcast
col = np.array([[100], [200]])
matrix + col  # [[101,102,103], [204,205,206]]
```

**Broadcasting rules**:
1. Arrays with fewer dimensions are padded with 1s on the left
2. Arrays with size 1 along a dimension act as if copied along that dimension
3. Arrays must have compatible shapes after these rules

```
Shape (3, 4) + Shape (4,)   → Works! (4,) becomes (1, 4), broadcasts to (3, 4)
Shape (3, 4) + Shape (3,)   → Error! Can't broadcast (3,) to (3, 4)
Shape (3, 4) + Shape (3, 1) → Works! (3, 1) broadcasts to (3, 4)
```

#### 6. Vectorized Operations

NumPy's real power: operations on entire arrays at once.

```python
# Universal functions (ufuncs) - operate element-wise
np.sqrt(arr)        # Square root of each element
np.exp(arr)         # e^x for each element
np.log(arr)         # Natural log
np.sin(arr)         # Sine
np.abs(arr)         # Absolute value

# Aggregations
arr.sum()           # Sum all elements
arr.mean()          # Average
arr.std()           # Standard deviation
arr.min(), arr.max()  # Min and max
arr.argmin(), arr.argmax()  # Index of min/max

# Along axes
matrix.sum(axis=0)  # Sum each column
matrix.sum(axis=1)  # Sum each row
matrix.mean(axis=0) # Mean of each column
```

#### 7. Linear Algebra

This is where ML really lives:

```python
# Matrix multiplication
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

A @ B              # Matrix multiplication (Python 3.5+)
np.dot(A, B)       # Same thing
np.matmul(A, B)    # Same thing

# Other operations
np.linalg.inv(A)   # Matrix inverse
np.linalg.det(A)   # Determinant
np.linalg.eig(A)   # Eigenvalues and eigenvectors
np.linalg.svd(A)   # Singular Value Decomposition
np.linalg.norm(A)  # Matrix/vector norm

# Solving linear systems: Ax = b
b = np.array([1, 2])
x = np.linalg.solve(A, b)

# QR decomposition (used in many ML algorithms)
Q, R = np.linalg.qr(A)
```

### Did You Know? NumPy's Secret Weapons

**BLAS and LAPACK**: NumPy's linear algebra is backed by BLAS (Basic Linear Algebra Subprograms) and LAPACK, libraries originally written in Fortran in the 1970s. These are so optimized that modern Python code using NumPy can be as fast as C code.

**Intel MKL**: If you install NumPy through Anaconda, you get Intel's Math Kernel Library (MKL), which uses specialized CPU instructions (AVX, AVX-512) for even faster matrix operations. A matrix multiplication can be 10x faster with MKL!

**Memory views**: When you slice a NumPy array, you don't copy data—you create a "view" that shares memory with the original. This is why NumPy is so memory-efficient, but also why modifying a slice modifies the original!

```python
arr = np.array([1, 2, 3, 4, 5])
view = arr[1:4]
view[0] = 100
print(arr)  # [1, 100, 3, 4, 5] - Original changed!

# To avoid this, explicitly copy:
copy = arr[1:4].copy()
```

---

## 🐼 pandas: Data Manipulation Made Easy

### What is pandas?

pandas provides:
1. **DataFrame**: 2D labeled data structure (like a spreadsheet)
2. **Series**: 1D labeled array (like a column)
3. **Data I/O**: Read/write CSV, Excel, SQL, JSON, Parquet
4. **Data cleaning**: Handle missing data, duplicates, transformations
5. **Grouping and aggregation**: SQL-like operations
6. **Time series**: Date/time handling, resampling

### Why pandas for ML?

Before you train a model, you spend 80% of your time:
- Loading and exploring data
- Cleaning and preprocessing
- Feature engineering
- Splitting and validating

pandas makes all of this 10x easier.

### Core pandas Concepts

#### 1. Series and DataFrames

```python
import pandas as pd

# Series: 1D labeled array
s = pd.Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])
s['a']      # 1
s[['a', 'c']]  # Series with a and c

# DataFrame: 2D labeled data structure
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
})

#      name  age  salary
# 0   Alice   25   50000
# 1     Bob   30   60000
# 2 Charlie   35   70000
```

#### 2. Reading and Writing Data

```python
# CSV
df = pd.read_csv('data.csv')
df.to_csv('output.csv', index=False)

# Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
df.to_excel('output.xlsx', index=False)

# JSON
df = pd.read_json('data.json')
df.to_json('output.json', orient='records')

# SQL
import sqlite3
conn = sqlite3.connect('database.db')
df = pd.read_sql('SELECT * FROM users', conn)
df.to_sql('users', conn, if_exists='replace', index=False)

# Parquet (efficient columnar format)
df = pd.read_parquet('data.parquet')
df.to_parquet('output.parquet')
```

#### 3. Exploring Data

```python
# Quick overview
df.head()          # First 5 rows
df.tail()          # Last 5 rows
df.shape           # (rows, columns)
df.info()          # Column types, non-null counts
df.describe()      # Statistical summary

# Column information
df.columns         # Column names
df.dtypes          # Data types
df['age'].unique() # Unique values
df['age'].nunique()  # Number of unique values
df['age'].value_counts()  # Frequency of each value

# Memory usage
df.memory_usage(deep=True)
```

#### 4. Selecting Data

```python
# Column selection
df['name']              # Single column (Series)
df[['name', 'age']]     # Multiple columns (DataFrame)

# Row selection with .loc (label-based)
df.loc[0]               # Row with index 0
df.loc[0:2]             # Rows 0 through 2 (inclusive!)
df.loc[0, 'name']       # Specific cell
df.loc[:, 'name':'salary']  # All rows, columns name to salary

# Row selection with .iloc (integer-based)
df.iloc[0]              # First row
df.iloc[0:2]            # First two rows (exclusive!)
df.iloc[0, 0]           # First cell
df.iloc[:, 0:2]         # All rows, first two columns

# Boolean selection
df[df['age'] > 25]                    # Rows where age > 25
df[(df['age'] > 25) & (df['salary'] > 55000)]  # Multiple conditions
df.query('age > 25 and salary > 55000')  # Same thing, cleaner
```

#### 5. Data Cleaning

```python
# Missing data
df.isna()              # Boolean mask of missing values
df.isna().sum()        # Count missing per column
df.dropna()            # Drop rows with any missing
df.dropna(subset=['age'])  # Drop rows missing age
df.fillna(0)           # Fill missing with 0
df.fillna(df.mean())   # Fill with column means
df.fillna(method='ffill')  # Forward fill

# Duplicates
df.duplicated()        # Boolean mask
df.drop_duplicates()   # Remove duplicates
df.drop_duplicates(subset=['name'])  # By specific columns

# Data types
df['age'] = df['age'].astype(int)
df['date'] = pd.to_datetime(df['date'])
df['category'] = df['category'].astype('category')

# String operations
df['name'].str.lower()
df['name'].str.strip()
df['name'].str.contains('A')
df['name'].str.replace('Alice', 'Alicia')
```

#### 6. Transforming Data

```python
# Apply functions
df['age_squared'] = df['age'] ** 2
df['age_category'] = df['age'].apply(lambda x: 'young' if x < 30 else 'old')
df['full_info'] = df.apply(lambda row: f"{row['name']}: {row['age']}", axis=1)

# Map values
df['grade'] = df['score'].map({90: 'A', 80: 'B', 70: 'C'})

# Binning
df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 100], labels=['young', 'mid', 'senior'])

# One-hot encoding
pd.get_dummies(df, columns=['category'])

# Renaming
df.rename(columns={'name': 'full_name'})
df.columns = ['Name', 'Age', 'Salary']  # Rename all
```

#### 7. Grouping and Aggregation

```python
# Group by single column
df.groupby('department')['salary'].mean()
df.groupby('department')['salary'].agg(['mean', 'min', 'max'])

# Group by multiple columns
df.groupby(['department', 'level'])['salary'].mean()

# Multiple aggregations
df.groupby('department').agg({
    'salary': ['mean', 'median'],
    'age': 'mean',
    'name': 'count'
})

# Transform (return same shape)
df['salary_zscore'] = df.groupby('department')['salary'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Filter groups
df.groupby('department').filter(lambda x: len(x) > 5)
```

#### 8. Merging and Joining

```python
# Merge (SQL-like joins)
merged = pd.merge(df1, df2, on='id')  # Inner join
merged = pd.merge(df1, df2, on='id', how='left')   # Left join
merged = pd.merge(df1, df2, on='id', how='outer')  # Outer join
merged = pd.merge(df1, df2, left_on='user_id', right_on='id')  # Different names

# Concat (stack DataFrames)
combined = pd.concat([df1, df2])  # Vertically
combined = pd.concat([df1, df2], axis=1)  # Horizontally

# Join (on index)
df1.join(df2, how='left')
```

#### 9. Pivot Tables and Reshaping

```python
# Pivot table
pivot = df.pivot_table(
    values='sales',
    index='region',
    columns='product',
    aggfunc='sum'
)

# Melt (unpivot)
melted = pd.melt(df, id_vars=['date'], value_vars=['product_a', 'product_b'])

# Stack/unstack
stacked = df.stack()
unstacked = df.unstack()
```

### Did You Know? pandas Performance Secrets

**The chained indexing trap**:
```python
# BAD - Creates copy, may not modify original
df[df['age'] > 25]['salary'] = 100000  # SettingWithCopyWarning!

# GOOD - Use .loc for assignment
df.loc[df['age'] > 25, 'salary'] = 100000
```

**Categorical data**: If you have a column with repeated string values, convert to category:
```python
df['status'] = df['status'].astype('category')
# Memory: 1M strings "active"/"inactive" = 50MB → 2MB (25x smaller!)
```

**Arrow and pandas 2.0**: pandas 2.0 (2023) can use Apache Arrow as the backend instead of NumPy. Arrow is faster for string operations and uses less memory:
```python
df = pd.read_csv('data.csv', dtype_backend='pyarrow')
```

---

## Visualization: matplotlib and seaborn

### matplotlib: The Grandfather of Python Plotting

matplotlib gives you complete control over every aspect of a plot. It's verbose but powerful.

#### Basic Plotting

```python
import matplotlib.pyplot as plt
import numpy as np

# Line plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y, label='sin(x)', color='blue', linewidth=2)
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.title('Sine Wave')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('sine.png', dpi=150)
plt.show()
```

#### The Object-Oriented Interface

For complex plots, use the OO interface:

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Top-left: Line plot
axes[0, 0].plot(x, np.sin(x), 'b-', label='sin')
axes[0, 0].plot(x, np.cos(x), 'r--', label='cos')
axes[0, 0].legend()
axes[0, 0].set_title('Trigonometric Functions')

# Top-right: Scatter plot
axes[0, 1].scatter(np.random.rand(50), np.random.rand(50),
                   c=np.random.rand(50), s=np.random.rand(50)*500,
                   alpha=0.6, cmap='viridis')
axes[0, 1].set_title('Scatter Plot')

# Bottom-left: Bar plot
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 78]
axes[1, 0].bar(categories, values, color='steelblue')
axes[1, 0].set_title('Bar Chart')

# Bottom-right: Histogram
data = np.random.randn(1000)
axes[1, 1].hist(data, bins=30, edgecolor='black', alpha=0.7)
axes[1, 1].set_title('Histogram')

plt.tight_layout()
plt.savefig('subplots.png', dpi=150)
plt.show()
```

#### Common Plot Types

```python
# Scatter plot
plt.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')

# Bar plot
plt.bar(categories, values)
plt.barh(categories, values)  # Horizontal

# Histogram
plt.hist(data, bins=30, density=True)  # density=True normalizes

# Box plot
plt.boxplot([data1, data2, data3], labels=['A', 'B', 'C'])

# Pie chart (use sparingly!)
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)

# Heatmap
plt.imshow(matrix, cmap='hot', aspect='auto')
plt.colorbar()

# Contour plot
plt.contour(X, Y, Z, levels=20)
plt.contourf(X, Y, Z, levels=20, cmap='viridis')  # Filled
```

### seaborn: Statistical Visualization

seaborn builds on matplotlib with:
- Beautiful default styles
- Statistical visualization functions
- Integration with pandas DataFrames
- Color palettes designed for data

```python
import seaborn as sns

# Set style
sns.set_theme(style='whitegrid')

# Distribution plots
sns.histplot(df['age'], kde=True)           # Histogram with KDE
sns.kdeplot(df['age'])                       # Just KDE
sns.boxplot(x='department', y='salary', data=df)
sns.violinplot(x='department', y='salary', data=df)

# Relationship plots
sns.scatterplot(x='age', y='salary', hue='department', data=df)
sns.lineplot(x='date', y='value', hue='category', data=df)
sns.regplot(x='age', y='salary', data=df)   # With regression line

# Categorical plots
sns.countplot(x='department', data=df)
sns.barplot(x='department', y='salary', data=df)  # With error bars
sns.catplot(x='department', y='salary', kind='violin', data=df)

# Matrix plots
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
sns.clustermap(data_matrix)  # Hierarchical clustering

# Pair plots (for exploring relationships)
sns.pairplot(df[['age', 'salary', 'experience']], hue='department')

# Joint plots (2D + marginal distributions)
sns.jointplot(x='age', y='salary', data=df, kind='hex')
```

### Visualization Best Practices for ML

#### 1. Exploring Your Data

```python
# Quick overview of distributions
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
for idx, col in enumerate(df.select_dtypes(include=[np.number]).columns):
    ax = axes[idx // 3, idx % 3]
    df[col].hist(ax=ax, bins=30)
    ax.set_title(col)
plt.tight_layout()
```

#### 2. Correlation Analysis

```python
# Correlation heatmap
corr = df.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=0.5)
plt.title('Feature Correlations')
```

#### 3. Target Distribution

```python
# For classification
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
df['target'].value_counts().plot(kind='bar', ax=axes[0])
axes[0].set_title('Target Distribution')
df['target'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=axes[1])
```

#### 4. Feature-Target Relationships

```python
# Numerical feature vs target
fig, axes = plt.subplots(1, len(numerical_cols), figsize=(15, 5))
for idx, col in enumerate(numerical_cols):
    sns.boxplot(x='target', y=col, data=df, ax=axes[idx])
    axes[idx].set_title(f'{col} by Target')
```

### Did You Know? The Art of Data Visualization

**Edward Tufte's principles** (the godfather of data viz):
1. **Data-ink ratio**: Maximize data, minimize chart junk
2. **Small multiples**: Same plot repeated for different subsets
3. **Integrity**: Don't mislead with scales or cherry-picking

**Color blindness**: ~8% of men are colorblind. Use:
- `cmap='viridis'` (perceptually uniform, colorblind-friendly)
- `cmap='cividis'` (optimized for colorblindness)
- Or use different line styles/markers

**The pie chart problem**: Humans are bad at comparing angles. Use bar charts instead:
```python
# BAD
plt.pie(values, labels=labels)

# GOOD
plt.barh(labels, values)
```

---

## 🔗 Putting It All Together: The ML Data Pipeline

Here's how these tools work together in a real ML workflow:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Load data
df = pd.read_csv('dataset.csv')

# 2. Explore
print(df.info())
print(df.describe())
print(df.isnull().sum())

# 3. Visualize
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
sns.histplot(df['target'], ax=axes[0, 0])
sns.heatmap(df.corr(), ax=axes[0, 1], cmap='coolwarm')
sns.boxplot(x='category', y='feature', data=df, ax=axes[1, 0])
sns.scatterplot(x='feature1', y='feature2', hue='target', data=df, ax=axes[1, 1])
plt.tight_layout()

# 4. Clean
df = df.dropna(subset=['important_column'])
df = df.fillna(df.median())
df = df.drop_duplicates()

# 5. Transform
df['log_feature'] = np.log1p(df['skewed_feature'])
df = pd.get_dummies(df, columns=['category'])

# 6. Split
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 7. Scale (using NumPy-backed transformations)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Now ready for ML!
```

---

## Practical Exercises

### Exercise 1: NumPy Fundamentals

Create a 10x10 matrix of random integers (0-100) and:
1. Find the mean of each row and column
2. Replace all values > 50 with 50
3. Find the indices of the 5 largest values
4. Multiply the matrix by its transpose
5. Calculate the determinant

### Exercise 2: pandas Data Analysis

Load a real dataset (e.g., Titanic, tips, iris) and:
1. Show basic statistics for numerical columns
2. Find and handle missing values
3. Group by a categorical variable and compute aggregations
4. Create 3 new features through transformations
5. Identify the most correlated features

### Exercise 3: Visualization Challenge

Create a dashboard with 6 plots showing:
1. Distribution of the target variable
2. Correlation heatmap
3. Box plots of numerical features by target
4. Scatter plot of two most correlated features
5. Time series (if applicable) or bar chart
6. Pair plot of top 4 features

---

## Deliverables

For this module, you will build:

### 1. NumPy Performance Benchmark
- Compare NumPy vs Python loops for common operations
- Measure impact of vectorization
- Document speedup factors

### 2. Data Analysis Pipeline
- Load, clean, and transform a dataset
- Feature engineering examples
- Export processed data

### 3. ML Data Toolkit (Main Deliverable)
- Reusable functions for:
  - Data loading and exploration
  - Cleaning and preprocessing
  - Feature engineering
  - Train/test splitting
  - Visualization generation
- CLI interface for quick analysis
- JSON configuration support

---

## Further Reading

### NumPy
- [NumPy User Guide](https://numpy.org/doc/stable/user/index.html)
- [From Python to NumPy](https://www.labri.fr/perso/nrougier/from-python-to-numpy/) - Free book by Nicolas Rougier
- [100 NumPy Exercises](https://github.com/rougier/numpy-100)

### pandas
- [pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [Python for Data Analysis](https://wesmckinney.com/book/) - Free book by Wes McKinney
- [Modern Pandas](https://tomaugspurger.github.io/posts/modern-1-intro/) - Best practices

### Visualization
- [matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- [seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [The Visual Display of Quantitative Information](https://www.edwardtufte.com/tufte/books_vdqi) - Tufte's classic

### Scientific Python
- [Scientific Python Lectures](https://lectures.scientific-python.org/)
- [SciPy Cookbook](https://scipy-cookbook.readthedocs.io/)

---

## Did You Know? Fun Facts

### The Billion-Dollar Bug
In 2012, Knight Capital lost $440 million in 45 minutes due to a trading algorithm bug. Post-mortem analysis was done entirely in pandas. The ability to quickly analyze millions of trades led to regulatory changes requiring better data analysis practices.

### NumPy in Space
NASA's James Webb Space Telescope image processing pipeline uses NumPy. The famous first images required processing petabytes of data through NumPy arrays. When you see those stunning space images, you're seeing NumPy at work.

### pandas Named After Econometrics
Despite what you might think, "pandas" isn't named after the animal. It comes from "Panel Data" - a term from econometrics for multi-dimensional data structures. Wes McKinney was an economist before a programmer!

### matplotlib's Easter Eggs
matplotlib has hidden XKCD-style plotting:
```python
with plt.xkcd():
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title('Much professional, very science')
```

### The Hadley Wickham Effect
Hadley Wickham created R's ggplot2 and tidyverse. His influence on data science was so strong that Python libraries started copying his approach. seaborn's "grammar of graphics" is directly inspired by ggplot2.

---

## ️ Next Steps

With NumPy, pandas, and visualization mastered, you're ready for **Module 26: Neural Networks from Scratch**.

You'll use these exact tools to:
- Create weight matrices with NumPy
- Track training metrics in pandas
- Visualize the learning process with matplotlib

The foundation is laid. Now let's build neural networks!

---

_Module 25 Complete! You now have the tools for machine learning._

**🥋🧠⚡**
