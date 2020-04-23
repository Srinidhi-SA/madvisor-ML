from bi.common.decorators import accepts
import numpy as np


class AlgorithmParameters:

    def __init__(self):
        self.name = None
        self.description = None
        self.displayName = None
        self.paramType = None
        self.defaultValue = None
        self.acceptedValue = None
        self.valueRange = None
        self.uiElemType = None
        self.diplay = None
        self.hyperpatameterTuningCandidate = None
        self.expectedDataType = None
        self.allowedDataType = None


    def set_params(self,algoParamObj):
        if "name" in algoParamObj:
            self.name = algoParamObj["name"]
        if "description" in algoParamObj:
            self.description = algoParamObj["description"]
        if "displayName" in algoParamObj:
            self.displayName = algoParamObj["displayName"]
        if "paramType" in algoParamObj:
            self.paramType = algoParamObj["paramType"]
        if "valueRange" in algoParamObj:
            self.valueRange = algoParamObj["valueRange"]
        if "uiElemType" in algoParamObj:
            self.uiElemType = algoParamObj["uiElemType"]
        if "diplay" in algoParamObj:
            self.diplay = algoParamObj["diplay"]
        if "hyperpatameterTuningCandidate" in algoParamObj:
            self.hyperpatameterTuningCandidate = algoParamObj["hyperpatameterTuningCandidate"]
        if "expectedDataType" in algoParamObj:
            self.expectedDataType = algoParamObj["expectedDataType"]
        if "allowedDataType" in algoParamObj:
            self.allowedDataType = algoParamObj["allowedDataType"]
        if "acceptedValue" in algoParamObj:
            self.acceptedValue = algoParamObj["acceptedValue"]
        ### Should be the last key
        if "defaultValue" in algoParamObj:
            self.defaultValue = algoParamObj["defaultValue"]

    def get_name(self):
        return self.name
    def get_param_type(self):
        return self.paramType
    def get_uielem_type(self):
        return self.uiElemType
    def get_value_range(self):
        return self.valueRange
    def check_for_tuning(self):
        return self.hyperpatameterTuningCandidate
    def get_accepted_value(self):
        return self.acceptedValue
    def get_expected_datatype(self):
        return self.expectedDataType

    def handle_boolean(self,dictObj):
        newArray = []
        for k,v in dictObj.items():
            if isinstance(v,list):
                vNew = []
                for val in v:
                    if str(val).lower() in ["true","false"]:
                        if str(val).lower() == "true":
                            vNew.append(True)
                        else:
                            vNew.append(False)
                    else:
                        vNew.append(val)
                newArray.append((k,vNew))
            elif isinstance(v,str):
                if str(v).lower() in ["true","false"]:
                    if str(v).lower() == "true":
                        vNew = True
                    else:
                        vNew = False
                    newArray.append((k,vNew))
                else:
                    newArray.append((k,v))
            else:
                newArray.append((k,v))
        return dict(newArray)




    def get_default_value(self,tuningParams=True):
        if type(self.defaultValue) == list:
            filteredArr = [x["name"] for x in filter(lambda x:x["selected"] == True,self.defaultValue)]
            outArray = []
            if len(filteredArr) > 0:
                for filteredVal in filteredArr:
                    if isinstance(filteredVal,str):
                        if filteredVal.lower() not in ["true","false"]:
                            outArray.append(filteredVal)
                        else:
                            if filteredVal.lower() == "true":
                                outArray.append(True)
                            else:
                                outArray.append(False)
                    else:
                        outArray.append(filteredVal)
            outArrayNew = []
            for val in outArray:
                if str(val).lower() in ["true","false"]:
                    if str(val).lower() == "true":
                        outArrayNew.append(True)
                    else:
                        outArrayNew.append(False)
                else:
                    outArrayNew.append(val)
            outArray = outArrayNew
            if len(outArray) == 0:
                print "SOMETHING FISHY IN",self.name
                return None
            else:

                if tuningParams == False:
                    return outArray[0]
                else:
                    return outArray
        else:
            if self.defaultValue != None:
                return self.defaultValue
            else:
                return self.defaultValue

    def hyperParameterInputParser(self,stringObj):
        print stringObj
        out = []
        blocks =  stringObj.split(",")
        for val in blocks:
            subBlocks = val.split("-")
            if len(subBlocks) == 1:
                if "." in subBlocks[0]:
                    out += [float(subBlocks[0])]
                else:
                    out += [int(subBlocks[0])]
            elif len(subBlocks) == 2:
                startVal = subBlocks[0]
                endVal = subBlocks[1]
                startValPrecision,endValPrecision = 0,0
                floatType = False
                if "." in startVal:
                    floatType = True
                    startValPrecision = len(startVal.split(".")[1])
                if "." in endVal:
                    floatType = True
                    endValPrecision = len(endVal.split(".")[1])
                precision = max(endValPrecision,startValPrecision)
                if startVal == endVal:
                    if precision > 0:
                        valRange = [float(startVal)]
                    else:
                        valRange = [int(startVal)]
                else:
                    if precision > 0:
                        valRange = list(np.arange(float(startVal),float(endVal),1.0/(10**precision)))
                        valRange = [round(x,precision) for x in valRange]
                        valRange.append(float(endVal))
                    else:
                        valRange = range(int(startVal),int(endVal))
                        valRange.append(int(endVal))
                out += valRange
        print out
        return out


    def get_param_value(self,hyperParams=True):
        output = None
        defaultValue = self.get_default_value(tuningParams=hyperParams)
        if hyperParams == True:
            if self.hyperpatameterTuningCandidate != True:
                if self.acceptedValue != None:
                    if self.name != "tol":
                        output = {self.name:self.acceptedValue}
                    else:
                        output = {self.name:1.0/10**self.acceptedValue}
                else:
                    if self.name != "tol":
                        output = {self.name:defaultValue}
                    else:
                        output = {self.name:1.0/10**defaultValue}
            else:
                if self.paramType != "list":
                    if self.acceptedValue != None:
                        outRange = self.hyperParameterInputParser(str(self.acceptedValue))
                    else:
                        outRange = [defaultValue]
                    if self.name != "tol":
                        output = {self.name:outRange}
                    else:
                        output = {self.name:[1.0/10**x for x in outRange]}
                else:
                    output = {self.name:defaultValue}
        else:
            if self.acceptedValue != None:
                if self.expectedDataType != None:
                    if "float" in self.expectedDataType:
                        self.acceptedValue = float(self.acceptedValue)
                    elif "int" in self.expectedDataType:
                        self.acceptedValue = int(self.acceptedValue)
                if self.name != "tol":
                    output = {self.name:self.acceptedValue}
                else:
                    output = {self.name:1.0/10**self.acceptedValue}
            else:
                if self.expectedDataType != None:
                    if defaultValue != None:
                        if "float" in self.expectedDataType:
                            self.acceptedValue = float(defaultValue)
                        elif "int" in self.expectedDataType:
                            self.acceptedValue = int(defaultValue)
                if self.name != "tol":
                    output = {self.name:defaultValue}
                else:
                    output = {self.name:1.0/10**defaultValue}
        return self.handle_boolean(output)



class HyperParameterSetting:
    def __init__(self):
        self.selected = None
        self.name = None
        self.displayName = None
        self.params = []
    def set_params(self,hyperParameterObj):
        if "name" in hyperParameterObj:
            self.name = hyperParameterObj["name"]
        if "selected" in hyperParameterObj:
            self.selected = hyperParameterObj["selected"]
        if "displayName" in hyperParameterObj:
            self.displayName = hyperParameterObj["displayName"]
        if "params" in hyperParameterObj:
            paramsArr = hyperParameterObj["params"]
            outArray = []
            if paramsArr != None:
                for paramObj in paramsArr:
                    algoParamsInstance = AlgorithmParameters()
                    algoParamsInstance.set_params(paramObj)
                    outArray.append(algoParamsInstance)
                self.params = outArray

    def get_name(self):
        return self.name
    def is_selected(self):
        return self.selected
    def get_params(self):
        return self.params
    def is_tuning_enabled(self):
        truthTuple = (self.is_selected(),len(self.get_params()) > 0)
        return (truthTuple[0] & truthTuple[1])



class AlgorithmParameterConfig:
    def __init__(self):
        self.description = None
        self.selected = None
        self.algorithmSlug = None
        self.algorithmName = None
        self.hyperParameterSetting = []
        self.parameters = []
        self.hyperParamsArray = []

    def set_params(self,algoParamObj):
        if "description" in algoParamObj:
            self.description = algoParamObj["description"]
        if "selected" in algoParamObj:
            self.selected = algoParamObj["selected"]
        if "algorithmSlug" in algoParamObj:
            self.algorithmSlug = algoParamObj["algorithmSlug"]
        if "algorithmName" in algoParamObj:
            self.algorithmName = algoParamObj["algorithmName"]
        if "hyperParameterSetting" in algoParamObj:
            hyperSettingArr = []
            hyperParamArray = algoParamObj["hyperParameterSetting"]
            for hyperParamObj in hyperParamArray:
                hyperParameterSettingInstance = HyperParameterSetting()
                hyperParameterSettingInstance.set_params(hyperParamObj)
                hyperSettingArr.append(hyperParameterSettingInstance)
            self.hyperParameterSetting = hyperSettingArr

        if "parameters" in algoParamObj:
            paramArr = []
            paramArrInput = algoParamObj["parameters"]
            for paramObj in paramArrInput:
                algoParamsInstance = AlgorithmParameters()
                algoParamsInstance.set_params(paramObj)
                paramArr.append(algoParamsInstance)
            self.parameters = paramArr

    def is_selected(self):
        return self.selected

    def get_algorithm_name(self):
        return self.algorithmName

    def get_algorithm_slug(self):
        return self.algorithmSlug

    def is_hyperparameter_tuning_enabled(self):
        hyperCheckArr = [obj.is_tuning_enabled() for obj in self.hyperParameterSetting]
        if True in hyperCheckArr:
            return True
        else:
            return False

    def get_hyperparameter_params(self):
        """
        give hyperparameter algorithm parameters
        """
        hyperParamsObj = [obj for obj in self.hyperParameterSetting if obj.is_tuning_enabled() == True][0]
        hyperParamsArray = hyperParamsObj.get_params()
        params_dict = {}
        for obj in hyperParamsArray:
            params_dict.update(obj.get_param_value(hyperParams=False))
        return params_dict

    def get_hyperparameter_algo_name(self):
        hyperParamsObj = [obj for obj in self.hyperParameterSetting if obj.is_tuning_enabled() == True][0]
        hyperParamsArray = hyperParamsObj.get_params()
        return hyperParamsObj.get_name()

    def get_params_dict(self):
        """
        give algorithm parameters when there is no tuning
        """
        params_dict = {}
        for obj in self.parameters:
            params_dict.update(obj.get_param_value(hyperParams=False))
        return params_dict

    def get_params_dict_hyperparameter(self):
        """
        give algorithm parameters when there is tuning
        """
        params_dict = {}
        for obj in self.parameters:
            if obj.check_for_tuning():
                params_dict.update(obj.get_param_value())
        return params_dict
