import pandas as pd
import csv
from io import BytesIO, StringIO
from flask import jsonify
import tempfile


def process_csv_file(file_object, num_columns=16):
    # Wrap the file object in a TextIO wrapper to ensure it's in text mode
    csv_file = StringIO(file_object.read().decode('utf-8'))

    reader = csv.reader(csv_file)
    headers = next(reader) # Reading the header row here

    data = []
    for row in reader:
        if len(row) > num_columns:
            # Combine overflow columns into the last column
            row = row[:num_columns - 1] + [','.join(row[:num_columns - 1])]
        elif len(row) < num_columns:
            # Pad with empty strings if row is short
            row = row + [''] * (num_columns - len(row))
        data.append(row)

    df = pd.DataFrame(data, columns=headers)
    return df



def merge_big_bom_and_attributes(files):
    try:
        print("Attempting to read upload files...")

        big_bom = process_csv_file(files['big_bom'])
        attributes_table = pd.read_excel(files['attributes_table'])

        # Merge the dataframes based on 'Parent Code' and 'Item'
            # Assuming the columns D to K are at positions 3 to 10, and P and Q are at 15 and 16
        print("Merging Big Bom And Attributes Table...")
        columns_to_merge = ['Parent Code'] + list(big_bom.columns[3:11]) + list(big_bom.columns[15:17])
        merged_df = pd.merge(attributes_table,
                            big_bom[columns_to_merge],
                            left_on='Item', right_on='Parent Code', how='left')

        # Rename columns to avoid confusion
        for col in merged_df.columns:
            if col.endswith('_y'):
                merged_df.rename(columns={col: f'BOM{col[:-2]}'}, inplace=True)
            elif col.endswith('_x'):
                merged_df.rename(columns={col: col[:-2]}, inplace=True)

        # Drop the redundant 'Parent Code' column from big_bom
        merged_df.drop('Parent Code', axis=1, inplace=True)

        print("Preparing result for output...")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            merged_df.to_excel(tmp.name, index=False, engine='openpyxl')
            tmp_path = tmp.name

        return tmp_path

    except KeyError as e:
        return jsonify({'error': f"Missing Required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({'error': f"Invalid value: {str(e)}"}), 400
    except Exception as e:
        print(f"Error in merging big_bom and attributes_table: {str(e)}")
        return jsonify({'error': str(e)}), 500




