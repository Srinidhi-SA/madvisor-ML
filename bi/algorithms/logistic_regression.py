from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression as Logit

from bi.algorithms import utils as MLUtils


class LogisticRegression:
    def __init__(self, data_frame, dataframe_helper, spark):
        # self._spark = spark
        # self.data_frame = data_frame.toPandas()
        # self._measure_columns = dataframe_helper.get_numeric_columns()
        # self._dimension_columns = dataframe_helper.get_string_columns()
        # self.classifier = initiate_forest_classifier(10,5)
        print "LOGSTIC REGRESSION INITIALIZATION DONE"
        self._levels = None

    def set_number_of_levels(self,levels):
        self._levels = levels

    def initiate_logistic_regression_classifier(self):
        if len(self._levels) > 2:
            clf = Logit(multi_class = 'multinomial', solver = 'newton-cg')
        else:
            clf = Logit()
        return clf

    def train_and_predict(self,x_train, x_test, y_train, y_test,clf,drop_cols):
        """
        Output is a dictionary
        y_prob => Array probability values for prediction
        feature_importance => features ranked by their Importance
        feature_Weight => weight of features
        """
        labelEncoder = preprocessing.LabelEncoder()
        labelEncoder.fit(y_train)
        if len(drop_cols) > 0:
            x_train = drop_columns(x_train,drop_cols)
            x_test = drop_columns(x_test,drop_cols)
        y_train = labelEncoder.transform(y_train)
        classes = labelEncoder.classes_
        transformed = labelEncoder.transform(classes)
        labelMapping = dict(zip(transformed,classes))
        clf = clf.fit(x_train, y_train)
        y_score = clf.predict(x_test)
        y_score = labelEncoder.inverse_transform(y_score)
        y_prob = clf.predict_proba(x_test)
        y_prob = [0]*len(y_score)

        feature_importance={}

        return {"trained_model":clf,"actual":y_test,"predicted":y_score,"probability":y_prob,"feature_importance":feature_importance,"featureList":list(x_train.columns),"labelMapping":labelMapping}

    def predict(self,x_test,trained_model,drop_cols):
        """
        """
        if len(drop_cols) > 0:
            x_test = MLUtils.drop_columns(x_test,drop_cols)
        y_score = trained_model.predict(x_test)
        y_prob = trained_model.predict_proba(x_test)
        y_prob = MLUtils.calculate_predicted_probability(y_prob)
        x_test['responded'] = y_score
        return {"predicted_class":y_score,"predicted_probability":y_prob}
