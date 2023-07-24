from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from fastapi import APIRouter
import Service
import re
import csv
import os
import json
import urllib.request as request
from typing import Optional

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()
