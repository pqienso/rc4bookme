import streamlit as st
from typing import Dict, List
import gspread
import json
from datetime import datetime
import pandas as pd
from uuid import uuid4

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
service_account = gspread.service_account_from_dict(
    st.secrets["service_account"], scopes=scope
)
spreadsheet = service_account.open("RC4MEDB")


def refresh_users():
    st.session_state["db"]["users"] = pd.DataFrame(
        spreadsheet.worksheet("Users").get_all_records()
    ).set_index("email")


def refresh_bookings():
    bookings_df = pd.DataFrame(spreadsheet.worksheet("Bookings").get_all_records())
    bookings_df = bookings_df.set_index("booking_uid", drop=True)
    if len(bookings_df) != 0:
        bookings_df["friend_ids"] = bookings_df["friend_ids"].apply(json.loads).apply(set)
    st.session_state["db"]["bookings"] = bookings_df


def is_registered_user(email: str) -> bool:
    refresh_users()
    is_registered_user = email in st.session_state["db"]["users"].index.values
    return is_registered_user


def get_user_details(email: str) -> Dict[str, str]:
    refresh_users()
    return dict(
        st.session_state["db"]["users"][
            ["tele_handle", "student_id", "name", "phone_number", "user_type"]
        ]
        .rename(
            columns={
                "tele_handle": "tele_handle",
                "student_id": "student_id",
                "user_type": "userType",
                "phone_number": "phone_number",
            }
        )
        .loc[email]
    )


def is_already_registered(student_id: str, tele_handle: str, phone_number: str) -> bool:
    refresh_users()
    student_id = student_id.upper()
    tele_handle = tele_handle.strip("@")
    phone_number = phone_number.replace(" ", "")
    is_already_registered = (
        student_id in st.session_state["db"]["users"]["student_id"].values
        or tele_handle in st.session_state["db"]["users"]["tele_handle"].values
        or phone_number in st.session_state["db"]["users"]["phone_number"].values
    )
    return is_already_registered


def register_student(
    student_id: str,
    tele_handle: str,
    phone_number: str,
    email: str,
    name: str,
    room_number: str,
    grad_year: int,
) -> None:
    sheet = spreadsheet.worksheet("Users")
    row = [
        email,
        name.title(),
        student_id.upper(),
        tele_handle.strip("@"),
        phone_number.replace(" ", ""),
        room_number,
        grad_year,
        "user",
    ]
    sheet.append_row(row)


def time_slot_is_taken(start_time: datetime, end_time: datetime) -> bool:
    refresh_bookings()
    if len(st.session_state["db"]["bookings"]) == 0:
        return False
    start_time = start_time.timestamp() * 1000
    end_time = end_time.timestamp() * 1000
    time_slot_is_taken = (
        len(
            st.session_state["db"]["bookings"].query(
                f"start_unix_ms < {end_time} & end_unix_ms > {start_time} & (status == 'A' | status == 'a')",
            )
        )
        > 0
    )
    return time_slot_is_taken


def add_booking(
    name: str,
    start_ts: datetime,
    end_ts: datetime,
    student_id: str,
    tele_handle: str,
    phone_number: str,
    booking_description: str,
    friend_ids: List[str],
):
    sheet = spreadsheet.worksheet("Bookings")
    row = [
        name,
        datetime.now().isoformat(),
        "P",
        start_ts.date().isoformat(),
        start_ts.time().isoformat(),
        end_ts.date().isoformat(),
        end_ts.time().isoformat(),
        student_id,
        tele_handle,
        str(phone_number),
        booking_description,
        json.dumps(friend_ids),
        start_ts.timestamp() * 1000,
        end_ts.timestamp() * 1000,
        str(uuid4()),
    ]
    sheet.append_row(row)


def get_pending_and_approved_bookings() -> pd.DataFrame:
    refresh_bookings()
    if len(st.session_state["db"]["bookings"]) == 0:
        return pd.DataFrame(
            columns=[
                "student_id",
                "name",
                "status",
                "tele_handle",
                "booking_description",
                "start_unix_ms",
                "end_unix_ms",
                "friend_ids",
            ]
        )
    return st.session_state["db"]["bookings"][
        [
            "student_id",
            "name",
            "status",
            "tele_handle",
            "booking_description",
            "start_unix_ms",
            "end_unix_ms",
            "friend_ids",
        ]
    ].query("(status == 'P' | status == 'A')")


def get_bookings_for_user(student_id: str) -> pd.DataFrame:
    refresh_bookings()
    bookings_df: pd.DataFrame = st.session_state["db"]["bookings"]
    is_relevant_to_user = bookings_df.apply(
        lambda row: row["student_id"] == student_id
        or (student_id in row["friend_ids"] and row["status"] == "A"),
        axis=1,
    )
    if is_relevant_to_user.sum() == 0:
        return pd.DataFrame(
            columns=[
                "name",
                "student_id",
                "start_unix_ms",
                "end_unix_ms",
                "status",
                "booking_description",
            ]
        )
    return bookings_df[is_relevant_to_user][
        [
            "name",
            "student_id",
            "start_unix_ms",
            "end_unix_ms",
            "status",
            "booking_description",
        ]
    ]


def write_to_db(new_df: pd.DataFrame, worksheet_name: str):
    """
    Overwrites the entire sheet! Use with caution.
    """
    bookings_worksheet = spreadsheet.worksheet(worksheet_name)
    bookings_worksheet.update([new_df.columns.values.tolist()] + new_df.values.tolist())


def get_booking_by_uid(uuid: str) -> pd.Series:
    bookings_df: pd.DataFrame = st.session_state["db"]["bookings"]
    booking = bookings_df.loc[uuid,]
    return booking


def edit_booking_timing(uuid: str, new_start: datetime, new_end: datetime):
    refresh_bookings()
    bookings_df: pd.DataFrame = st.session_state["db"]["bookings"].copy()
    try:
        bookings_df.loc[
            uuid,
            [
                "booking_start_date",
                "booking_start_time",
                "booking_end_date",
                "booking_end_time",
                "start_unix_ms",
                "end_unix_ms",
            ],
        ] = (
            new_start.date().isoformat(),
            new_start.time().isoformat(),
            new_end.date().isoformat(),
            new_end.time().isoformat(),
            new_start.timestamp() * 1000,
            new_end.timestamp() * 1000,
        )
        bookings_df["friend_ids"] = (
            bookings_df["friend_ids"].apply(list).apply(json.dumps)
        )
        bookings_df["booking_uid"] = bookings_df.index
        bookings_df = bookings_df.reset_index(drop=True)
        write_to_db(bookings_df, "Bookings")
    except KeyError:
        raise KeyError("Booking not found. Please refresh your calendar")


def delete_booking(uuid: str):
    refresh_bookings()
    bookings_df: pd.DataFrame = st.session_state["db"]["bookings"].copy()
    try:
        bookings_df = bookings_df.drop(index=uuid)
        bookings_df["friend_ids"] = (
            bookings_df["friend_ids"].apply(list).apply(json.dumps)
        )
        bookings_df["booking_uid"] = bookings_df.index
        bookings_df = bookings_df.reset_index(drop=True)
        dummy_row = pd.DataFrame(
            [["" for column in bookings_df.columns]], columns=bookings_df.columns
        )
        bookings_df = pd.concat([bookings_df, dummy_row])
        write_to_db(bookings_df, "Bookings")
    except KeyError:
        raise KeyError("Booking not found. Please refresh your calendar")


def edit_booking_status(uuid: str, status: str):
    refresh_bookings()
    bookings_df: pd.DataFrame = st.session_state["db"]["bookings"].copy()
    try:
        bookings_df.loc[uuid, "status"] = status
        bookings_df["friend_ids"] = (
            bookings_df["friend_ids"].apply(list).apply(json.dumps)
        )
        bookings_df["booking_uid"] = bookings_df.index
        bookings_df = bookings_df.reset_index(drop=True)
        write_to_db(bookings_df, "Bookings")
    except KeyError:
        raise KeyError("Booking not found. Please refresh your calendar")
