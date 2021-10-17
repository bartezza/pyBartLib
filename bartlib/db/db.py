
import os
import pymongo
from typing import Optional
from ..utils import dump_exception


class MongoDb:
    client: pymongo.MongoClient
    url: str
    config: Optional[dict]
    db: pymongo.database.Database

    def __init__(self, config: Optional[dict] = None, url: Optional[str] = None):
        if url is None:
            if config is None:
                config = {
                    "host": os.environ.get("MONGO_HOST", "127.0.0.1"),
                    "username": os.environ.get("MONGO_USERNAME"),
                    "password": os.environ.get("MONGO_PASSWORD"),
                    "db_name": os.environ.get("MONGO_DB_NAME", "db")
                }
            
            if "host" not in config:
                raise Exception("Mongo hostname not set (it can be set in MONGO_HOST env var)")
            if "db_name" not in config:
                raise Exception("Mongo DB name not set (it can be set in MONGO_DB_NAME env var)")

            if config["username"] and config["password"]:
                url = "mongodb://{}:{}@{}/{}".format(config["username"], config["password"],
                                                     config["host"], config["db_name"])
            else:
                url = "mongodb://{}/{}".format(config["host"], config["db_name"])
            # print(url)

        self.client = pymongo.MongoClient(url)
        try:
            self.client.server_info()
        except pymongo.errors.OperationFailure as exc:
            dump_exception()
            if config["username"] and config["password"]:
                url2 = "mongodb://{}@{}/{}".format(config["username"], config["host"],
                                                   config["db_name"])
            else:
                url2 = url
            raise Exception(f"Could not connect to mongo at {url2}") from exc

        self.url = url
        self.config = config
        self.db = self.client[config["db_name"]]

    def get_coll(self, name):
        return self.db[name]

    def get_url(self):
        return self.url
