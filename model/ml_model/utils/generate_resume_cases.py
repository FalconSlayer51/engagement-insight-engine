import pandas as pd
import numpy as np

def generate_resume_cases(num_cases=2000):
    # Create empty lists to store the data
    resume_uploaded = []
    batch_resume_uploaded_pct = []
    should_nudge_resume = []
    
    # Generate cases where should_nudge_resume = 1
    for _ in range(num_cases):
        # For should_nudge_resume = 1 cases:
        # Create more diverse patterns to improve precision and recall
        if np.random.random() < 0.7:  # 70% of cases follow the main pattern
            # Main pattern: resume_uploaded = 0, high batch percentage
            resume_uploaded.append(0)
            batch_resume_uploaded_pct.append(np.random.uniform(80, 95))
        else:  # 30% of cases follow alternative patterns
            if np.random.random() < 0.5:  # 15% of total cases
                # Pattern 1: Very high batch percentage (95-100%)
                resume_uploaded.append(0)
                batch_resume_uploaded_pct.append(np.random.uniform(95, 100))
            else:  # 15% of total cases
                # Pattern 2: Moderately high batch percentage (75-85%)
                resume_uploaded.append(0)
                batch_resume_uploaded_pct.append(np.random.uniform(75, 85))
        
        should_nudge_resume.append(1)
    
    # Create DataFrame
    df = pd.DataFrame({
        'resume_uploaded': resume_uploaded,
        'batch_resume_uploaded_pct': batch_resume_uploaded_pct,
        'should_nudge_resume': should_nudge_resume
    })
    
    return df

if __name__ == "__main__":
    # Generate 2000 new cases
    new_cases = generate_resume_cases(2000)
    
    # Read existing dataset
    existing_df = pd.read_csv('train_dataset/resume_dataset.csv')
    
    # Combine existing and new cases
    combined_df = pd.concat([existing_df, new_cases], ignore_index=True)
    
    # Save the combined dataset
    combined_df.to_csv('train_dataset/resume_dataset.csv', index=False)
    
    print(f"Added {len(new_cases)} new cases to the dataset")
    print(f"New dataset shape: {combined_df.shape}")
    print("\nValue counts for should_nudge_resume:")
    print(combined_df['should_nudge_resume'].value_counts())
    
    # Print distribution of batch_resume_uploaded_pct for the new cases
    print("\nDistribution of batch_resume_uploaded_pct in new cases:")
    print(new_cases['batch_resume_uploaded_pct'].describe()) 