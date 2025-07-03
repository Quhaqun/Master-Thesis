from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)

@app.route('/submit_trial', methods=['POST'])
def submit_trial():
    header = ['objx_0', 'objy_0', 'objx_1', 'objy_1', 'objx_2', 'objy_2', 'objx_3', 'objy_3', 'objx_4', 'objy_4',
              'objx_5', 'objy_5', 'objx_6', 'objy_6', 'objx_7', 'objy_7', 'objx_8', 'objy_8', 'objx_9', 'objy_9',
              'objx_10', 'objy_10', 'objx_11', 'objy_11', 'objx_12', 'objy_12', 'objx_13', 'objy_13', 'objx_14',
              'objy_14',
              'objx_15', 'objy_15', 'objx_16', 'objy_16', 'objx_17', 'objy_17', 'objx_18', 'objy_18',
              'Subnum', 'Trial', 'player1correct', 'player1incorrect',
              'player2correct', 'player2incorrect', 'paircorrect', 'pairincorrect',
              'player1total', 'player2total', 'pairtotal', 'doublesel',
              'Markalltime', 'AGE', 'GENDER', 'HANDEDNESS', 'CONDITION',
              'Experiment', 'ChosenHuman', 'ChosenAI',
              'selobj1', 'selobj2', 'selobj3', 'selobj4', 'selobj5', 'selobj6',
              'selobj7', 'selobj8', 'selobj9', 'selobj10', 'selobj11', 'selobj12',
              'selobj13', 'selobj14', 'selobj15', 'selobj16', 'selobj17', 'selobj18', 'selobj19',
              'selobjother1', 'selobjother2', 'selobjother3', 'selobjother4', 'selobjother5', 'selobjother6',
              'selobjother7', 'selobjother8', 'selobjother9', 'selobjother10', 'selobjother11', 'selobjother12',
              'selobjother13', 'selobjother14', 'selobjother15', 'selobjother16', 'selobjother17', 'selobjother18',
              'selobjother19', 'Selectiontime', 'ReactiontimeSelection', 'ReactiontimeMarkall', 'Resolution', 'AverageSpeed']

    try:
        # Get list data directly
        content = request.get_json()
        Subnum = content.get("Subnum")
        row = content.get("row")

        EXPPATH = os.path.dirname(os.path.abspath(__file__))
        SUBDIR = os.path.join(EXPPATH, f"Data/Pair{Subnum}")
        csvfile = content.get("csvfile")
        path = os.path.join(SUBDIR, csvfile)
        writeheader = content.get("writeheader")

        if not isinstance(row, list):
            return jsonify({"status": "error", "message": "Expected a list"}), 400

        # Create subdir if it doesn't exist
        if not os.path.exists(SUBDIR):
            os.makedirs(SUBDIR)
        if writeheader:
            if not os.path.exists(path):
                with open(path, 'w', newline='') as f:
                    wr = csv.writer(f)
                    wr.writerow(header)

        # Append to CSV
        if writeheader:
            with open(path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        else:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(row)

        return jsonify({"status": "ok", "message": "Row saved successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/submit_email', methods=['POST'])
def submit_email():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"status": "error", "message": "No email provided"}), 400

        EXPPATH = os.path.dirname(os.path.abspath(__file__))
        email_file = os.path.join(EXPPATH, "Data/emails.csv")

        # Falls Datei neu: Header schreiben
        write_header = not os.path.exists(email_file)

        with open(email_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["email"])
            writer.writerow([email])

        return jsonify({"status": "ok", "message": "Email saved successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
