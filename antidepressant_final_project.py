import pandas as pd
from pathlib import Path

# Finds main project folder even if this script is inside final_project_data
PROJECT_ROOT = Path(__file__).resolve().parent.parent

final_dir = PROJECT_ROOT / "final_project_data"
final_dir.mkdir(exist_ok=True)

main_path = PROJECT_ROOT / "merged_project_data" / "antidepressant_job_market_merged.csv"
jobs_path = PROJECT_ROOT / "occupation_data" / "nontraditional_jobs_by_gender_year.csv"

print("Project root:", PROJECT_ROOT)
print("Main merged file:", main_path)
print("Occupation file:", jobs_path)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main merged file: {main_path}")

if not jobs_path.exists():
    raise FileNotFoundError(f"Missing occupation file: {jobs_path}")

main = pd.read_csv(main_path)
jobs = pd.read_csv(jobs_path)

# Make sure gender labels match
main["gender"] = main["gender"].str.strip()
jobs["gender"] = jobs["gender"].str.strip()

# Merge on match_year and gender
final = main.merge(
    jobs,
    left_on=["match_year", "gender"],
    right_on=["year", "gender"],
    how="left",
    suffixes=("", "_occupation")
)

# Keep clean columns
final = final[
    [
        "cycle",
        "match_year",
        "gender",
        "people_ages_20_35",
        "people_using_target_antidepressant",
        "percent_using_target_antidepressant",
        "approx_unemployment_rate_20_34",
        "total_workers",
        "nontraditional_workers",
        "percent_in_nontraditional_jobs"
    ]
]

# Save final dataset
final_path = final_dir / "final_antidepressant_job_occupation_dataset.csv"
final.to_csv(final_path, index=False)

print("Saved final dataset:")
print(final_path)

print("\nPreview:")
print(final.head(20))