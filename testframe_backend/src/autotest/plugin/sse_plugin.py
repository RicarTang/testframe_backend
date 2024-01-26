import os
from ...utils.log_util import log
from ...core.cache import RedisService


class SSEPlugin:
    """Pytest 插件类"""

    def pytest_sessionstart(self, session):
        # 在测试会话开始时初始化测试结果统计
        log.debug(f"会话开始,{session.config.getoption('task_id')}")
        # RedisService.rpush(session.config.getoption("task_id"), "会话开始")
        # session.config.test_passed = 0
        # session.config.test_failed = 0
        # session.config.test_errors = 0
        # session.config.test_total = 0

    def pytest_runtest_protocol(self, item, nextitem):
        # 在每个测试用例执行前更新测试结果统计
        # item.session.config.test_total += 1
        log.debug(item.config.getoption("task_id"))
        # log.debug(f"已测试用例数量：{item.session.config.test_total}")

    def pytest_runtest_logreport(self, report):
        # 在每个测试用例执行后更新测试结果统计
        # if report.passed:
        #     report.session.config.test_passed += 1
        # elif report.failed:
        #     report.session.config.test_failed += 1
        # elif report.skipped and hasattr(report, "wasxfail"):
        #     report.session.config.test_failed += 1
        # elif report.skipped:
        #     report.session.config.test_errors += 1
        log.debug(report)
