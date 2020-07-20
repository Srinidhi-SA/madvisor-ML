# marlabs-bi
Business Intelligence application by Marlabs. Contains Python code thats run on spark clusters for business insight generation.

## Installation

    pip instal -r requirements.txt`
python setup.py bdist_egg

curl -X POST 'localhost:8090/contexts/pysql-context?context-factory=spark.jobserver.python.PythonSQLContextFactory'
curl --data-binary @dist/marlabs_bi_jobs-0.0.0-py2.7.egg -H 'Content-Type: application/python-archive' localhost:8090/binaries/test_api_1

## Code Layout
    - code layout details....

## Writing unit test cases
    * unit test conventions.....

## Code coverage reports
    * code coverage tool: [coverage.py](https://coverage.readthedocs.io/en/coverage-4.3.4/)
    * Procedure to generate coverage reports:
        * Run unit tests and collect coverage stats:
            ```python
            >>> coverage run -m bi.tests
            ```
        * Generate coverage reports


### Submitting spark jobs to cluster
    ```
    $ spark-submit --master {spark-url} {pyspark-script} --arg1-name arg1 --arg2-name arg2 ....

    * spark-url: spark cluster master url, of the form *spark://host:port*
    * pyspark-script: python script to be submitted to spark cluster
    * arguments: all args have arg name token followed by arg value
    ```
## Spark job monitoring

    * job failures
        * due to errors in python script: fix errros in the code and resubit the job again
        * due to system (spark/hadoop) errors: fix system errors and re-submit the job.
            On standalone spark cluster, many a times spark driver is freezing.
            Restarting the spark cluster resolved the issue.

    * Monitoring system should be able identify both application and system errors.

    * Its still work in progress


## spark jobs
0. [Metadata](https://github.com/rammohan/marlabs-bi/blob/master/docs/Metadata.md)
1. [Descriptive Statistics](https://github.com/rammohan/marlabs-bi/blob/master/docs/Descriptive_Stats.md)
2. [Trend Analysis](https://github.com/rammohan/marlabs-bi/blob/master/docs/Trend.md)
3. [Anova](https://github.com/rammohan/marlabs-bi/blob/master/docs/Anova.md)
4. [Regression](https://github.com/rammohan/marlabs-bi/blob/master/docs/Regression.md)
5. [Frequency Calculation](https://github.com/rammohan/marlabs-bi/blob/mitali_dev/docs/Frequency_Dimension.md)
6. [Chi Square Test](https://github.com/rammohan/marlabs-bi/blob/mitali_dev/docs/ChiSquare.md)
7. [Decision Tree](https://github.com/rammohan/marlabs-bi/blob/mitali_dev/docs/DecisionTree.md)
