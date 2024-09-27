#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
=================================================
作者：[郭磊]
手机：[15210720528]
Email：[174000902@qq.com]
Github：https://github.com/guolei19850528/guolei_py3_zkhb
=================================================
"""
from types import NoneType
from typing import Callable, Union

import requests
import xmltodict
from addict import Dict
from bs4 import BeautifulSoup
from jsonschema import validate
from jsonschema.validators import Draft202012Validator


class ApiUrlSettings:
    URL__GET_DATA_SET = "/estate/webService/ForcelandEstateService.asmx?op=GetDataSet"


class Api(object):
    """
    中科华博物管收费系统API Class
    """

    def __init__(self, base_url: str = ""):
        self._base_url = base_url

    @property
    def base_url(self):
        return self._base_url[:-1] if self._base_url.endswith("/") else self._base_url

    @base_url.setter
    def base_url(self, base_url: str):
        self._base_url = base_url

    def post(
            self,
            url: str = "",
            params: dict = None,
            data: dict = None,
            kwargs: dict = None,
            custom_callable: Callable = None
    ):
        """
        use requests.post
        :param url: requests.post(url=url,params=params,data=data,**kwargs) url=base_url+url if not pattern ^http else url
        :param params: requests.post(url=url,params=params,data=data,**kwargs)
        :param data: requests.post(url=url,params=params,data=data,**kwargs)
        :param kwargs: requests.post(url=url,params=params,data=data,**kwargs)
        :param custom_callable: custom_callable(response) if isinstance(custom_callable,Callable)
        :return:custom_callable(response) if isinstance(custom_callable,Callable) else addict.Dict instance
        """
        if not Draft202012Validator({"type": "string", "minLength": 1, "pattern": "^http"}).is_valid(url):
            url = f"/{url}" if not url.startswith("/") else url
            url = f"{self.base_url}{url}"

        kwargs = Dict(kwargs) if isinstance(kwargs, dict) else Dict()
        response = requests.post(
            url=url,
            params=params,
            data=data,
            **kwargs.to_dict()
        )
        if isinstance(custom_callable, Callable):
            return custom_callable(response)
        if response.status_code == 200:
            return response.text
        return None

    def request(
            self,
            method: str = "GET",
            url: str = "",
            params: dict = None,
            data: dict = None,
            kwargs: dict = None,
            custom_callable: Callable = None
    ):
        """
        use requests.request
        :param method: requests.request(method=method,url=url,params=params,data=data,**kwargs)
        :param url: requests.request(method=method,url=url,params=params,data=data,**kwargs) url=base_url+url if not pattern ^http else url
        :param params: requests.request(method=method,url=url,params=params,data=data,**kwargs)
        :param data: requests.request(method=method,url=url,params=params,data=data,**kwargs)
        :param kwargs: requests.request(method=method,url=url,params=params,data=data,**kwargs)
        :param custom_callable: custom_callable(response) if isinstance(custom_callable,Callable)
        :return:custom_callable(response) if isinstance(custom_callable,Callable) else addict.Dict instance
        """
        if not Draft202012Validator({"type": "string", "minLength": 1, "pattern": "^http"}).is_valid(url):
            url = f"/{url}" if not url.startswith("/") else url
            url = f"{self.base_url}{url}"
        kwargs = Dict(kwargs) if isinstance(kwargs, dict) else Dict()
        response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            **kwargs.to_dict()
        )
        if isinstance(custom_callable, Callable):
            return custom_callable(response)
        if response.status_code == 200:
            return response.text
        return None

    def get_data_set(
            self,
            url: str = ApiUrlSettings.URL__GET_DATA_SET,
            sql: str = None,
            kwargs: dict = None,
    ):
        kwargs = Dict(kwargs) if isinstance(kwargs, dict) else Dict()
        kwargs.headers.setdefault("Content-Type", "text/xml; charset=utf-8")
        data = xmltodict.unparse(
            {
                "soap:Envelope": {
                    "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "soap:Body": {
                        "GetDataSet": {
                            "@xmlns": "http://zkhb.com.cn/",
                            "sql": sql,
                            "url": "",
                        }
                    }
                }
            }
        )
        return self.post(
            url=url,
            data=data,
            kwargs=kwargs
        )

    def query_actual_charge_list(
            self,
            estate_id: Union[int, str] = 0,
            types: str = "",
            room_no: str = "",
            end_date: str = "",
            kwargs: dict = None,
    ):
        """
        查询实际缴费列表
        :param estate_id: 项目ID
        :param types: 缴费类型
        :param room_no: 房间号
        :param end_date: 结束日期
        :param kwargs:
        :return:
        """
        validate(instance=estate_id,
                 schema={"oneOf": [{"type": "string", "minLength": 1}, {"type": "integer", "minimum": 1}]})
        validate(instance=types, schema={"type": "string", "minLength": 1})
        validate(instance=room_no, schema={"type": "string", "minLength": 1})
        validate(instance=end_date, schema={"type": "string", "minLength": 1, "format": "date-time"})
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
        text = self.get_data_set(
            url=ApiUrlSettings.URL__GET_DATA_SET,
            sql=sql,
            kwargs=kwargs
        )
        if Draft202012Validator({"type": "string", "minLength": 1}).is_valid(text):
            if not isinstance(BeautifulSoup(text, "xml").find("NewDataSet"), NoneType):
                results = Dict(
                    xmltodict.parse(
                        BeautifulSoup(text, "xml").find("NewDataSet").encode("utf-8")
                    )
                ).NewDataSet.Table
                if not isinstance(results, list):
                    results = [results]
                return [Dict(i) for i in results]
        return []
