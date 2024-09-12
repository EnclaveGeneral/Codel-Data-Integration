from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from methods.bom_graph import bom_graph
from methods.bom_adjacency import process_bom_adjacency
from methods.merge_big_bom_attributes import merge_big_bom_and_attributes
from methods.filter_attributes_on_adjacent import filter_attributes

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

static_folder = os.path.join(application_path, 'static')
app = Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app)

print(f"Static folder path: {app.static_folder}")
print(f"Does static folder exist: {os.path.exists(app.static_folder)}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/process', methods=['POST'])
def process_files():
    print("Process endpoint hit")
    try:
        method = request.form.get('method')
        print(f"Method: {method}")

        if method == 'bom_adjacency':
            print("Executing bom_adjacency")
            result = process_bom_adjacency(request)
            print(f"bom_adjacency result: {result}")
            return result
        elif method == 'bom_graph':
            print("Executing bom_graph")
            bom_details_list = request.files['bom_details_list.xlsx']
            bom_parents_list = request.files['bom_parents_list.xlsx']
            try:
                output = bom_graph({'bom_details_list': bom_details_list, 'bom_parents_list': bom_parents_list})
                print("Output generated successfully, attempting to send file...")
                return send_file(
                    output,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='bom_graph.csv'
                )
            except Exception as e:
                print(f"Error in bom_graph: {str(e)}")
                return jsonify({"error": str(e)}), 500
        elif method == 'bom_merge':
            print("Executing bom_merge")
            big_bom = request.files['big_bom.csv']
            attributes_table = request.files['attributes_table.xlsx']
            try:
                tmp_path = merge_big_bom_and_attributes({'big_bom': big_bom, 'attributes_table': attributes_table})
                print("Output generated successfully, attempting to send file...")
                return_value = send_file(
                    tmp_path,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name='merged_big_bom_attributes.xlsx'
                )

                @return_value.call_on_close
                def remove_temp():
                    os.remove(tmp_path)

                return return_value
            except Exception as e:
                print(f"Error in bom_merge: {str(e)}")
                return jsonify({"error": str(e)}), 500
        elif method == 'filter_on_adjacency':
            print("Attempting to filter...")
            bom_adjacency = request.files["bom_adjacency.xlsx"]
            attributes_table = request.files["attributes_table.xlsx"]
            try: 
                tmp_path = filter_attributes({'bom_adjacency': bom_adjacency, 'attributes_table':attributes_table})
                print("Outpuyt generated successfully, attempting to send file...")
                return_value = send_file(
                    tmp_path,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name='attributes_filtered_on_adjacency.xlsx'
                )

                @return_value.call_on_close
                def remove_temp():
                    os.remove(tmp_path)

                return return_value
            except Exception as e:
                print(f"Error in attributes filter: {str(e)}")
                return jsonify({"error": str(e)}), 500
        else:
            print(f"Invalid method: {method}")
            return jsonify({"error": "Invalid method specified"}), 400
    except Exception as e:
        print(f"Error in process_files: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Include your existing helper functions here:
# find_precursors_and_successors, get_description, get_next_description, write_to_excel

@app.route('/get_methods_info', methods=['GET'])
def get_method_info():
    method_info = {
        'bom_adjacency': {
            'input files': [{'name': 'bom_file', 'type': 'csv'}],
            'params': [
                {'name': 'central_bom_id', 'type': 'number'},
                {'name': 'max_distance', 'type': 'number'}
            ]
        },
        'bom_graph': {
            'files': [{'name': 'bom_details', 'type': 'xlsx'}, {'name': 'bom_parents', 'type': 'xlsx'}],
        },
        'merge_big_bom_attributes': {
            'files': [{'name': 'big_bom', 'type': 'csv'}, {'name': 'attributes_table', 'type': 'xlsx'}],
        }
    }
    return jsonify(method_info)

if __name__ == '__main__':
    app.run(debug=False)

