import tesserocr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
from io import BytesIO
from PIL import Image
EMAIL = 'test@test.com'
PASSWORD = ''

class CrachGeetest():
    def __init__(self):
        self.url = 'https://account.geetest.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser,20)
        self.email = EMAIL
        self.password = PASSWORD

    # 模拟点击
    def get_geetest_button(self):
        # 获取初始验证按钮 return 按钮对象
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'geetest_radar_tip')))
        return button

    # 识别缺口
    def get_position(self):
        # 获取验证码位置 return 验证码按钮对象
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'geetest_canvas_img')))
        time.sleep(2)
        location = img.location
        size = img.size
        top,bottom,left,right = location["y"],location['y']+size["height"],location["x"],location["x"] + size["width"]
        return (top,bottom,left,right)

    def get_geetest_image(self,name='captcha.png'):
        # 获取验证码图片 return 图片对象
        top,bottom,left,right = self.get_position()
        print('验证码位置',top,bottom,left,right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left,top,right,bottom))
        return captcha

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_slider(self):
        # 获得滑块
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'geetest_slider_button')))
        return slider

    # slider = self.get_slider()
    # slider.click()
    def is_pixel_equal(self,image1,image2,x,y):
        """
        判断两个像素是否重合
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 获取两个像素点
        pixel1 = image1.load()[x,y]
        pixel2 = image2.load()[x,y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.ID, 'email')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        email.send_keys(self.email)
        password.send_keys(self.password)

    def get_gap(self,image1,image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        left = 60
        for i in range(left,image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1,image2,i,j):
                    left = i
                    return left
        return left

    # 模拟拖动
    def get_track(self,distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 偏移轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为2
                a = 2
            else:
                # 加速度为-3
                a = -3
            # 初速度
            v0 = v
            # 当前速度 v = v0 + at
            v = v0 + a * t
            # 移动距离 x = v0t + 1/2 * a * t ^ 2
            move = v0 * t + 1/2 * a * t * t
            #当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return  track

    def move_to_gap(self,slider,tracks):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param tracks: 缺口
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=x,yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform() #松开鼠标

    def login(self):
        submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'login-btn')))
        submit.click()
        time.sleep(10)
        print('登录成功')

    def crack(self):
        # 输入用户名和密码
        self.open()
        time.sleep(5)
        # 点击验证按钮
        button = self.get_geetest_button()
        button.click()
        time.sleep(5)
        # 获取验证码图片
        image1 = self.get_geetest_image('captcha1.png')
        # 点按呼出缺口
        slider = self.get_slider()
        slider.click()
        # 获取缺口图片
        image2 = self.get_geetest_image('captcha2.png')
        # 获取缺口位置
        gap = self.get_gap(image1,image2)
        print('缺口位置',gap)
        # 获取移动轨迹
        track = self.get_track(gap)
        print('移动轨迹',track)
        # 拖动滑块
        self.move_to_gap(slider,track)

        success = self.wait.until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
        print(success)

        if success:
            self.login()
        else:
            self.crack()

if __name__ == '__main__':
    cracks = CrachGeetest()
    cracks.crack()