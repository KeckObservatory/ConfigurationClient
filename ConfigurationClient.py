
# imports
from pymongo import MongoClient
from pprint import pprint
import os
import pandas as pd
from bson.objectid import ObjectId
import numpy as np

try:
    import ktl
    useKTL = True
except:
    print("WARNING: KTL functions are not available")
    useKTL = False

# establish connection with configuration database
# first you need: ssh keola@observinglogs -L 27017:localhost:27017
client = MongoClient('localhost')


class Instrument():
    def __init__(self):
        pass
        #print("Instrument class is ready")
        
    # KTL decorator: This decorator returns the original method of the super class if KTL
    # is not defined
    @classmethod
    def ktl_decorator(cls, func):
        if useKTL:
            return func
        else:
            #print("%s(%s): KTL is not available, using super method" %
            #      (cls.__name__,func.__name__))
            return getattr(cls, func.__name__)
                
    def get_outdir(self):
        """
        Return the current working directory. 
        Individual child classes can override to use outdir
        """
        return(os.getcwd())

    def sort_dataframe_columns(self, dataframe):
        current_columns = list(dataframe.columns.values)
        current_columns.remove('_id')
        if 'semester' in current_columns:
            current_columns.remove('semester')
        current_columns.remove('progname')
        current_columns.remove('statenam')

        new_columns = ['semester', 'progname', 'statenam']
        for column in current_columns:
            new_columns.append(column)
        dataframe = dataframe[new_columns]
        return dataframe

    def get_all_configs(self, semester=None, progname=None):
        configurations = []
        if semester and progname:
            confs = self.db.Configurations.find({'semester': semester, 'progname': progname})
        elif semester:
            confs = self.db.Configurations.find({'semester': semester})
        elif progname:
            confs = self.db.Configurations.find({'progname': progname})
        else:
            confs = self.db.Configurations.find()
        configurations = list(confs)
        converted_configurations = []
        for config in configurations:
            converted_configurations.append(config)

        dataframe = pd.DataFrame(converted_configurations).replace(np.nan, '', regex=True)
        print(self.sort_dataframe_columns(dataframe))

    def get_all_projects(self, semester=None):
        projects_list = []
        if semester is None:
            projects = self.db.Configurations.find({},{'progname':1})
        else:
            projects = self.db.Configurations.find({'semester': semester}, {'progname':1})
        for project in projects:
            try:
                projects_list.append(project['progname'])
            except:
                pass
        print(set(projects_list))
        
    def get_config(self, semester=None, progname=None, statenam=None):
        config = self.db.Configurations.find(
            {'semester':semester, 
             'progname': progname,
             'statenam': statenam})
        output_config=[]
        for conf in config:
            output_config = conf
            pprint(conf)
        if output_config:
            return(output_config)
        else:
            return([])

        
    def convert_configuration(self, configuration):
        configurationDetail={}
        if not self.elements:
            print("The conversion table is not defined")
            return
        for key in self.elements.keys():
            state_keyword = self.elements[key][0]
            mongo_keyword = self.elements[key][1]
            required = self.elements[key][2]
            if required:
                try:
                    configurationDetail[state_keyword] = configuration[mongo_keyword]
                except Exception as e:
                    raise KeyError("Missing keyword %s" % (e))

            else:
                try:
                    configurationDetail[state_keyword] = configuration[mongo_keyword]
                except:
                    configurationDetail[state_keyword]=""
        configurationDetail['id']=str(configuration['_id'])
        return configurationDetail
    
    def get_state_file(self, semester=None, progname=None, statenam=None):
        config = list(self.db.Configurations.find(
            {'semester':semester, 
             'progname': progname,
             'statenam': statenam}))

        if len(list(config)) == 0:
            print("No results returned")
            return
        if len(list(config)) > 1:
            print("More than one configuration meet the search criteria")
            for conf in config:
                print(conf)
            return
        else:
            translated_config = self.convert_configuration(config[0])

        print("STATE FILE: \n")
        if translated_config:
            for key in translated_config:
                if translated_config[key]:
                    print("%s = %s" % (key, translated_config[key]))
    

class LRIS(Instrument):
    def __init__(self):
        self.db = client.LRIS
        self.set_conversion_elements()
        super(LRIS, self).__init__()
    
    @Instrument.ktl_decorator
    def get_outdir(self):
        lris = ktl.cache('lris')
        outdir = lris['outdir'].read()
        return(outdir)
    
    def set_conversion_elements(self):
        self.elements = {
            '1': ['statenam', 'statenam', False],
            '2': ['GRISNAME', 'bluegrism', False],
            '3': ['DICHNAME', 'dichroic', False],
            '4': ['BLUFILT', 'filter', False],
            '5': ['GRANAME', 'redgrism', False],
            '6': ['SLITNAME', 'slitmask', False],
            '7': ['PROGNAME', 'progname', False]
            }
    

class MOSFIRE(Instrument):
    def __init__(self):
        self.db = client.MOSFIRE
        super(MOSFIRE, self).__init__()
        
    @Instrument.ktl_decorator
    def get_outdir(self):
        mosfire = ktl.cache('mosfire')
        outdir = mosfire['outdir'].read()
        return(outdir)
    
class KCWI(Instrument):
    def __init__(self):
        self.db = client.KCWI
        self.set_conversion_elements()
        super(KCWI, self).__init__()
        
    def set_conversion_elements(self):
        self.elements = {
            '1': ['statenam','statenam',True],
            '2': ['image_slicer','image_slicer',False],
            '3': ['filterb','filterb',False],
            '4': ['gratingb','gratingb',False],
            '5': ['nsmaskb','nsmaskb',False],
            '6': ['ampmodeb','ampmodeb',False],
            '7': ['gainmulb','gainmulb',False],
            '8': ['ccdmodeb','ccdmodeb',False],
            '9': ['binningb','binningb',False],
            '10':['cal_mirror','cal_mirror',False],
            '11':['polarizer','polarizer',False],
            '12':['cwaveb','cwaveb',False],
            '13':['pwaveb','pwaveb',False],
            '14':['progname','progname',False],
            '15':['camangleb','camangleb',False],
            '16':['focusb','focusb',False]
            }
        

    @Instrument.ktl_decorator
    def get_outdir(self):
        kbds = ktl.cache('lbds')
        outdir = kbds['outdir'].read()
        return(outdir)

def get_instrument_class(instrument):
    if instrument == 'LRIS':
        myclass = LRIS()
    if instrument == 'MOSFIRE':
        myclass = MOSFIRE()
    if instrument == 'KCWI':
        myclass = KCWI()
    return myclass