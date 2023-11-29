import pandas as pd
import os

def determine_band(mode):
    """ Determine the band based on the mode. """
    return 'Wide' if mode == 'FM' else 'Narrow'

def calculate_txfreq(row):
    """ Calculate Channel_TxFreq based on Duplex and Offset. """
    if row['Duplex'] == '+':
        return row['Channel_RxFreq'] + row['Offset']
    elif row['Duplex'] == '-':
        return row['Channel_RxFreq'] - row['Offset']
    else:
        return row['Channel_RxFreq']

def set_tone_values(row):
    """ Set the Channel_RxQt and Channel_TxQt values based on the Tone column. """
    tone = row['Tone']
    if tone == '':
        return 'Off', 'Off'
    elif tone == 'Tone':
        return row['rToneFreq'], 'Off'
    elif tone == 'TSQL':
        return 'Off', row['cToneFreq']
    elif tone == 'DTCS':
        return 'Off', row['cToneFreq']
    else:
        return 'Off', 'Off'

def transform_csv(input_csv_path, output_csv_path):
    try:
        # Read the original CSV file
        df = pd.read_csv(input_csv_path)
        print("Input CSV file read successfully.")

        # Renaming and mapping columns
        df = df.rename(columns={
            'Location': 'Channel_SN',
            'Name': 'Channel_Name',
            'Frequency': 'Channel_RxFreq',
            'Power': 'Channel_Power'
        })

        # Incrementing Channel_SN values by 101
        df['Channel_SN'] = df['Channel_SN'].astype(int) + 101

        # Calculating Channel_TxFreq
        df['Channel_TxFreq'] = df.apply(calculate_txfreq, axis=1)

        # Apply the set_tone_values function to set Channel_RxQt and Channel_TxQt
        df[['Channel_RxQt', 'Channel_TxQt']] = df.apply(set_tone_values, axis=1, result_type='expand')
        print("Tone values set.")

        # Determining Channel_Band based on Mode
        df['Channel_Band'] = df['Mode'].apply(determine_band)
        print("Channel band determined.")

        # Setting default values for the missing columns
        default_values = {
            'Channel_MuteMode': 'QT',
            'Channel_Scream': 'OFF',
            'Channel_ScanAdd': 'ON',
            'Channel_Compand': 'OFF',
            'Channel_AM': 'OFF',
            'Channel_FAV': 'OFF',
            'Channel_SendLoc': 'OFF',
            'Channel_CallCodeSn': '1',
            'Channel_TxFreq': 0
        }
        for col, default in default_values.items():
            if col not in df.columns:
                df[col] = default

        # Define the ordered columns as specified
        ordered_columns = [
            'Channel_SN', 'Channel_RxFreq', 'Channel_TxFreq', 'Channel_RxQt', 
            'Channel_TxQt', 'Channel_Power', 'Channel_Band', 'Channel_MuteMode', 
            'Channel_Scream', 'Channel_ScanAdd', 'Channel_Compand', 'Channel_AM', 
            'Channel_FAV', 'Channel_SendLoc', 'Channel_CallCodeSn', 'Channel_Name'
        ]

        # Check if output.csv exists and read it, otherwise create an empty DataFrame
        if os.path.exists(output_csv_path):
            output_df = pd.read_csv(output_csv_path)
            print("Existing output CSV file read successfully.")
            # Ensure Channel_SN is an integer column in the existing output_df
            if 'Channel_SN' in output_df.columns:
                output_df['Channel_SN'] = output_df['Channel_SN'].astype(int)
            else:
                print("Channel_SN column missing in existing output CSV file.")
                raise ValueError("Channel_SN column missing in existing output CSV file.")
        else:
            output_df = pd.DataFrame(index=range(1, 1000), columns=ordered_columns)
            print("Created a new empty DataFrame for output.")

        # Log the existing and new Channel_SN values
        print("Existing Channel_SN values:", output_df['Channel_SN'].dropna().astype(int).tolist())
        print("New Channel_SN values:", df['Channel_SN'].astype(int).tolist())

        # Update the DataFrame with new data
        for _, row in df.iterrows():
            row_index = row['Channel_SN']
            new_row_data = row[ordered_columns]

                        # Check if the new row is empty and the existing row has data
            if new_row_data.isnull().all() and not output_df.loc[row_index].isnull().all():
                continue  # Keep the existing data
            output_df.loc[row_index] = new_row_data

        # Replace NaN values with empty strings
        output_df.fillna('', inplace=True)

        # Write the updated data to the output CSV file
        output_df.to_csv(output_csv_path, index=False)
        print(f"Output CSV file updated and written to {output_csv_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Sample usage (replace 'input.csv' and 'output.csv' with your actual file paths)
transform_csv('input.csv', 'output.csv')

