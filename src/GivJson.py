# version 1.0
import json
from GivTCP import GivTCP

class GivJSON():
    def output_JSON(array):
        json_object = json.dumps(array, indent = 4)  
        print(json_object)
        GivTCP.debug("JSON output: "+ json_object)