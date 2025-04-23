import eaia.async_patch  # Apply patches early
import sys
sys.path.insert(0, "./eaia")  # Ensure local imports are prioritized
import os
from dotenv import load_dotenv
load_dotenv()

import argparse
import asyncio
from typing import Optional
from bs4 import BeautifulSoup
from eaia.gmail import fetch_group_emails
from eaia.main.config import get_config
from langgraph_sdk import get_client
import httpx
import uuid
import hashlib


async def main(
    url: Optional[str] = None,
    minutes_since: int = 60,
    gmail_token: Optional[str] = None,
    gmail_secret: Optional[str] = None,
    early: bool = True,
    rerun: bool = False,
    email: Optional[str] = None,
):
    if email is None:
        config = {"configurable": {}}
        email_address = get_config(config)["email"]
    else:
        email_address = email
    if url is None:
        client = get_client(url="http://127.0.0.1:2024")
    else:
        client = get_client(
            url=url
        )

    # TODO: This really should be async
    for email in fetch_group_emails(
        email_address,
        minutes_since=minutes_since,
        gmail_token=gmail_token,
        gmail_secret=gmail_secret,
    ):
        print("--- Processing Email --- ")
        print(f"From: {email.get('from_email', 'N/A')}")
        print(f"To: {email.get('to_email', 'N/A')}")
        print(f"Subject: {email.get('subject', 'N/A')}")
        print(f"Sent: {email.get('send_time', 'N/A')}")
        page_content = email.get('page_content', '')
        if page_content:
            soup = BeautifulSoup(page_content, 'lxml')
            text_content = soup.get_text(separator=' ', strip=True)
        else:
            text_content = ""
        print(f"Content:\n{text_content[:1000]}...") # Print first 1000 chars of parsed text content
        print("-------------------------")

        thread_id = str(
            uuid.UUID(hex=hashlib.md5(email["thread_id"].encode("UTF-8")).hexdigest())
        )
        try:
            thread_info = await client.threads.get(thread_id)
        except httpx.HTTPStatusError as e:
            if "user_respond" in email:
                continue
            if e.response.status_code == 404:
                thread_info = await client.threads.create(thread_id=thread_id)
            else:
                raise e
        if "user_respond" in email:
            await client.threads.update_state(thread_id, None, as_node="__end__")
            continue
        recent_email = thread_info["metadata"].get("email_id")
        if recent_email == email["id"]:
            if early:
                break
            else:
                if rerun:
                    pass
                else:
                    continue
        await client.threads.update(thread_id, metadata={"email_id": email["id"]})

        await client.runs.create(
            thread_id,
            "main",
            input={"email": email},
            multitask_strategy="rollback",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL to run against",
    )
    parser.add_argument(
        "--early",
        type=int,
        default=1,
        help="whether to break when encountering seen emails",
    )
    parser.add_argument(
        "--rerun",
        type=int,
        default=0,
        help="whether to rerun all emails",
    )
    parser.add_argument(
        "--minutes-since",
        type=int,
        default=60,
        help="Only process emails that are less than this many minutes old.",
    )
    parser.add_argument(
        "--gmail-token",
        type=str,
        default=None,
        help="The token to use in communicating with the Gmail API.",
    )
    parser.add_argument(
        "--gmail-secret",
        type=str,
        default=None,
        help="The creds to use in communicating with the Gmail API.",
    )
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="The email address to use",
    )

    args = parser.parse_args()
    asyncio.run(
        main(
            url=args.url,
            minutes_since=args.minutes_since,
            gmail_token=args.gmail_token,
            gmail_secret=args.gmail_secret,
            early=bool(args.early),
            rerun=bool(args.rerun),
            email=args.email,
        )
    )
