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

import xmltodict
from addict import Dict
from bs4 import BeautifulSoup
from guolei_py3_requests.library import ResponseCallable, request
from jsonschema.validators import Draft202012Validator
from requests import Response


class ResponseCallable(ResponseCallable):
    """
    Response Callable Class
    """

    @staticmethod
    def text_xml(response: Response = None, status_code: int = 200, features: Union[str, Sequence[str]] = "xml"):
        return BeautifulSoup(
            ResponseCallable.text(response=response, status_code=status_code),
            features="xml"
        )

    @staticmethod
    def text_xml__new_data_set__table(
            response: Response = None,
            status_code: int = 200,
            features: Union[str, Sequence[str]] = "xml"
    ):
        text_xml = ResponseCallable.text_xml(response=response, status_code=status_code, features=features)
        if isinstance(text_xml, NoneType):
            return []
        results = Dict(
            xmltodict.parse(
                text_xml.find("NewDataSet").encode(
                    "utf-8"))
        ).NewDataSet.Table
        if isinstance(results, list):
            return results
        if isinstance(results, dict) and len(results.keys()):
            return [results]
        return []


class UrlsSetting:
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

    def post(
            self,
            response_callable: Callable = ResponseCallable.text_xml__new_data_set__table,
            url: str = None,
            params: Any = None,
            data: Any = None,
            json: Any = None,
            headers: Any = None,
            **kwargs: Any
    ):
        return self.request(
            response_callable=response_callable,
            method="POST",
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            **kwargs
        )

    def request(
            self,
            response_callable: Callable = ResponseCallable.text_xml__new_data_set__table,
            method: str = "GET",
            url: str = None,
            params: Any = None,
            headers: Any = None,
            **kwargs
    ):
        if not Draft202012Validator({"type": "string", "minLength": 1, "pattern": "^http"}).is_valid(url):
            url = f"/{url}" if not url.startswith("/") else url
            url = f"{self.base_url}{url}"
        return request(
            response_callable=response_callable,
            method=method,
            url=url,
            params=params,
            headers=headers,
            **kwargs
        )

    def get_data_set(
            self, sql: str = None,
            url: str = None,
            response_callable: Callable = ResponseCallable.text_xml__new_data_set__table
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
            response_callable=response_callable,
            url=UrlsSetting.GET_DATA_SET,
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
