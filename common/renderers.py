import json
from rest_framework import renderers

class ApiCustomRenderer(renderers.JSONRenderer):
    charset = "utf-8"
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = str()
        
        # import pdb
        # pdb.set_trace()
        if "ErrorDetail" in str(data) or "error" in str(data) or "detail" in str(data) or data.get("status_code") == 404:
            response = json.dumps({"errors": data, "status_code": 400})
     
        else:
            response = json.dumps({"data": data, "status_code": 200}) 
            
        return response