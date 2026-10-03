import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual styling for charts
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.size': 11, 'figure.autolayout': True})


def calculate_grade(score: float) -> str:
    """Helper function to assign grades based on total score percentage."""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'


def process_dashboard_exporter(csv_path: str, output_folder: str):
    """
    Cleans student dataset, generates subject statistics, and exports data files + charts.

    Expected Time Complexity: O(n * s)
    Expected Space Complexity: O(n * s)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # 1. Load Data
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_path}' not found.", file=sys.stderr)
        return

    # Non-subject metadata columns
    meta_cols = ['enrollment', 'name']
    # Identify subject columns dynamically
    subject_cols = [col for col in df.columns if col.lower() not in meta_cols]

    # 2. Data Cleaning & Missing Value Imputation
    # Clean numeric types and coerce invalid entries/out-of-range marks (0 to 100)
    for col in subject_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Out-of-bounds numbers treated as missing values
        df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan
        # Impute missing values with subject median score
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

    # Calculate overall aggregates
    df['total_score'] = df[subject_cols].sum(axis=1)
    df['average_score'] = df[subject_cols].mean(axis=1)
    df['grade'] = df['average_score'].apply(calculate_grade)

    # Export Cleaned CSV
    cleaned_csv_path = os.path.join(output_folder, 'cleaned_marks.csv')
    df.to_csv(cleaned_csv_path, index=False)

    # 3. Compute Summary Statistics per Subject
    summary_data = []
    for col in subject_cols:
        summary_data.append({
            'Subject': col,
            'Mean': round(df[col].mean(), 2),
            'Median': round(df[col].median(), 2),
            'Std_Dev': round(df[col].std(), 2),
            'Min': round(df[col].min(), 2),
            'Max': round(df[col].max(), 2),
            'Pass_Rate_%': round((df[col] >= 40).mean() * 100, 2)
        })

    summary_df = pd.DataFrame(summary_data)
    summary_csv_path = os.path.join(output_folder, 'summary.csv')
    summary_df.to_csv(summary_csv_path, index=False)

    # 4. Visualization 1: Grade Distribution (Bar Chart)
    plt.figure(figsize=(8, 5))
    grade_counts = df['grade'].value_counts().reindex(['A+', 'A', 'B', 'C', 'D', 'F'], fill_value=0)
    ax = sns.barplot(x=grade_counts.index, y=grade_counts.values, hue=grade_counts.index, legend=False, palette="viridis")
    plt.title("Overall Student Grade Distribution", fontsize=14, fontweight='bold')
    plt.xlabel("Grade Level")
    plt.ylabel("Number of Students")
    
    # Value annotations on top of bars
    for p in ax.patches:
        height = int(p.get_height())
        if height > 0:
            ax.annotate(f'{height}', (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=10, xytext=(0, 3),
                        textcoords='offset points')

    chart1_path = os.path.join(output_folder, 'grade_distribution.png')
    plt.savefig(chart1_path, dpi=300)
    plt.close()

    # 5. Visualization 2: Subject-Wise Average Comparison (Horizontal Bar Chart)
    plt.figure(figsize=(9, 5))
    avg_scores = summary_df.sort_values(by='Mean', ascending=True)
    ax = sns.barplot(x='Mean', y='Subject', data=avg_scores, hue='Subject', legend=False, palette="crest")
    plt.title("Subject-Wise Average Score Comparison", fontsize=14, fontweight='bold')
    plt.xlabel("Average Score (Out of 100)")
    plt.ylabel("Subject")
    plt.xlim(0, 100)

    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f'{width:.1f}', (width + 1, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', fontsize=10)

    chart2_path = os.path.join(output_folder, 'subject_average.png')
    plt.savefig(chart2_path, dpi=300)
    plt.close()

    # 6. Visualization 3: Top Performers Chart (Top 10 Students by Average Score)
    plt.figure(figsize=(10, 5))
    top_10 = df.nlargest(10, 'average_score').sort_values(by='average_score', ascending=True)
    ax = sns.barplot(x='average_score', y='name', data=top_10, hue='name', legend=False, palette="magma")
    plt.title("Top 10 Performers by Average Score", fontsize=14, fontweight='bold')
    plt.xlabel("Average Score")
    plt.ylabel("Student Name")

    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f'{width:.1f}', (width + 0.5, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', fontsize=10)

    chart3_path = os.path.join(output_folder, 'top_performers.png')
    plt.savefig(chart3_path, dpi=300)
    plt.close()

    print("Dashboard Export Completed Successfully!")
    print(f"1. Cleaned CSV:      {cleaned_csv_path}")
    print(f"2. Summary CSV:      {summary_csv_path}")
    print(f"3. Grade Dist Chart: {chart1_path}")
    print(f"4. Subject Avg Chart:{chart2_path}")
    print(f"5. Top Performers:   {chart3_path}")


if __name__ == "__main__":
    # Example Driver Execution
    input_csv = "marks.csv"
    output_dir = "dashboard_output"
    
    # Create a demo marks.csv if missing for testing purposes
    if not os.path.exists(input_csv):
        sample_df = pd.DataFrame({
            'enrollment': [101, 102, 103, 104, 105],
            'name': ['Asha', 'Dev', 'Rohan', 'Priya', 'Karan'],
            'Python': [95, 84, np.nan, 62, 45],
            'DBMS': [91, 78, 88, np.nan, 50],
            'OS': [92, 85, 76, 58, 40]
        })
        sample_df.to_csv(input_csv, index=False)

    process_dashboard_exporter(input_csv, output_dir)
