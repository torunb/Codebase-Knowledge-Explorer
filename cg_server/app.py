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


@app.route('/upload', methods=['POST'])
def upload_file():
    classes = []
    methods = []
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        jar_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save the file
        file.save(jar_path)

        # Define output paths
        output_txt = os.path.join(OUTPUT_FOLDER, f"{filename.rsplit('.', 1)[0]}.txt")
        output_dot = os.path.join(OUTPUT_FOLDER, f"{filename.rsplit('.', 1)[0]}.dot")
        output_png = os.path.join(OUTPUT_FOLDER, f"{filename.rsplit('.', 1)[0]}.png")
        output_json = os.path.join(OUTPUT_FOLDER, f"{filename.rsplit('.', 1)[0]}.json")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_static_jar = os.path.join(script_dir, "javacg-0.1-SNAPSHOT-static.jar")

        #path_to_static_jar = os.path.join(UPLOAD_FOLDER, "javacg-0.1-SNAPSHOT-static.jar")
        try:

            subprocess.run(["java", "-jar", path_to_static_jar, jar_path, ">", output_txt], shell=True, check=True)

            generate_dot_file(output_txt, output_dot)
            subprocess.run(
                ["dot", "-Tpng", "-o", output_png, output_dot],
                check=True,
                text=True,
                shell=True
            )

            with open(output_txt, "r") as file:
                for line in file:
                    line = line.strip()
                    # Match class relationships
                    if match := re.match(r"^C:(.+?) (.+)$", line):
                        classes.append({
                            "CallerClass": match.group(1),
                            "CalleeClass": match.group(2)
                        })
                    # Match method relationships
                    elif match := re.match(
                            r"^M:(.+?):(.+?)\((.*?)\) \((.+?)\)(.+?):(.+?)\((.*?)\)$", line
                    ):
                        methods.append({
                            "CallerClass": match.group(1),
                            "CallerMethod": match.group(2),
                            "CallerSignature": match.group(3),
                            "Type": match.group(4),  # (O), (S), (M), etc.
                            "CalleeClass": match.group(5),
                            "CalleeMethod": match.group(6),
                            "CalleeSignature": match.group(7),
                        })

            # Combine results into a single dictionary
            callgraph_json = {
                "Classes": classes,
                "Methods": methods
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
            # Optionally delete the input file after processing
            if os.path.exists(jar_path):
                os.remove(jar_path)
    else:
        return jsonify({"error": "Invalid file type. Only .jar files are allowed."}), 400


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

            # Read the callgraph.txt and write the edges
            with open(callgraph_txt_path, "r") as txt_file:
                for line in txt_file:
                    parts = line.strip().split()
                    if len(parts) >= 2:  # Ensure there are enough parts to form an edge
                        dot_file.write(f'"{parts[0]}" -> "{parts[1]}";\n')

            # Write the footer
            dot_file.write("}\n")

        print(f"DOT file generated at {output_dot_path}")
    except Exception as e:
        print(f"Error generating DOT file: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
