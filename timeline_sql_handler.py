import sqlite3
import json

class TimelineSQLHandler:
    def __init__(self):
        self.conn = sqlite3.connect('timeline.db')

    def insert_assets_from_file(self, json_file_path):
        json_file = open(json_file_path)
        json_data = json.load(json_file)
        timelineArr = json_data["timeline"]

        self.conn.execute('CREATE TABLE IF NOT EXISTS TIMELINE (dateTime TEXT PRIMARY KEY NOT NULL, name TEXT, description TEXT, media TEXT)')
        for entry in timelineArr:
            dateTime = entry["dateTime"]
            cursor = self.conn.execute('SELECT dateTime from TIMELINE where dateTime=?', (dateTime,))
            timelineData = cursor.fetchone()

            if timelineData is None:
                name = entry["name"]
                description = entry["description"]
                media = json.dumps(entry["media"])
                self.conn.execute('INSERT INTO TIMELINE (dateTime, name, description, media) VALUES (?,?,?,?)',
                             (dateTime, name, description, media))
        self.conn.commit()


    def retrieve_timeline(self):
        json_data = {}
        timeline = []
        cursor = self.conn.execute("SELECT dateTime, name, description, media from TIMELINE")
        for row in cursor:
            timeline_entry = {}
            timeline_entry["dateTime"] = row[0]
            timeline_entry["name"] = row[1]
            timeline_entry["description"] = row[2]
            timeline_entry["media"] = json.loads(row[3])

            timeline.append(timeline_entry)

        json_data["timeline"] = timeline

        return json_data

    def exit(self):
        self.conn.close()


