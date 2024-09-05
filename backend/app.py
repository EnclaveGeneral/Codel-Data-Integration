from flask import Flask, request, send_file, jsonify
import traceback
from flask_cors import CORS
from methods.bom_graph import bom_graph
from methods.bom_adjacency import process_bom_analysis

app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])

@app.route('/process', methods=['POST'])
def process_files():
    try:
        method = request.form.get('method')
        if method == 'bom_analysis':
            return process_bom_analysis(request)
        elif method == 'bom_graph':
            bom_details_list = request.files['bom_details_list']
            bom_parents_list = request.files['bom_parents_list']
            try:
                output = bom_graph({'bom_details_list': bom_details_list, 'bom_parents_list': bom_parents_list})
                print("Output generated successfully, attempting to send file...")
                return send_file(
                    output,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='bom_graph.csv'  # Changed this line
                )
            except Exception as e:
                print(f"Error in method2 or sending file: {str(e)}")
                print(traceback.format_exc())
                return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Error in process_files: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# Include your existing helper functions here:
# find_precursors_and_successors, get_description, get_next_description, write_to_excel

@app.route('/get_method_info', methods=['GET'])
def get_method_info():
    method_info = {
        'bom_analysis': {
            'files': [{'name': 'bom_file', 'type': 'csv'}],
            'params': [
                {'name': 'central_bom_id', 'type': 'number'},
                {'name': 'max_distance', 'type': 'number'}
            ]
        },
        'method2': {
            'files': [{'name': 'file1', 'type': 'csv'}, {'name': 'file2', 'type': 'xlsx'}],
            'params': [
                {'name': 'param1', 'type': 'string'},
                {'name': 'param2', 'type': 'number'}
            ]
        },
        'method3': {
            'files': [{'name': 'data_file', 'type': 'json'}],
            'params': [
                {'name': 'option', 'type': 'string'}
            ]
        }
    }
    return jsonify(method_info)

if __name__ == '__main__':
    app.run(debug=True)

