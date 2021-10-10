
import copy
import uuid
import json
from typing import Optional
from bson import json_util


def new_id():
    return str(uuid.uuid4())


class ModelDb:
    # _coll
    _data: dict
    _is_new: bool
    _projection: Optional[dict]

    @property
    def id(self):
        return self._data["id"]

    @property
    def is_new(self):
        return self._is_new

    def __init__(self, coll, data, is_new, projection=None):
        self._coll = coll
        self._data = data
        self._is_new = is_new
        self._projection = projection
    
    def to_dict(self):
        return json.loads(json_util.dumps(self._data))

    @classmethod
    def get_by_id(cls, coll, id):
        ret = coll.find_one({"id": id})
        if ret is not None:
            return cls(coll=coll, data=ret, is_new=False)
        else:
            return None

    @classmethod
    def find(cls, coll, query={}, sort=None, projection=None, skip=None, limit=None) -> list:
        data = coll.find(query, projection=projection)
        if sort is not None:
            data.sort(sort)
        if skip is not None:
            data.skip(skip)
        if limit is not None:
            data.limit(limit)
        poss = []
        for pos_data in data:
            ret = cls(coll=coll, data=pos_data, is_new=False)
            ret._projection = projection
            poss.append(ret)
        return poss

    def duplicate(self):
        other = self.__class__(coll=self._coll, data=copy.deepcopy(self._data), is_new=True)
        other._data["id"] = new_id()
        other._data.pop("_id", None)
        return other

    def update_db(self):
        if self._is_new:
            self._coll.insert_one(self._data)
        else:
            res = self._coll.update_one(
                {"_id": self._data["_id"]},
                {"$set": self._data}
            )
            if res.matched_count != 1:
                raise Exception("No match while updating {} ({})".format(self.__class__.__name__, self._data["id"]))

    def delete_db(self):
        # self.coll.delete_one({"_id": bson.objectid.ObjectId(_id)})
        self._coll.delete_one({"_id": self._data["_id"]})
