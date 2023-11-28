from typing import Optional, List
from pydantic import BaseModel, Field
from ..db.models import Testsuite_Pydantic
from .common_schema import PageParam
from .testcase_schema import TestCaseTo


class TestSuiteIn(BaseModel):
    """添加测试套件request schema"""

    suite_no: str = Field(max_length=10, description="套件编号")
    suite_title: str = Field(max_length=50, description="套件名称/标题")
    remark: Optional[str] = Field(description="备注")
    testcase_id: Optional[List[int]] = Field(
        gt=0, description="测试用例id", alias="testcase_id_list"
    )


class TestSuiteTo(Testsuite_Pydantic):
    """测试套件response schema"""

    testcases: List[TestCaseTo] = Field(description="套件包含的用例")


class TestSuitesTo(PageParam):
    """翻页测试套件 response schema"""

    data: List[TestSuiteTo]