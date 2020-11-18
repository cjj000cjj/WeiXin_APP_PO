#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @time  :2020/11/16:10:12
# @Author:啊哩哩
# @File  :test_sendmessage.py
import os
from time import sleep

import pytest
import yaml
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def get_datas():
    yamlfilepath = os.path.dirname(__file__) + "/yamlfile/contacts.yml"
    with open(yamlfilepath, encoding="utf-8") as f:
        contacts = yaml.safe_load(f)
        addcontact = contacts["add"]
        delcontact = contacts["del"]
    return [addcontact, delcontact]



class TestWorkWeixin:
    def setup(self):
        desired_caps = {}
        desired_caps['platformName'] = "Android"
        desired_caps['platformVersion'] = "6.0"
        desired_caps['deviceName'] = "127.0.0.1:7555"
        desired_caps['appPackage'] = "com.tencent.wework"
        desired_caps['appActivity'] = "com.tencent.wework.launch.LaunchSplashActivity"
        desired_caps['noReset'] = "true"
        # 等待页面空闲的时间
        desired_caps['settings[waitForIdleTimeout]'] = 0
        desired_caps['dontStopAppOnReset'] = "true"
        desired_caps['skipDeviceInitialization'] = "true"
        desired_caps['unicodeKeyboard'] = "true"
        desired_caps['resetKeyboard'] = "true"
        # iOS专用 默认接受弹窗设置
        # desired_caps['autoAcceptAlerts'] = "true"
        # 这网址是固定写法:4723/wd/hub这是appium服务所在端口和服务名
        self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", desired_caps)
        self.driver.implicitly_wait(10)
        # 微信已登录，已经在微信认证，企业微信在后台运行中
        # 执行下面这句后，弹出微信登录页面
        # MobileBy.XPATH这种写法是为了封装方便
        # self.driver.find_element(MobileBy.XPATH, "//*[contains(@text,'微信登录')]").click()
        # self.driver.implicitly_wait(5)
        # # 用uiautomator定位到“进入企业 ”后边居然有空格，怪不得执行到这里老提示no Element
        # self.driver.find_element(MobileBy.XPATH, "//*[contains(@text,'进入企业')]").click()
        # self.driver.implicitly_wait(10)


    def teardown(self):
        self.driver.quit()

    def test_sendmessage(self):
        """
        搜索聊天群，在群里发消息
        :return:
        """
        # 先确定聊天群是否存在：查duofu群，然后再点duofu，进入聊天页面
        # 进入搜索框，搜索duofu，进入duofu的聊天窗口
        # 老师说com.tencent.wework:id/ 可以去掉
        # com.tencent.wework:id/guu这样的id命名，没有具体含义，是动态id
        # 不要用动态id定位，换手机，id会变，代码得重写
        self.driver.find_element(MobileBy.ID, "guu").click()
        searchname = "duofu"
        self.driver.find_element(MobileBy.XPATH, "//*[@text='搜索']").send_keys(searchname)
        # 搜索结果有可能会很久才出现，所以需要等待，等事件出现并且可以点击，才会执行点击操作
        locator = (MobileBy.ID, "dh2")
        WebDriverWait(self.driver, 60).until(expected_conditions.element_to_be_clickable(locator))
        self.driver.find_element(*locator).click()
        # 输入聊天内容，并发送
        sendmessage = "test003"
        self.driver.find_element(MobileBy.ID, "dx1").send_keys(sendmessage)
        self.driver.find_element(MobileBy.XPATH, "//*[@text='发送']").click()
        # 收集窗口中所有的聊天内容，并判断发送的内容是否正确
        elements = self.driver.find_elements(MobileBy.ID, "dwm")
        assert sendmessage == elements[-1].text

    def test_daka(self):
        """
        到工作台外出打卡
        :return:
        """
        self.driver.find_element(MobileBy.XPATH, "//*[@text='工作台']").click()
        # 打卡功能初始页面没有，下拉到下面才出现
        daka = "打卡"
        self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
            'new UiScrollable(new UiSelector().'
            'scrollable(true).instance(0)).'
            f'scrollIntoView(new UiSelector().text("{daka}")'
            '.instance(0))').click()
        # 外出打卡标签页有可能晚出现，需要等待一会，等能点击后，再点击
        locator = (MobileBy.XPATH, "//*[@text='外出打卡']")
        WebDriverWait(self.driver, 60).until(expected_conditions.element_to_be_clickable(locator))
        self.driver.find_element(*locator).click()
        # 外出打卡
        self.driver.find_element(MobileBy.XPATH, "//*[contains(@text,'次外出')]").click()
        # 获取文本属性
        result = self.driver.find_element(MobileBy.ID, "mn").text
        # 判断打卡结果
        assert result == "外出打卡成功"


    @pytest.mark.parametrize("name, gender, phone", get_datas()[0])
    def test_addcontact(self, name, gender, phone):
        """
        添加联系人
        :return:
        """
        # 首页进入通讯录页面
        self.driver.find_element(MobileBy.XPATH, "//*[@text='通讯录']").click()
        # 考虑到成员很多的时候，底部导航栏需要滚动到下面才能看到，所以做了个滚动操作
        self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                                 'new UiScrollable(new UiSelector().'
                                 'scrollable(true).instance(0)).'
                                 'scrollIntoView(new UiSelector().text("添加成员")'
                                 '.instance(0))').click()
        self.driver.find_element(MobileBy.XPATH, "//*[@text='手动输入添加']").click()
        self.driver.find_element(MobileBy.XPATH, "//*[contains(@text,'姓名')]/../*[@text='必填']").send_keys(name)
        self.driver.implicitly_wait(3)
        self.driver.find_element(MobileBy.XPATH, "//*[@text='男']").click()
        if gender == "女":
            self.driver.find_element(MobileBy.XPATH, "//*[@text='女']").click()
        else:
            # 显式等待10秒
            element = WebDriverWait(self.driver, 10).until(lambda x:x.find_element(MobileBy.XPATH, "//*[@text='男']"))
            element.click()
        # 手机名称对应输入框的定位
        self.driver.find_element(MobileBy.XPATH, "//*[contains(@text,'手机') and @class='android.widget.TextView']/..//*[@class='android.widget.EditText']").send_keys(phone)
        # 点击保存，保存联系人
        self.driver.find_element(MobileBy.XPATH, "//*[contains(@text,'保存')]").click()
        # 获取toast提示并判断
        mytoast = self.driver.find_element(MobileBy.XPATH, "//*[@class='android.widget.Toast']").text
        assert mytoast == "添加成功"
        # 退出添加成员页面,有时候toast提示显示较慢,需要等待几秒
        self.driver.implicitly_wait(3)
        self.driver.find_element(MobileBy.ID, "com.tencent.wework:id/gu_").click()


    @pytest.mark.parametrize("name", get_datas()[1])
    def test_deletecontact(self, name):
        """
        删除联系人
        :return:
        """
        # 首页进入通讯录页面
        self.driver.find_element(MobileBy.XPATH, "//*[@text='通讯录']").click()
        # 查询要删除的联系人
        self.driver.find_element(MobileBy.ID, "com.tencent.wework:id/guu").click()
        self.driver.find_element(MobileBy.XPATH, "//*[@text='搜索']").send_keys(name)
        # 手机企业微信这里查询结果出现 比较慢
        # 搜索所有姓名
        # locator1 = (MobileBy.XPATH, f"//*[@text='{name}']")
        # WebDriverWait(self.driver, 60).until(expected_conditions.visibility_of_all_elements_located(locator1))
        # 显式等待不管用啊
        sleep(3)
        elements = self.driver.find_elements(MobileBy.XPATH, f"//*[@text='{name}']")
        if len(elements) < 2:
            print("要删除的联系人不存在")
            return
        sleep(3)
        elements[1].click()
        # 点击个人信息
        self.driver.find_element(MobileBy.ID, "com.tencent.wework:id/guk").click()
        # 没有等待时间,编辑成员按钮加载出来了也不点,不懂为什么
        locator2 = (MobileBy.XPATH, "//*[@text='编辑成员']")
        WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_all_elements_located(locator2))
        elements2 = self.driver.find_element(*locator2)
        elements2.click()
        sleep(3)
        # 考虑部分手机需要滚动到下面才能看到，所以做了个滚动操作
        self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                                 'new UiScrollable(new UiSelector().'
                                 'scrollable(true).instance(0)).'
                                 'scrollIntoView(new UiSelector().text("删除成员")'
                                 '.instance(0))').click()
        sleep(2)
        self.driver.find_element(MobileBy.XPATH, "//*[@text='确定']").click()
        sleep(2)
        deleelement = self.driver.find_elements(MobileBy.XPATH, f"//*[@text='{name}']")
        assert len(deleelement) == len(elements)-1
        # 退出添加成员页面,需要等待断言完成
        sleep(3)
        self.driver.find_element(MobileBy.ID, "com.tencent.wework:id/gu_").click()





