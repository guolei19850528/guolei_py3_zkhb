#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
=================================================
中科华博 物管收费系统 类库
-------------------------------------------------
作者：[郭磊]
手机：[15210720528]
Email：[174000902@qq.com]
Github：https://github.com/guolei19850528/guolei_py3_zkhb
=================================================
"""
from typing import Callable, Iterable

import xmltodict
from addict import Dict
from bs4 import BeautifulSoup
from guolei_py3_requests import RequestsResponseCallable, requests_request
from requests import Response


class RequestsResponseCallable(RequestsResponseCallable):
    @staticmethod
    def status_code_200_text_beautiful_soup(response: Response = None, features=""):
        return BeautifulSoup(
            RequestsResponseCallable.status_code_200_text(response=response),
            features=features
        )

    @staticmethod
    def status_code_200_text_xml(response: Response = None):
        return RequestsResponseCallable.status_code_200_text_beautiful_soup(
            response=response,
            features="xml"
        )

    @staticmethod
    def status_code_200_text_xml_new_data_set(response: Response = None):
        if RequestsResponseCallable.status_code_200_text_xml(response=response).find("NewDataSet") is None:
            return []
        results = Dict(
            xmltodict.parse(
                RequestsResponseCallable.status_code_200_text_xml(response=response).find("NewDataSet").encode(
                    "utf-8"))
        ).NewDataSet.Table
        if isinstance(results, list):
            return results
        if isinstance(results, dict) and len(results.keys()):
            return [results]
        return []


class Api(object):
    """
    中科华博 物业管理收费系统 Api Class
    """

    def __init__(self, url: str = ""):
        """
        中科华博 物业管理收费系统 Api Class
        :param url: web service url
        """
        self._url = url

    @property
    def url(self) -> str:
        return self._url[:-1] if self._url.endswith("/") else self._url

    @url.setter
    def url(self, value: str = ""):
        self._url = value

    def call_get_data_set(
            self,
            requests_request_data: dict = {},
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_text_xml,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> list:
        """
        :param requests_request_data:
        :param requests_response_callable:
        :param requests_request_args:
        :param requests_request_kwargs:
        :return:
        """
        requests_request_data = Dict(requests_request_data)
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": self.url,
            "method": "POST",
            "headers": {
                "Content-Type": "text/xml; charset=utf-8",
                **requests_request_kwargs.headers,
            },
            "data": xmltodict.unparse(
                {
                    "soap:Envelope": {
                        "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
                        "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                        "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                        "soap:Body": {
                            "GetDataSet": {
                                "@xmlns": "http://zkhb.com.cn/",
                                **requests_request_data,
                                **requests_request_kwargs.data,
                            }
                        }
                    }
                }
            )
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def query_actual_charges(
            self,
            estate_id: int = 0,
            types: str = "",
            room_no: str = "",
            end_date: str = "",
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_text_xml_new_data_set,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> list:
        """
        :param estate_id: 项目ID
        :param types: 收费类型
        :param room_no: 房间号
        :param end_date: 结束日期
        :param requests_response_callable:
        :param requests_request_args:
        :param requests_request_kwargs:
        :return:
        """
        requests_request_kwargs = Dict(requests_request_kwargs)
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
        return self.call_get_data_set(
            requests_request_data={
                "sql": sql,
                **requests_request_kwargs.data,
            },
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )
