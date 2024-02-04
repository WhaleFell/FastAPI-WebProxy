#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   gps_kml_generator.py
@Time    :   2024/02/04 17:06:37
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   GPS data to KML file
"""
from datetime import datetime, timezone, timedelta
from app.schema.base import GPSUploadData

KML_FORMAT = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
    <name>GPS Track</name>
    <Placemark>
        <name>[name]</name>
        <Style>
            <LineStyle><color>7fff0000</color><width>5</width></LineStyle>
        </Style>
            <gx:Track>
                [datas]
            </gx:Track>
    </Placemark>
</Document>
</kml>
"""


# make kml string use kml format
def replace_kml_string(data: str, name: str = "default") -> str:
    return (
        KML_FORMAT.replace("[datas]", data)
        .replace("[name]", name)
        .replace("\n", "")
        .replace("\t", "")
        .replace("  ", "")
    )


# second timestamp to utc+8 datetime
def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=8)))


# datetime convert to 2023-07-19T11:52:10Z format
def datetime_to_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def timestamp_to_str(timestamp) -> str:
    timestamp = int(timestamp)
    dt = timestamp_to_datetime(timestamp)
    return datetime_to_str(dt)


def make_kml(datas: list[GPSUploadData], name: str = "default") -> str:
    kml_str = ""
    for data in datas:
        try:
            kml_str += f"<when>{timestamp_to_str(data.GPSTimestamp)}</when><gx:coord>{data.longitude} {data.latitude} {data.altitude}</gx:coord>"
        except:
            continue

    return replace_kml_string(kml_str, name)
