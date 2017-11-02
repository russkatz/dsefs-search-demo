CREATE KEYSPACE dsefs_demo WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}  AND durable_writes = true;

CREATE TABLE dsefs_demo.docx (
    docid uuid,
    lineid timeuuid,
    dsefspath text,
    filename text,
    linetext text,
    PRIMARY KEY (docid, lineid)
);
