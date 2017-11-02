#!/usr/bin/python

from flask import Flask, jsonify, abort, request, make_response, url_for, redirect, send_file, Response
import docx2txt
import uuid
import os
import io
from pywebhdfs.webhdfs import PyWebHdfsClient
from dse.cluster import Cluster

#Configuration
tmpdir = '/tmp'
contactpoints = ['127.0.0.1','127.0.0.1']
dsefshost='127.0.0.1'

## END OF CONFIG
app = Flask(__name__)

print "Connecting to cluster"
cluster = Cluster( contact_points=contactpoints)
session = cluster.connect()

print "Connecting to DSEFS"
dsefs = PyWebHdfsClient(host=dsefshost,port='5598')

@app.route('/docx/<string:docid>')
def download_file(docid):
    query = """ SELECT dsefspath, filename FROM dsefs_demo.docx WHERE docid = %s """ % (docid)
    results = session.execute(query)
    dsefspath = str(results[0][0])
    filename = str(results[0][1])
    dsefsfile = dsefs.read_file(dsefspath)
    return send_file(io.BytesIO(dsefsfile), attachment_filename=filename, as_attachment=True, mimetype='application/octet-stream')

@app.route('/docx', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            docid = uuid.uuid4()
            dsefspath = 'docx/' + str(docid) + '/' + filename
            dsefs.create_file(dsefspath, file)
            text = docx2txt.process(file)
   
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]

            for line in chunks:
               query =  """ INSERT INTO dsefs_demo.docx (docid, lineid, filename, linetext, dsefspath) VALUES (%s, now(), '%s', '%s', '%s') """ % (docid, filename, line, dsefspath)
               session.execute(query)
            
            return str(docid) + ' Success!'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

