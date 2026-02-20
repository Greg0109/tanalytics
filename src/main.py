from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import httpx

from src.schemas import UserProfile, Stream, UserResponse, StreamsResponse
from src.twitch_client import twitch_client
from . import logger

app = FastAPI(
    title="Twitch Analytics API",
    description="A backend service to abstract Twitch analytics.",
    version="0.1.0",
)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up
    """
    await twitch_client.close()


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint (provides info about API)
    """
    return {
        "message": "Welcome to the Twitch Analytics API. Visit /docs for API documentation."
    }


@app.get(
    "/analytics/user",
    response_model=UserResponse,
    summary="Get Twitch user information",
    description="Retrieves information about specific Twitch streamer.",
    tags=["analytics"],
)
async def get_twitch_user(
    id: Optional[str] = Query(None, description="Twitch user ID."),
    login: Optional[str] = Query(
        None, description="The login name of the Twitch user."
    ),
):
    if not id and not login:
        raise HTTPException(
            status_code=400, detail="Either 'id' or 'login' parameter must be provided."
        )

    try:
        twitch_data = await twitch_client.get_users(
            user_ids=[id] if id else None, user_logins=[login] if login else None
        )

        if not twitch_data or not twitch_data.get("data"):
            raise HTTPException(status_code=404, detail="Twitch user not found.")

        user_data = twitch_data["data"][0]

        user_profile = UserProfile(**user_data)
        return UserResponse(user=user_profile)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise HTTPException(
                status_code=400,
                detail=f"Twitch API Error: {e.response.json().get('message', 'Bad request')}",
            )
        elif e.response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Authentication error with Twitch API. Check credentials.",
            )
        elif e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Twitch user not found.")
        elif e.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Twitch API rate limit exceeded. Please try again later.",
            )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error when fetching from Twitch: {e}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_twitch_user: {e}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@app.get(
    "/analytics/streams",
    response_model=StreamsResponse,
    summary="Get active Twitch streams",
    description="Retrieves a list of currently active Twitch streams, can be filtered by user.",
    tags=["analytics"],
)
async def get_twitch_streams(
    user_id: Optional[str] = Query(
        None, description="Filter streams by Twitch user ID."
    ),
    user_login: Optional[str] = Query(
        None, description="Filter streams by Twitch username."
    ),
):
    try:
        twitch_data = await twitch_client.get_streams(
            user_ids=[user_id] if user_id else None,
            user_logins=[user_login] if user_login else None,
        )

        streams = [Stream(**stream_data) for stream_data in twitch_data.get("data", [])]
        return StreamsResponse(streams=streams)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in get_twitch_streams: {e}")
        if e.response.status_code == 400:
            raise HTTPException(
                status_code=400,
                detail=f"Twitch API Error: {e.response.json().get('message', 'Bad request')}",
            )
        elif e.response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Authentication error with Twitch API. Check credentials.",
            )
        elif e.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Twitch API rate limit exceeded. Please try again later.",
            )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error when fetching from Twitch: {e}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_twitch_streams: {e}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )
