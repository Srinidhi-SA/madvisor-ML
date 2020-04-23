import pandas as pd
from sklearn.svm import SVC
from sklearn import preprocessing

from bi.algorithms import utils as MLUtils
from bi.common import utils as CommonUtils


class SupportVectorMachine:
    def __init__(self, data_frame, dataframe_helper, spark):
        # self._spark = spark
        # self.data_frame = data_frame.toPandas()
        # self._measure_columns = dataframe_helper.get_numeric_columns()
        # self._dimension_columns = dataframe_helper.get_string_columns()
        # self.classifier = initiate_forest_classifier(10,5)
        print "SVM INITIALIZATION DONE"

    def initiate_svm_classifier(self,n_estimators,max_features):
        clf = SVC(kernel='linear',probability=True)
        return clf

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

    def train_and_predict(self,x_train, x_test, y_train, y_test,clf,plot_flag,print_flag,drop_cols):
        """
        Output is a dictionary
        y_prob => Array probability values for prediction
        results => Array of predicted class
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
        print "starting svm model fit"
        import time
        st = time.time()
        clf = clf.fit(x_train, y_train)
        print "time for fit",time.time()-st
        print "svm model fit completed"
        print "#"*40
        y_score = clf.predict(x_test)
        y_score = labelEncoder.inverse_transform(y_score)
        y_prob = clf.predict_proba(x_test)
        results = pd.DataFrame({"actual":y_test,"predicted":y_score,"prob":list(y_prob)})

        feature_importance = None
        # feature_importance = dict(sorted(zip(x_train.columns,clf.feature_importances_),key=lambda x: x[1],reverse=True))
        # for k, v in feature_importance.iteritems():
        #     feature_importance[k] = CommonUtils.round_sig(v)

        return {"trained_model":clf,"actual":y_test,"predicted":y_score,"probability":y_prob,"feature_importance":feature_importance,"featureList":list(x_train.columns),"labelMapping":labelMapping}
