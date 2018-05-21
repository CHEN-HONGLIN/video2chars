# -*- coding:utf-8 -*-

import numpy as np
import pickle
import os

# 用于生成字符画的像素，越往后视觉上越明显。。这是我自己按感觉排的，你可以随意调整。写函数里效率太低，所以只好放全局了
pixels = " .,-'`:!1+*abcdefghijklmnopqrstuvwxyz<>()\/{}[]?234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ%&@#$"


def video2imgs(video_name, size):
    """

    :param video_name: 字符串, 视频文件的路径
    :param size: 二元组，(宽, 高)，用于指定生成的字符画的尺寸
    :return: 一个 img 对象的列表，img对象实际上就是 numpy.ndarray 数组
    """
    import cv2  # 导入 opencv

    img_list = []

    # 从指定文件创建一个VideoCapture对象
    cap = cv2.VideoCapture(video_name)

    # 如果cap对象已经初始化完成了，就返回true，换句话说这是一个 while true 循环
    while cap.isOpened():
        # cap.read() 返回值介绍：
        #   ret 表示是否读取到图像
        #   frame 为图像矩阵，类型为 numpy.ndarry.
        ret, frame = cap.read()
        if ret:
            # 转换成灰度图，也可不做这一步，转换成彩色字符视频。
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # resize 图片，保证图片转换成字符画后，能完整地在命令行中显示。
            img = cv2.resize(gray, size, interpolation=cv2.INTER_AREA)

            # 分帧保存转换结果
            img_list.append(img)
        else:
            break

    # 结束时要释放空间
    cap.release()

    return img_list


def img2chars(img):
    res = []
    """

    :param img: numpy.ndarray, 图像矩阵
    :return: 字符串的列表：图像对应的字符画，其每一行对应图像的一行像素
    """

    # 要注意这里的顺序和 之前的 size 刚好相反
    height, width = img.shape
    for row in range(height):
        line = ""
        for col in range(width):
            # 灰度是用8位表示的，最大值为255。
            # 这里将灰度转换到0-1之间
            percent = img[row][col] / 255

            # 将灰度值进一步转换到 0 到 (len(pixels) - 1) 之间，这样就和 pixels 里的字符对应对应起来了
            index = int(percent * (len(pixels) - 1))

            # 添加字符像素（最后面加一个空格，是因为命令行有行距却没几乎有字符间距，用空格当间距）
            line += pixels[index] + " "
        res.append(line)

    return res


def imgs2chars(imgs):
    video_chars = []
    for img in imgs:
        video_chars.append(img2chars(img))

    return video_chars


def play_video(video_chars):
    """
    播放字符视频
    :param video_chars: 字符画的列表，每个元素为一帧
    :return: None
    """
    # 导入需要的模块，这两个模块只有这个函数需要，所以在这里导入了
    import time
    import curses

    # 获取字符画的尺寸
    width, height = len(video_chars[0][0]), len(video_chars[0])

    # 初始化curses，这个是必须的，直接抄就行
    stdscr = curses.initscr()
    curses.start_color()
    try:
        # 调整窗口大小，宽度最好略大于字符画宽度。另外注意curses的height和width的顺序
        stdscr.resize(height, width * 2)

        for pic_i in range(len(video_chars)):
            # 显示 pic_i，即第i帧字符画
            for line_i in range(height):
                # 将pic_i的第i行写入第i列。(line_i, 0)表示从第i行的开头开始写入。最后一个参数设置字符为白色
                stdscr.addstr(line_i, 0, video_chars[pic_i][line_i], curses.COLOR_WHITE)
            stdscr.refresh()  # 写入后需要refresh才会立即更新界面

            time.sleep(1 / 24)  # 粗略地控制播放速度。
    finally:
        # curses 使用前要初始化，用完后无论有没有异常，都要关闭
        curses.endwin()
    return


def dump(obj, file_name):
    """
    将指定对象，以file_nam为名，保存到本地
    """
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f)
    return


def load(filename):
    """
    从当前文件夹的指定文件中load对象
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)


def get_file_name(file_path):
    """
    从文件路径中提取出不带拓展名的文件名
    """
    # 从文件路径获取文件名 _name
    path, file_name_with_extesion = os.path.split(file_path)

    # 拿到文件名前缀
    file_name, file_extern = os.path.splitext(file_name_with_extesion)

    return file_name


def has_file(path, file_name):
    """
    判断指定目录下，是否存在某文件
    """
    return file_name in os.listdir(path)


def get_video_chars(video_path):
    """
    返回视频对应的字符视频
    """
    video_dump = get_file_name(video_path) + ".pickle"

    # 如果 video_dump 已经存在于当前文件夹，就可以直接读取进来了
    if has_file(".", video_dump):
        print("发现该视频的转换缓存，直接读取")
        video_chars = load(video_dump)
    else:
        print("未发现缓存，开始字符视频转换")

        print("开始逐帧读取")
        # 视频转字符动画
        imgs = video2imgs(video_path, (64, 48))

        print("视频已全部转换到图像， 开始逐帧转换为字符画")
        video_chars = imgs2chars(imgs)

        print("转换完成，开始缓存结果")
        # 把转换结果保存下来
        dump(video_chars, video_dump)
        print("缓存完毕")

    return video_chars


if __name__ == "__main__":
    # 宽，高
    size = (64, 48)
    # 视频路径，换成你自己的
    video_path = "BadApple.mp4"
    video_chars = get_video_chars(video_path)
    play_video(video_chars)