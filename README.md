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
