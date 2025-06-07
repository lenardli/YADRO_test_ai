import datetime
import os
from datetime import timedelta, datetime
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBasicCredentials
from werkzeug.security import generate_password_hash

from database.common.models import db, URL, User, Visit
from database.core import crud, create_tables, close_db
from schemas.user_schema import SUserRegister
from utils.check_creds import get_current_username
from utils.check_exp_link import check_row
from utils.gen_random_url import random_alphanumeric_string

load_dotenv()
url_len = int(os.getenv("URL_LEN"))

app = FastAPI(title="URL Alias Service",
              description="Сервис для сокращения URL-адресов",
              version="1.0.0")


@app.get("/url")
async def create_new_url(credentials: Annotated[HTTPBasicCredentials,
                         Depends(get_current_username)], url: Request):
    short_code = random_alphanumeric_string(url_len)
    data = await url.json()
    crud.create()(db, URL,
                  {'original_url': data['url'], 'short_code': short_code})
    return f"{url.base_url}{short_code}"


@app.get("/urls")
def get_all_links(credentials: Annotated[HTTPBasicCredentials,
                  Depends(get_current_username)],
                  page: int = Query(1, ge=1),
                  per_page: int = Query(10, ge=1, le=100)):
    query = crud.retrieve_all()(db, URL)
    total = query.count()
    urls = query.paginate(page, per_page)
    results = [{
        "short_code": url.short_code,
        "original_url": url.original_url,
        "expired_at": url.expired_at,
        "is_active": url.is_active
    } for url in sorted(urls, key=lambda x: x.is_active, reverse=True)]

    return JSONResponse({
        "data": results,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    })


@app.get("/stats")
def get_stats(credentials: Annotated[HTTPBasicCredentials,
              Depends(get_current_username)]):
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)
    visits = crud.retrieve_all()(db, Visit)
    visits = [vars(i)['__data__'] for i in visits]
    res_dict = {}
    for i in visits:
        if not (i['original_url'], i['short_url']) in res_dict:
            res_dict[(i['original_url'], i['short_url'])] = {
                'last_hour_clicks': 0, 'last_day_clicks': 0}
        if i['created_at'] >= one_day_ago:
            res_dict[(i['original_url'], i['short_url'])][
                'last_day_clicks'] += 1
            if i['created_at'] >= one_hour_ago:
                res_dict[(i['original_url'], i['short_url'])][
                    'last_hour_clicks'] += 1
    return JSONResponse([{"link": i[0][1], "original_link": i[0][0],
                          'last_hour_clicks': i[1]['last_hour_clicks'],
                          'last_day_clicks': i[1]['last_day_clicks']} for i in
                         res_dict.items()])


@app.put("/deactivate_url")
async def deactivate_url(credentials: Annotated[HTTPBasicCredentials,
                         Depends(get_current_username)],
                         short_url: Request):
    data = await short_url.json()
    short_code = data['url'][-1 * url_len:]
    crud.update_data()(db, URL, "is_active", False, "short_code", short_code)
    return f"url={data['url']} successfully deactivated"


@app.post("/register")
def register(credentials: SUserRegister):
    if crud.check_exists()(db, User, "username", credentials.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    try:
        user_id = crud.create()(db, User, {"username": credentials.username,
                                           "hashed_password":
                                               generate_password_hash(
                                                   credentials.password)})
        return {"message": "User created", "user_id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/{short_code}")
async def redirect_to_orig_url(short_code, request: Request):
    try:
        if check_row(short_code):
            row = crud.retrieve_single()(db, URL, "short_code", short_code)
            url = row[0].original_url
            crud.create()(db, Visit, {"short_url": f"{request.base_url}"
                                                   f"{short_code}",
                                      "original_url": url})
        else:
            raise HTTPException(status_code=403,
                                detail=f"Link has expired")
    except IndexError:
        raise HTTPException(status_code=404,
                            detail=f"Not found url for {short_code=}")
    return RedirectResponse(url=url)


@app.on_event("startup")
def startup():
    create_tables()


@app.on_event("shutdown")
def shutdown():
    close_db()
