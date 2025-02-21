import pandas as pd
import numpy as np
from api_handler import get_sample_details
from tqdm import tqdm

def process_sample_data(api_key, samples_df, status_text, progress_bar):
    """Process sample data and return all required DataFrames."""
    try:
        samples_array = samples_df[['sample_id']].values.astype(int)

        # Initialize empty lists for collecting data
        trees_data = []
        stems_data = []
        calculations_data = []
        height_data = []

        # Process each sample
        total_samples = len(samples_array)
        for idx, sample_id in enumerate(samples_array):
            try:
                sample_json = get_sample_details(api_key, int(sample_id[0]))  # Extract the integer from the array
                if not sample_json or not isinstance(sample_json, list) or len(sample_json) == 0:
                    print(f"Invalid sample data for ID {sample_id[0]}")
                    continue

                sample_data = sample_json[0]
                if 'trees' not in sample_data or not sample_data['trees']:
                    print(f"No trees data found for sample ID {sample_id[0]}")
                    continue

                # Process trees
                trees = sample_data['trees']
                if not trees or len(trees) == 0:
                    print(f"Empty trees data for sample ID {sample_id[0]}")
                    continue

                trees_df = pd.json_normalize(trees[0])
                if not trees_df.empty:
                    trees_df['sample_id'] = sample_id[0]
                    trees_data.append(trees_df)

                # Process stems
                if 'stems' in trees[0]:
                    stems_df = pd.json_normalize(trees[0], record_path=['stems'])
                    stems_df = stems_df.rename(columns={'id': 'stem_id', 'name': 'stem_name'})
                    stems_df['tree_id'] = trees[0].get('tree_id')
                    stems_df['sample_id'] = sample_id[0]
                    if not stems_df.empty:
                        stems_data.append(stems_df)

                # Process calculations
                if 'calculations' in sample_data:
                    calc_df = pd.DataFrame(sample_data['calculations'])
                    if not calc_df.empty:
                        calculations_data.append(calc_df)

                # Process heights
                if 'heightAgeGrowth' in sample_data:
                    heights_df = pd.DataFrame(sample_data['heightAgeGrowth'])
                    heights_df = heights_df.rename(columns={'id': 'height_id', 'name': 'stem_name'})
                    if not heights_df.empty:
                        height_data.append(heights_df)

            except Exception as e:
                print(f"Error processing sample {sample_id[0]}: {str(e)}")
                continue

            # Update progress
            progress = 30 + (60 * (idx + 1) / total_samples)
            progress_bar.progress(int(progress))
            status_text.text(f"Processing sample {idx + 1} of {total_samples}...")

        # Combine all data
        combined_data = {
            'Samples': samples_df,
            'Trees': pd.concat(trees_data, ignore_index=True) if trees_data else pd.DataFrame(),
            'Stems': pd.concat(stems_data, ignore_index=True) if stems_data else pd.DataFrame(),
            'Calculations': pd.concat(calculations_data, ignore_index=True) if calculations_data else pd.DataFrame(),
            'Heights': pd.concat(height_data, ignore_index=True) if height_data else pd.DataFrame()
        }

        # Process specific columns
        if len(combined_data['Stems']) > 0:
            combined_data['Stems'].loc[combined_data['Stems']['diameter'].notna(), 'diameter'] *= 100

        if len(combined_data['Heights']) > 0:
            combined_data['Heights'].loc[combined_data['Heights']['diameter'].notna(), 'diameter'] *= 100

        return combined_data

    except Exception as e:
        print(f"Error processing sample data: {str(e)}")
        return None