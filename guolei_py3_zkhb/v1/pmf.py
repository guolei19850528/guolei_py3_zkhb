#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from types import NoneType
from typing import Callable, Union

import requests
import xmltodict
from addict import Dict
from bs4 import BeautifulSoup
from jsonschema import validate
from jsonschema.validators import Draft202012Validator


class Api(object):
    """
    中科华博物管收费系统API Class
    """

    def __init__(self, url: str = ""):
        validate(instance=url, schema={"type": "string", "minLength": 1, "format": "uri"})
        self._url = url

    @property
    def url(self):
        return self._url[:-1] if self._url.endswith("/") else self._url

    @url.setter
    def url(self, url: str):
        self._url = url

    def call_get_dataset(
            self,
            request_func_kwargs_data_sql: str = "",
            request_func_kwargs_data_url: str = "",
            request_func_kwargs: dict = {},
            request_func_response_callable: Callable = None
    ):
        validate(instance=request_func_kwargs_data_sql, schema={"type": "string", "minLength": 1, "format": "uri"})
        validate(instance=request_func_kwargs_data_url, schema={"type": "string", "format": "uri"})
        if not Draft202012Validator({"type": "boolean", "const": True}).is_valid(isinstance(request_func_kwargs, dict)):
            request_func_kwargs = {}
        request_func_kwargs = Dict(request_func_kwargs)
        request_func_kwargs.setdefault("url", f"{self.url}")
        request_func_kwargs.setdefault("method", "POST")
        request_func_kwargs.setdefault("headers", Dict())
        request_func_kwargs.headers.setdefault("Content-Type", "text/xml; charset=utf-8")
        request_func_kwargs.setdefault(
            "data",
            xmltodict.unparse(
                {
                    "soap:Envelope": {
                        "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
                        "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                        "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                        "soap:Body": {
                            "GetDataSet": {
                                "@xmlns": "http://zkhb.com.cn/",
                                "sql": request_func_kwargs_data_sql,
                                "url": request_func_kwargs_data_url,
                            }
                        }
                    }
                }
            )
        )
        response = requests.request(**request_func_kwargs.to_dict())
        if Draft202012Validator({"type": "boolean", "const": True}).is_valid(
                isinstance(request_func_response_callable, Callable)):
            return request_func_response_callable(response, request_func_kwargs)
        if response.status_code == 200:
            if Draft202012Validator({"type": "string", "minLength": 1}).is_valid(response.text):
                if not isinstance(BeautifulSoup(response.text, "xml").find("NewDataSet"), NoneType):
                    results = Dict(
                        xmltodict.parse(
                            BeautifulSoup(response.text, "xml").find("NewDataSet").encode("utf-8"))
                    ).NewDataSet.Table
                    if not isinstance(results, list):
                        results = [results]
                    return [Dict(i) for i in results]
        return []

    def query_actual_charge_list(
            self,
            estate_id: Union[int, str] = 0,
            types: str = "",
            room_no: str = "",
            end_date: str = "",
            call_get_dataset_func_kwargs: dict = {},
    ):
        """
        查询实际缴费列表
        :param estate_id: 项目ID
        :param types: 缴费类型
        :param room_no: 房间号
        :param end_date: 结束日期
        :param call_get_dataset_func_kwargs: call_get_dataset(**call_get_dataset_func_kwargs)
        :return:
        """
        validate(instance=estate_id,
                 schema={"oneOf": [{"type": "string", "minLength": 1}, {"type": "integer", "minimum": 1}]})
        validate(instance=types, schema={"type": "string", "minLength": 1})
        validate(instance=room_no, schema={"type": "string", "minLength": 1})
        validate(instance=end_date, schema={"type": "string", "minLength": 1, "format": "date-time"})
        if not Draft202012Validator({"type": "boolean", "const": True}).is_valid(
                isinstance(call_get_dataset_func_kwargs, dict)):
            call_get_dataset_func_kwargs = {}
        call_get_dataset_func_kwargs = Dict(call_get_dataset_func_kwargs)
        sql = f"""select
                    cml.ChargeMListID,
                    cml.ChargeMListNo,
                    cml.ChargeTime,
                    cml.PayerName,
                    cml.ChargePersonName,
                    cml.ActualPayMoney,
                    cml.EstateID,
                    cml.ItemNames,
                    ed.Caption as EstateName,
                    cfi.ChargeFeeItemID,
                    cfi.ActualAmount,
                    cfi.SDate,
                    cfi.EDate,
                    cfi.RmId,
                    rd.RmNo,
                    cml.CreateTime,
                    cml.LastUpdateTime,
                    cbi.ItemName,
                    cbi.IsPayFull
                from
                    chargeMasterList cml,EstateDetail ed,ChargeFeeItem cfi,RoomDetail rd,ChargeBillItem cbi
                where
                    cml.EstateID=ed.EstateID
                    and
                    cml.ChargeMListID=cfi.ChargeMListID
                    and
                    cfi.RmId=rd.RmId
                    and
                    cfi.CBillItemID=cbi.CBillItemID
                    and
                    (cml.EstateID={estate_id} and cbi.ItemName='{types}' and rd.RmNo='{room_no}' and cfi.EDate>='{end_date}')
                order by cfi.ChargeFeeItemID desc;
            """
        call_get_dataset_func_kwargs.setdefault("request_func_kwargs_data_sql", sql)
        return self.call_get_dataset(**call_get_dataset_func_kwargs.to_dict())
