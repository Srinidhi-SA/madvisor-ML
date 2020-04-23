source env/bin/activate
python setup.py bdist_egg
#curl -X POST 'localhost:8090/contexts/pysql-context?context-factory=spark.jobserver.python.PythonSQLContextFactory'
curl --data-binary @dist/marlabs_bi_jobs-0.0.0-py2.7.egg -H 'Content-Type: application/python-archive' 34.196.204.54:8090/binaries/product_revamp
