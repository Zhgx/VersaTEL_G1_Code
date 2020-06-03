#ecoding=utf8
import logging
import pytest

def setup_module():
    logging.info("setup_module：整个.py模块下，只执行一次")
def teardown_module():
    logging.info("teardown_module：整个.py模块下，只执行一次")

class TestPytestObject2:
    def test_three(self):
        assert [1, 2] == [1, 3]
    def test_foure(self):
        assert {"a": 1, "b": "sss"} == {"a": 2, "b": "ss"}

class TestPytestObject:
    @classmethod
    def setup_class(cls):
        logging.info("setup_class：该class下，所有用例前面执行一次")

    def setup_method(self):
        logging.info("setup_methon：每个用例开始前都会执行")

    def test_two(self):
        assert 1 == 2
    def test_one(self):
        assert 2 == 2

    def teardown_method(self):
        logging.info("teardown_method：每个用例结束后都会执行")

    @classmethod
    def teardown_class(cls):
        logging.info("teardown_class：该class下，所有用例后面执行一次")