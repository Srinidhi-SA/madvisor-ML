from pyspark import RDD
from pyspark.sql import Row
from pyspark.sql import SparkSession
from pyspark.sql import types as pst

from decorators import accepts
from writemode import WriteMode

'''
Ref: http://nadbordrozd.github.io/blog/2016/05/22/one-weird-trick-that-will-fix-your-pyspark-schemas/

Multilevel JSON persitence fails with existing DataFrame RDD apis, so borrowed implementation from above reference
'''
class DataWriter:

    @staticmethod
    @accepts(SparkSession, dict, basestring, write_mode=type(WriteMode.OVERWRITE))
    def write_dict_as_json(spark, data, target_file, write_mode=WriteMode.OVERWRITE):
        """
        TODO: 1) failing on dict with non-string keys
        TODO: 2) failing on list with elements of different data type
        """
        rdd_rows = spark.sparkContext.parallelize([data])
        result_df = DataWriter.df_from_rdd(rdd_rows, data, spark)
        result_df.write.json(target_file, mode=write_mode)

    # @staticmethod
    # @accepts(SparkSession, basestring, basestring, write_mode=type(WriteMode.OVERWRITE))
    # def write_pickle_as_text(spark, data, target_file, write_mode=WriteMode.OVERWRITE):
    #     """
    #     """
    #     print target_file
    #     try:
    #         subprocess.call(["hadoop", "fs", "-rm", "-r", target_file])
    #         rdd_rows = spark.sparkContext.parallelize([data])
    #         rdd_rows.saveAsPickleFile(target_file)
    #     except:
    #         print "Can Not Delete"

    @staticmethod
    def infer_schema(rec):
        """infers dataframe schema for a record. Assumes every dict is a Struct, not a Map"""
        if isinstance(rec, dict):
            return pst.StructType([pst.StructField(key, DataWriter.infer_schema(value), True)
                                   for key, value in sorted(rec.items())])
        elif isinstance(rec, list):
            if len(rec) == 0:
                #raise ValueError("can't infer type of an empty list")
                return pst.ArrayType(pst.NullType())
            elem_type = DataWriter.infer_schema(rec[0])
            for elem in rec:
                this_type = DataWriter.infer_schema(elem)
                if elem_type != this_type:
                    raise ValueError("can't infer type of a list with inconsistent elem types")
            return pst.ArrayType(elem_type)
        else:
            return pst._infer_type(rec)

    @staticmethod
    def _rowify(x, prototype):
        """creates a Row object conforming to a schema as specified by a dict"""

        def _equivalent_types(x, y):
            if type(x) in [str, unicode] and type(y) in [str, unicode]:
                return True
            return isinstance(x, type(y)) or isinstance(y, type(x))

        if x is None:
            return None
        elif isinstance(prototype, dict):
            if type(x) != dict:
                raise ValueError("expected dict, got %s instead" % type(x))
            rowified_dict = {}
            for key, val in x.items():
                if key not in prototype:
                    raise ValueError("got unexpected field %s" % key)
                rowified_dict[key] = DataWriter._rowify(val, prototype[key])
                for _ptype in prototype:
                    if key not in x:
                        raise ValueError(
                            "expected %s field but didn't find it" % _ptype)

            return Row(**rowified_dict)
        elif isinstance(prototype, list):
            if type(x) != list:
                raise ValueError("expected list, got %s instead" % type(x))
            return [DataWriter._rowify(e, prototype[0]) for e in x]
        else:
            if not _equivalent_types(x, prototype):
                raise ValueError("expected %s, got %s instead" %
                                 (type(prototype), type(x)))
            return x


    @staticmethod
    @accepts(RDD, dict, SparkSession)
    def df_from_rdd(rdd, prototype, sql):
        """creates a dataframe out of an rdd of dicts, with schema inferred from a prototype record"""
        schema = DataWriter.infer_schema(prototype)
        row_rdd = rdd.map(lambda x: DataWriter._rowify(x, prototype))
        return sql.createDataFrame(row_rdd, schema)
