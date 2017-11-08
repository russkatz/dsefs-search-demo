#!/usr/bin/python
# Russ Katz
# DataStax Solutions Engineer
# Tested with DSE 5.1
# Created: 11/03/2017
# Updated: 11/07/2017

from flask import Flask, jsonify, abort, request, make_response, url_for, redirect, send_file
import docx2txt
import uuid
import os
import io
from pywebhdfs.webhdfs import PyWebHdfsClient
from dse.cluster import Cluster

#Configuration
contactpoints = ['127.0.0.1','127.0.0.1']
dsefshost='127.0.0.1'

## END OF CONFIG
app = Flask(__name__)

print "Connecting to cluster"
cluster = Cluster( contact_points=contactpoints)
session = cluster.connect()

print "Connecting to DSEFS"
dsefs = PyWebHdfsClient(host=dsefshost,port='5598')

# REST endpoint to retrieve a docid from DSEFS
@app.route('/docx/<string:docid>')
def download_file(docid):
    # Create query string for docid from request URL
    query = """ SELECT dsefspath, filename FROM dsefs_demo.docx WHERE docid = %s """ % (docid)
    # Execute query (NOTE: This is syncronous, use session.aexecute for async)
    results = session.execute(query)
    # Grab the results
    dsefspath = str(results[0][0])
    filename = str(results[0][1])
    # Read the file in from DSEFS
    dsefsfile = dsefs.read_file(dsefspath)
    # Return the file
    return send_file(io.BytesIO(dsefsfile), attachment_filename=filename, as_attachment=True, mimetype='application/octet-stream')

# Rest endpoint for uploading a new docx file
# Security note: There is NO filetype verification done, and we are trusting user input for the filename.
@app.route('/docx', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if there is a file attached to the request
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            # Get filename from request (See security note)
            filename = file.filename
            # Create docid
            docid = uuid.uuid4()
            # Create path to save file in DSEFS
            dsefspath = 'docx/' + str(docid) + '/' + filename
            # Write file to DSEFS
            dsefs.create_file(dsefspath, file)
            # Use docx2txt library to extract text from docx file 
            text = docx2txt.process(file)
   
            # Break up text into chunks for even partitioning later
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]

            # Write extracted text to DSE Core, one row per chunk.
            for line in chunks:
               query =  """ INSERT INTO dsefs_demo.docx (docid, lineid, filename, linetext, dsefspath) VALUES (%s, now(), '%s', '%s', '%s') """ % (docid, filename, line, dsefspath)
               session.execute(query)
            
            # Celebrations \o/
            return str(docid) + ' Success!'
    # NONE SHALL PASS!
    return 403
