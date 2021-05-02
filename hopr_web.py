from flask import Flask, request, jsonify, render_template
from google.cloud import storage
import logging
from werkzeug.exceptions import HTTPException



app = Flask(__name__)
bucketName = 'hopr-parameter-files'
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s')

def random_string(length):
    import random
    import string

    pool = string.letters + string.digits
    return ''.join(random.choice(pool) for i in xrange(length))

def copy_local_directory_to_gcs(local_path, bucket, gcs_path):
    """Recursively copy a directory of files to GCS.

    local_path should be a directory and not have a trailing slash.
    """
    # From https://stackoverflow.com/questions/48514933/how-to-copy-a-directory-to-google-cloud-storage-using-google-cloud-python-api
    import os
    import glob

    assert os.path.isdir(local_path)
    for local_file in glob.glob(local_path + '/**'):
        if not os.path.isfile(local_file):
            continue
        remote_path = os.path.join(gcs_path, local_file[1 + len(local_path) :])
        blob = bucket.blob(remote_path)
        blob.upload_from_filename(local_file)


@app.route('/', methods=["GET"])
# API Version 1.0
def index():
    """HOPr Web API Version 0.0.0."""

    client = storage.Client()
    bucket = client.get_bucket(bucketName)
    blobs = bucket.list_blobs()
    files = []
    for blob in blobs:
        files.append(blob.name)
    return jsonify(files)

@app.route("/meshgen", methods=['GET'])
def meshgen():
    import os
    import subprocess

    parameter_file = request.args.get("parameter_ini","tutorials/1-01-cartbox/parameter.ini")
    local_path = "/workspace/"+random_string(32)
    os.mkdir(local_path)
    logging.info('Processing HOPr parameter file {}'.format(parameter_file))

    # Download parameter file from bucket into container
    client = storage.Client()
    bucket = client.get_bucket(bucketName)
    blob = bucket.blob(parameter_file)
    try:
        blob.download_to_filename("/workspace/parameter.ini")
    except:
        err = 'Failed to download {} from {}'.format(parameter_file,bucketName
        logging.error(err)
        handle_error(err)


    # Run HOPr
    output = subprocess.run(['/opt/view/bin/hopr',local_path+'/parameter.ini'],
                            cwd=local_path,
                            capture_output=True)
    if output.returncode == 0:
      copy_local_directory_to_gcs(local_path, bucket, local_path)
      return jsonify( {gcs_bucket=bucketName,path=local_path} ) 
    else:
      handle_error(output.stderr)


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code=e.code
    return jsonify(error=str(e)), code

if __name__ == "__main__":
    # Used when running locally only. When deploying to Cloud Run,
    # a webserver process such as Gunicorn will serve the app.
    print(__name__)
    app.run(host="localhost", port=8080, debug=True)
