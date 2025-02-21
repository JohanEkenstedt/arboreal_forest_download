import requests
import pandas as pd
import json

def validate_api_key(api_key):
    """Validate the API key format."""
    return bool(api_key.strip())  # Just check if there's a non-empty key

def format_api_key(api_key):
    """Format the API key by adding 'Key ' prefix if not present."""
    api_key = api_key.strip()
    if not api_key.startswith("Key "):
        api_key = f"Key {api_key}"
    return api_key

def get_samples(api_key):
    """Fetch samples from the Arboreal API."""
    try:
        api_endpoint = "https://api.arboreal.se/getFilteredSamples"
        formatted_key = format_api_key(api_key)
        headers = {
            'Accept': 'application/json',
            "Authorization": formatted_key
        }
        response = requests.get(
            api_endpoint,
            headers=headers
        )

        if response.status_code != 200:
            return None

        samples_json = response.json()
        samples_df = pd.json_normalize(samples_json)

        # Reorder columns as in the notebook
        desired_columns = [
            'sample_id', 'external_id', 'external_name', 'name', 'unix_time', 
            'area', 'sample_radius', 'measure_method_type', 'longitude', 'latitude',
            'altitude', 'gps_stamp_horizontal_accuracy', 'center_x', 'center_y',
            'center_z', 'tracking_not_available', 'tracking_limited',
            'tracking_normal', 'latest_sync', 'heading', 'comment', 'customer_id',
            'app_version', 'model'
        ]
        return samples_df.reindex(columns=desired_columns)
    except Exception as e:
        print(f"Error fetching samples: {str(e)}")
        return None

def get_sample_details(api_key, sample_id):
    """Fetch detailed information for a specific sample."""
    try:
        api_endpoint = "https://api.arboreal.se/getSampleById"
        formatted_key = format_api_key(api_key)
        parameters = {"id": sample_id}
        headers = {
            'Accept': 'application/json',
            "Authorization": formatted_key
        }

        response = requests.get(api_endpoint, headers=headers, params=parameters)

        if response.status_code != 200:
            return None

        return response.json()
    except Exception as e:
        print(f"Error fetching sample details: {str(e)}")
        return None