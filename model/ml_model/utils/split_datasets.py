import pandas as pd

def split_dataset(input_file, resume_output, event_output):
    # Read the dataset
    df = pd.read_csv(input_file)
    
    # Create resume dataset
    resume_df = df[['resume_uploaded', 'batch_resume_uploaded_pct', 'should_nudge_resume']]
    resume_df.to_csv(resume_output, index=False)
    
    # Create event dataset
    # event_df = df[['karma', 'event_fomo_score', 'should_nudge_event']]
    # event_df.to_csv(event_output, index=False)
    
    print(f"Split {input_file} successfully!")
    print(f"Resume dataset shape: {resume_df.shape}")
    # print(f"Event dataset shape: {event_df.shape}")

# Split training dataset
split_dataset('processed_fomo_dataset_event_karma_noisy_10.csv', 
             'resume_dataset.csv', 
             'event_dataset.csv')