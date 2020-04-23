"""
functions to load data from various sources to create a dataframe
"""

from pyspark.sql import SparkSession, HiveContext
from pyspark import SparkContext, SparkConf

from decorators import accepts


class DataLoader:

    @staticmethod
    @accepts(SparkSession, basestring, has_header=bool, interpret_data_schema=bool)
    def load_csv_file(spark_session, csv_file_path, has_header=True, interpret_data_schema=True):
        return spark_session.read.csv(csv_file_path, header=has_header, inferSchema=interpret_data_schema)

    @staticmethod
    @accepts(SparkSession, basestring, dict)
    def create_dataframe_from_jdbc_connector(spark_session, datasource_type, dbConnectionParams):
        datasource_type = datasource_type.lower()
        print "~"*100
        print "Data Source :- ",datasource_type
        print "Database Connection Params :- ",dbConnectionParams
        print "~"*100
        if "hana" == datasource_type:
            return DataLoader.create_dataframe_from_hana_connector(spark_session, dbConnectionParams)
        elif "mysql" == datasource_type:
            return DataLoader.create_dataframe_from_mysql_db(spark_session, dbConnectionParams)
        elif "mssql" == datasource_type:
            return DataLoader.create_dataframe_from_mssql_db(spark_session, dbConnectionParams)
        elif "oracle" == datasource_type:
            return DataLoader.create_dataframe_from_oracle_db(spark_session, dbConnectionParams)
        elif "hive" == datasource_type:
            return DataLoader.create_dataframe_from_hive(spark_session, dbConnectionParams)

    @staticmethod
    @accepts(SparkSession, dict)
    def create_dataframe_from_mysql_db(spark_session, dbConnectionParams):
        df = None
        # change jdbc_url

        jdbc_url = "jdbc:mysql://{}:{}/{}".format(dbConnectionParams["host"], dbConnectionParams["port"], DataLoader.get_db_name(dbConnectionParams))
        print jdbc_url

        table_name = dbConnectionParams.get("tablename")
        username = dbConnectionParams.get("username")
        password = dbConnectionParams.get("password")
        try:
            df = spark_session.read.format("jdbc").option(
                "url", jdbc_url).option(
                "dbtable", "{}".format(table_name)).option(
                "user", username).option("password", password).load()
            return df
        except Exception as e:
            print("couldn't connect to database")
            print e
        return df

    @staticmethod
    @accepts(SparkSession, dict)
    def create_dataframe_from_mssql_db(spark_session, dbConnectionParams):
        df = None
        # change jdbc_url
        jdbc_url = "jdbc:sqlserver://{}:{};databaseName={};".format(dbConnectionParams["host"], dbConnectionParams["port"],
                                                                    DataLoader.get_db_name(dbConnectionParams))
        try:
            df = spark_session.read.format("jdbc").option("url", jdbc_url).option("dbtable", "{}".format(
                dbConnectionParams.get("tablename"))).option("user", dbConnectionParams.get("username")).option(
                "password", dbConnectionParams.get("password")).load()

        except Exception as e:
            print("couldn't connect to database")
        return df

    @staticmethod
    @accepts(SparkSession, dict)
    def create_dataframe_from_oracle_db(spark_session, dbConnectionParams):
        pass

    @staticmethod
    @accepts(SparkSession, dict)
    def create_dataframe_from_hana_connector(spark_session, dbConnectionParams):
        df = None
        jdbc_url = "jdbc:sap://{}:{}/?currentschema={}".format(dbConnectionParams["host"], dbConnectionParams["port"], DataLoader.get_db_name(dbConnectionParams))
        table_name = dbConnectionParams.get("tablename")
        username = dbConnectionParams.get("username")
        password = dbConnectionParams.get("password")
        try:
            df = spark_session.read.format("jdbc").option(
                "url", jdbc_url).option("driver", "com.sap.db.jdbc.Driver").option(
                "dbtable", table_name).option("user", username).option("password", password).load()
        except Exception as e:
            print("couldn't connect to hana")
            raise e
        return df

    @staticmethod
    @accepts(SparkSession, dict)
    def create_dataframe_from_hive(spark_session, dbConnectionParams):
        df = None
        try:
            sc = SparkSession.builder.appName("Testing").config(conf=SparkConf()).enableHiveSupport().getOrCreate()
            sqlContext = HiveContext(sc)
            sqlContext.setConf("hive.metastore.uris", "thrift://{}:{}".format(dbConnectionParams.get("host"),dbConnectionParams.get("port")))

            tdf=sqlContext.sql("show databases")
            tdf.show()

            schema = DataLoader.get_db_name(dbConnectionParams)
            table_name = dbConnectionParams.get("tablename")
            df = sqlContext.table(".".join([schema,table_name]))

        except Exception as e:
            print("couldn't connect to hive")
            raise e
        return df

    @staticmethod
    def get_db_name(dbConnectionParams):
        if "schema" in dbConnectionParams.keys():
            return dbConnectionParams.get("schema")
        elif "databasename" in dbConnectionParams.keys():
            return dbConnectionParams.get("databasename")
