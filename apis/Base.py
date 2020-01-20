from django.conf import settings
import os

# class Meta(type):
#     def __new__(cls,name,bases,dct):
#         cls = type.__new__(cls,name,bases,dct)
#         return cls

class BaseView(object):

    class_name = None
    unique_name = None

    """docstring for BaseView"""
    def __init_subclass__(cls,default_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        
        cls.class_name = cls.__name__
        cls.unique_name = default_name


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.send = {}
        self.send['status']  = 0
        self.send['message'] = "Data not found!"
        self.send['data']    = {}

        self.request = None

        #initialising logging for API's
        self.init_logging()


    def init_logging(self):
        #Create a log path for this file
        from log_controller import Initiate_logging

        log_path = settings.API_LOGGING_ROOT
        os.makedirs(log_path,exist_ok=True)

        #Tracking User Authentication
        report_name = f"{log_path}/{self.class_name}"
        Log = Initiate_logging(report_name,10)
        self.log = Log.Track()


    def required_fields(self,serializer):
        validation_rules = {}
        errors = {}

        for key, value in  serializer.fields.items():
            validation_rules[key] = value.error_messages

        for key, value in serializer.errors.items():
            errors[key] = value[0]

        self.send['errors'] = errors
        #self.send['validation_rules'] = validation_rules


    def Serialize_Method(self,SerializerClass,data,instance=None,many=False,partial=False):

        serializer = SerializerClass(instance=instance,data=data,many=many,partial=partial)

        if serializer.is_valid():
            return (True, serializer)
        return (False, serializer)


    def Send_Response(self,message='Success',status=1,status_code=200):
        #self.send['status_code'] = status_code
        self.send['status']      = status
        self.send['message']     = message

        from rest_framework.response import Response

        return Response(self.send)

