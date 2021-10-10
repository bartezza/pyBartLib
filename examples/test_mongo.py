
from dotenv import load_dotenv
from argparse import ArgumentParser
from bartlib.db import MongoDb


if __name__ == "__main__":
    parser = ArgumentParser(description="test_mongo")
    parser.add_argument("-e", "--env", dest="env", action="store", default="../my.env", help="Env file")
    parser.add_argument("-c", "--coll", dest="coll", action="store", default="pubmed", help="Collection")
    args = parser.parse_args()

    load_dotenv(args.env)

    mongo = MongoDb(config=None)
    db = mongo.db

    coll = db[args.coll]

    print("Records =", coll.estimated_document_count())
