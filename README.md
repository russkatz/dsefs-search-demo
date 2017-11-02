# DataStax DSEFS + Search
### This demo uses the Datastax Python Driver + Flask to create a REST API for submitting and retrieving Microsoft DOCX files. The DOCX files are stored in DSEFS and the metadata is stored in DSE and indexed for searching.

#### Prereqs
* DSE 5.1+
  * Search enabled
  * DSEFS enabled
* Datastax Python Driver
   * `pip install dse-driver`
* Other Python drivers
   * Flask: `pip install flask`
   * pyWebHDFS: `pip install pywebhdfs`
   * docx2txt: `pip install docx2txt`
* Curl
* git

#### Setup
* Download Repository
   * `git clone https://github.com/russkatz/dsefs-search-demo && cd dsefs-search-demo`
* Create data model
   * This uses simple replication with RF=1. You may need to adjust this.
   * `cqlsh -f create_schema.cql`
* Configure DSE Search index
   * cqlsh: `CREATE SEARCH INDEX ON dsefs_demo.docx WITH OPTIONS { reindex : true };`
* Configure Flask
   * `export FLASK_APP=docxapi.py`
   
#### Running
* Start API server
   * `flask run --host=0.0.0.0 &`
* Submit docx file
   * `curl -F 'file=@test1.docx' http://127.0.0.1:5000/docx`
* Verify metadata in DSE
   * cqlsh: `SELECT * FROM dsefs_demo.docx`
* Verify Search is indexing
   * cqlsh: `SELECT docid,dsefspath WHERE solr_query = 'linetext:"DataStax cluster"';`
   * You will need the dsefspath and docid later
* Verify file is in DSEFS
   * Start dsefs command prompt: `dse fs`
   * `ls <dsefspath from above>`
* Download file through the API
   * `curl -JLO http://127.0.0.1:5000/docx/<docid from above>`
   * Example: `curl -JLO http://127.0.0.1:5000/docx/88dcf35e-4261-4c0f-936a-c5d9d44bc035`
