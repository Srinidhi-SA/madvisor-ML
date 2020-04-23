source env/bin/activate
python setup.py bdist_egg
#curl -X POST '174.129.163.0:8090/contexts/pysql-context?context-factory=spark.jobserver.python.PythonSQLContextFactory'
curl --data-binary @dist/marlabs_bi_jobs-0.0.0-py2.7.egg -H 'Content-Type: application/python-archive' 174.129.163.0:8090/binaries/product_revamp
