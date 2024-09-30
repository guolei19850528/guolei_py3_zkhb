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
from typing import Callable, Union, Any, Sequence

import requests
import xmltodict
from addict import Dict
from bs4 import BeautifulSoup
from requests import Response


class ResponseCallable(object):
    """
    Response Callable Class
    """

    @staticmethod
    def xml_new_data_set_table(
            response: Response = None,
            status_code: int = 200,
            features: Union[str, Sequence[str]] = "xml"
    ):
        if response.status_code == status_code:
            xml_doc = BeautifulSoup(
                response.text,
                features=features
            )
            if isinstance(xml_doc, NoneType):
                return []
            results = Dict(
                xmltodict.parse(
                    xml_doc.find("NewDataSet").encode(
                        "utf-8"))
            ).NewDataSet.Table
            if isinstance(results, list):
                return results
            if isinstance(results, dict) and len(results.keys()):
                return [results]
        return []


class UrlSetting(object):
    GET_DATA_SET = "/estate/webService/ForcelandEstateService.asmx?op=GetDataSet"


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

    def post(self, on_response_callback: Callable = None, path: str = None,
             **kwargs):
        """
        execute post by requests.post

        params.setdefault("key", self.key)

        :param on_response_callback: response callback
        :param path: if url is None: url=f"{self.base_url}{path}"
        :param kwargs: requests.get(**kwargs)
        :return: on_response_callback(response) or response
        """
        path = kwargs.get("url", None) or f"{self.base_url}{path}"
        kwargs.update([
            ("url", path),
        ])
        response = requests.post(**kwargs)
        if isinstance(on_response_callback, Callable):
            return on_response_callback(response)
        return response

    def request(self, on_response_callback: Callable = None, path: str = None,
                **kwargs):
        """
        execute request by requests.request

        params.setdefault("key", self.key)

        :param on_response_callback: response callback
        :param path: if url is None: url=f"{self.base_url}{path}"
        :param kwargs: requests.get(**kwargs)
        :return: on_response_callback(response) or response
        """
        path = kwargs.get("url", None) or f"{self.base_url}{path}"
        kwargs.update([
            ("url", path),
        ])
        response = requests.request(**kwargs)
        if isinstance(on_response_callback, Callable):
            return on_response_callback(response)
        return response

    def get_data_set(
            self,
            sql: str = None,
            url: str = None
    ):
        data = xmltodict.unparse(
            {
                "soap:Envelope": {
                    "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "soap:Body": {
                        "GetDataSet": {
                            "@xmlns": "http://zkhb.com.cn/",
                            "sql": f"{sql}",
                            "url": f"{url}",
                        }
                    }
                }
            }
        )
        return self.post(
            on_response_callback=ResponseCallable.xml_new_data_set_table,
            path=UrlSetting.GET_DATA_SET,
            data=data,
            headers={"Content-Type": "text/xml; charset=utf-8"}
        )

    def query_actual_charge_list(
            self,
            estate_id: Union[int, str] = 0,
            types: str = "",
            room_no: str = "",
            end_date: str = ""
    ) -> list:
        """
        :param estate_id: 项目ID
        :param types: 收费类型
        :param room_no: 房间号
        :param end_date: 结束日期
        :return:
        """
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
        return self.get_data_set(sql=sql)
