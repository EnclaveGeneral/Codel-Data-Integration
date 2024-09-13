import pandas as pd
from flask import jsonify
import tempfile

def filter_attributes(files):
    try:
        print("Attempting to read upload files...")

        attributes_df = pd.read_excel(files['attributes_table'])
        adjacency_df = pd.read_excel(files['bom_adjacency'])

        # Extract unique values from columns B and D of the CSV file
        filter_values = set(adjacency_df.iloc[:,1].astype(str).tolist() + adjacency_df.iloc[:,3].astype(str).tolist())

        # Function to check if any filter value is in the cell
        def contains_filter_value(cell, filter_values):
            if pd.isna(cell):
                return False
            cell_str = str(cell)

            # Check if the cell is a simple string match
            if cell_str in filter_values:
                return True

            # Split the cell by '__' and check each part
            parts = cell_str.split('__')
            return any(part in filter_values for part in parts)

        # Apply the filter to columns H, I, and J
        mask = (
            attributes_df.iloc[:,7].apply(lambda x: contains_filter_value(x, filter_values)) |
            attributes_df.iloc[:,8].apply(lambda x: contains_filter_value(x, filter_values)) |
            attributes_df.iloc[:,9].apply(lambda x: contains_filter_value(x, filter_values))
        )

        # Filter the Excel DataFrame
        filtered_adjacency_df = attributes_df[mask]

        # Remove unecessary columns if they are completely blank / empty
        filtered_adjacency_df.dropna(how='all')

        print("Preparing result for output...")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            filtered_adjacency_df.to_excel(tmp.name, index=False, engine='openpyxl')
            tmp_path = tmp.name

        return tmp_path

    except KeyError as e:
        return jsonify({'error': f"Missing Required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({'error': f"Invalid value: {str(e)}"}), 400
    except Exception as e:
        print(f"Error in filtering attributes table on adjacency BOM: {str(e)}")
        return jsonify({'error': str(e)}), 500



