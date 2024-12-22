from flask import Flask, request, send_from_directory, jsonify
import os
import subprocess
import re
import json
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # Store uploaded files
OUTPUT_FOLDER = os.path.join(os.getcwd(), "outputs")  # Store generated files
ALLOWED_EXTENSIONS = {'jar'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_function_name(function_name):
    """
    Removes the text inside parentheses (e.g., "(java.lang.String[])") from the function name.
    """
    return re.sub(r'\(.*\)', '()', function_name)

@app.route('/generate', methods=['GET'])
def upload_file():
    methods = []
    function_name = request.args.get('function_name')
    if not function_name:
        return jsonify({"error": "Function name is required"}), 400
    jar_dir = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(jar_dir, "MathProject.jar")

    # Define output paths
    output_txt = os.path.join(OUTPUT_FOLDER, f"cg.txt")
    output_filtered_txt = os.path.join(OUTPUT_FOLDER, f"cg2.txt")
    output_dot = os.path.join(OUTPUT_FOLDER, f"cg.dot")
    output_png = os.path.join(OUTPUT_FOLDER, f"cg.png")
    output_json = os.path.join(OUTPUT_FOLDER, f"cg.json")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_to_static_jar = os.path.join(script_dir, "javacg-0.1-SNAPSHOT-static.jar")


    try:

        subprocess.run(["java", "-jar", path_to_static_jar, file, ">", output_txt], shell=True, check=True)
        with open(output_txt, "r") as infile, open(output_filtered_txt, "w") as outfile:
            for line in infile:
                # Keep only lines containing "function", not containing "<init>", and not starting with "C:"
                if function_name in line and "<init>" not in line and not line.startswith("C:"):
                    #cleaned_line = re.sub(r"\s*\(M\)|\s*\(I\)|\s*\(O\)|\s*\(S\)|\s*\(D\)", "", line)
                    outfile.write(line)

        print("Filtered file saved")


        generate_dot_file(output_filtered_txt, output_dot)
        subprocess.run(
            ["dot", "-Tpng", "-o", output_png, output_dot],
            check=True,
            text=True,
            shell=True
        )

        callers = set()
        calls = set()

        with open(output_filtered_txt, "r") as txt_file:
            for line in txt_file:
                parts = line.strip().split()
                if len(parts) >= 2:
                    caller = parts[0].split(":")[-1]  # Extract the caller function
                    callee = parts[1].split(":")[-1]  # Extract the callee function

                    caller_cleaned = clean_function_name(caller)
                    callee_cleaned = clean_function_name(callee)
                    # If the caller is the function_name, add the callee to calls
                    if function_name in caller_cleaned:
                        calls.add(callee_cleaned)

                    # If the callee is the function_name, add the caller to callers
                    if function_name in callee_cleaned:
                        callers.add(caller_cleaned)

        callers_list = sorted(list(callers))
        calls_list = sorted(list(calls))

        callgraph_json = {
            "function_name": function_name,
            "callers": callers_list,
            "calls": calls_list
        }

        # Write JSON to a file
        with open(output_json, "w") as json_file:
            json.dump(callgraph_json, json_file, indent=4)


        # Check if output files are created
        if not os.path.exists(output_png) or not os.path.exists(output_json):
            return jsonify({"error": "Failed to generate call graph"}), 500

        return jsonify({
            "png_url": f"/download/{os.path.basename(output_png)}",
            "json_url": f"/download/{os.path.basename(output_json)}"
        })
    finally:
        pass




@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


def generate_dot_file(callgraph_txt_path, output_dot_path):
    try:
        with open(output_dot_path, "w") as dot_file:
            # Write the header
            dot_file.write("digraph CallGraph {\n")
            dot_file.write('node [shape=box, style=filled, fillcolor=lightblue, fontname="Arial"];\n')
            dot_file.write('edge [fontname="Arial"];\n')
            # Read the callgraph.txt and write the edges
            with open(callgraph_txt_path, "r") as txt_file:
                for line in txt_file:
                    parts = line.strip().split()
                    if len(parts) >= 2:  # Ensure there are enough parts to form an edge
                        caller = parts[0].split(":")[-1]  # Extract the caller function
                        callee = parts[1].split(":")[-1]  # Extract the callee function
                        #caller_class = parts[0].split(":")[-2]
                        #callee_class = parts[1].split(":")[-2]

                        caller_cleaned = clean_function_name(caller)
                        callee_cleaned = clean_function_name(callee)
                        dot_file.write(f'"{caller_cleaned}" -> "{callee_cleaned}";\n')

            # Write the footer
            dot_file.write("}\n")

        print(f"DOT file generated at {output_dot_path}")
    except Exception as e:
        print(f"Error generating DOT file: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
