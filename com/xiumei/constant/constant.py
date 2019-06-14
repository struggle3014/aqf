# -*- coding=utf-8 -*-
import sys


class Const:

    class ConstError(PermissionError):
        """
        自定义异常处理
        """
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        """
        重写 __setattr__() 方法
        :param name:
        :param value:
        :return:
        """
        if name in self.__dict__:  # 已包含该常量，不能二次赋值
            raise self.ConstError("Can't change const {0}".format(name))
        if not name.isupper():  # 所有的字母需要大写
            raise self.ConstCaseError("const name {0} is not all uppercase".format(name))
        self.__dict__[name] = value


# 将系统加载的模块列表中的 constant 替换为 _const() 实例
sys.modules[__name__] = Const()
