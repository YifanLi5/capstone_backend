import json

class FolderAsset():
    def __init__(self, asset_url, upload_time, text, category):
        self.upload_time = upload_time
        self.asset_url = asset_url
        self.text = text
        self.category = category
   
       
class FolderAssetJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FolderAsset): 
            return {
                'upload_time' : obj.upload_time,
                'asset_url' : obj.asset_url,
                'text' : obj.text,
                'category' : obj.category
            }
        return json.JSONEncoder.default(self, obj)
