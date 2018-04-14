import json

class TimelineAsset():
    def __init__(self, dateTime, name, description, filetypes, links):
        if(len(filetypes) == len(links)):
            self.dateTime = dateTime
            self.name = name
            self.description = description
            self.media = []
            for idx, type in enumerate(filetypes):
                self.media.append(Media(type, links[idx]))


class Media():
    def __init__(self, filetype, s3_image_url):
        self.filetype = filetype
        self.s3_image_url = s3_image_url

class TimelineAssetJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TimelineAsset):
            return {
                'dateTime' : obj.dateTime,
                'name' : obj.name,
                'description' : obj.description,
                'media' : [
                    obj.media
                ]
            }
        return json.JSONEncoder.default(self, obj)

class MediaJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Media):
            return {
                'type' : obj.filetype,
                'link' : obj.s3_image_url
            }
        return json.JSONEncoder.default(self, obj)