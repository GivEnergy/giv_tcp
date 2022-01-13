# version 1.0
import json
import logging

class GivJSON():
    
    def output_JSON(array):
        json_object = json.dumps(array, indent = 4)  
        print(json_object)
        logging.info("JSON output: "+ json_object)