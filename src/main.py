"""
Main application and entrypoint.
"""

# import modules
from deta import Deta
from typing import Union
from fastapi import FastAPI, Response, status
from functions import app_info, cache_read, cache_write, tag_info, category_info
import os, datetime, json, semver, typing

# load configuration
from dotenv import load_dotenv

load_dotenv()

# initialise app
app = FastAPI()


# include "pretty" for backwards compatibility
class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        # check if pretty print enabled
        if content["pretty"]:
            del content["pretty"]
            return json.dumps(content, indent=4, sort_keys=True).encode("utf-8")

        else:
            del content["pretty"]
            return json.dumps(content, sort_keys=True).encode("utf-8")


@app.get("/v1/info/{app_id}", response_class=PrettyJSONResponse)
def read_app(app_id: int, pretty: bool = True):
    if "CACHE" in os.environ and os.environ["CACHE"]:
        info = cache_read(app_id)

        if not info:
            print("App info: " + str(app_id) + " could not be find in the cache")
            info = app_info(app_id)
            cache_write(app_id, info)

    else:
        info = app_info(app_id)

    if "apps" not in info:
        # return empty result for not found app
        return {"data": {app_id: {}}, "status": "success", "pretty": pretty}

    return {"data": info["apps"], "status": "success", "pretty": pretty}


@app.get("/v1/version", response_class=PrettyJSONResponse)
def read_item(pretty: bool = True):
    # check if version succesfully read and parsed
    if "VERSION" in os.environ and os.environ["VERSION"]:
        return {
            "status": "success",
            "data": semver.parse(os.environ["VERSION"]),
            "pretty": pretty,
        }
    else:
        return {
            "status": "error",
            "data": "Something went wrong while retrieving and parsing the current API version. Please try again later",
            "pretty": pretty,
        }

@app.get("v1/tags/{tag_ids}", response_class=PrettyJSONResponse)
def read_tags(tag_ids: str, pretty: bool = False):
    # fetch tag information from steam api

    # split tag ids
    tag_ids = tag_ids.split(",")

    # get tag_info or return api-formatted error
    try:
        tag_info = tag_info(tag_ids)
    except Exception as err:
        print("Error while fetching tag info for tag ids: " + ",".join(tag_ids))
        print(err)
        return {"data": {}, "status": "error", "pretty": pretty}
    
    # return tags
    return {"data": tag_info, "status": "success", "pretty": pretty}

@app.get("v1/categories/{category_ids}", response_class=PrettyJSONResponse)
def read_categories(category_ids: str, pretty: bool = False):
    # fetch category information from steam api

    # split category ids
    category_ids = category_ids.split(",")

    # get category_info or return api-formatted error
    try:
        category_info = category_info(category_ids)
    except Exception as err:
        print("Error while fetching category info for category ids: " + ",".join(category_ids))
        print(err)
        return {"data": {}, "status": "error", "pretty": pretty}
    
    # return categories
    return {"data": category_info, "status": "success", "pretty": pretty}