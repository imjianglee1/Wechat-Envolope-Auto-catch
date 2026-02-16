import cv2
import numpy as np
import pyautogui
import time
import sys
import mss


def find_image_on_screen_fast(sct, monitor, template_gray, threshold=0.8):
    """预加载加速版：直接处理内存中的灰度数据"""
    sct_img = sct.grab(monitor)
    # 转换为 numpy 数组并直接转灰度 (mss 返回 BGRA)
    screenshot_gray = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template_gray.shape
        return (max_loc[0] + w // 2, max_loc[1] + h // 2, max_val)
    return None


def sequential_loop(
    red_packet_path,
    open_button_path,
    threshold=0.8,
    interval=1.0,
    post_click_delay=0.5,
    open_button_timeout=1.0,
    animation_delay=1.5,
):
    print("正在初始化资源...")
    tpl_red = cv2.imread(red_packet_path, 0)
    tpl_open = cv2.imread(open_button_path, 0)

    if tpl_red is None or tpl_open is None:
        print("错误：无法读取模板图片，请检查路径")
        sys.exit(1)

    sct = mss.mss()
    monitor = sct.monitors[1]
    print("资源加载完成，程序启动！")

    try:
        while True:
            print("等待红包出现...")
            while True:
                res = find_image_on_screen_fast(sct, monitor, tpl_red, threshold)
                if res:
                    pyautogui.click(res[0], res[1])
                    print(f"找到红包! ({res[2]:.2f})")
                    time.sleep(post_click_delay)
                    break
                time.sleep(interval)
            print("等待打开按钮...")
            start_time = time.time()
            found_open = False

            while time.time() - start_time <= open_button_timeout:
                res_open = find_image_on_screen_fast(sct, monitor, tpl_open, threshold)
                if res_open:
                    pyautogui.click(res_open[0], res_open[1])
                    print(f"已点击打开按钮，等待动画 {animation_delay}s...")
                    time.sleep(animation_delay)
                    found_open = True
                    break
                time.sleep(interval)

            if not found_open:
                print(f"等待超时 ({open_button_timeout}s)，强制执行 Esc 重置...")

            # 执行返回操作
            pyautogui.press("esc")
            print("已发送 Esc, 准备下一轮...\n")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n程序已停止")
        sys.exit(0)


if __name__ == "__main__":
    # 红包模板图片路径
    RED_PACKET_PATH = r"red_packet_icon.png"
    # 打开红包按钮模板图片路径
    OPEN_BUTTON_PATH = r"open_button.png"

    THRESHOLD = 0.85
    INTERVAL = 0.05
    POST_CLICK_DELAY = 0.03
    OPEN_BUTTON_TIMEOUT = 1.2
    ANIMATION_DELAY = 3
    sequential_loop(
        RED_PACKET_PATH,
        OPEN_BUTTON_PATH,
        THRESHOLD,
        INTERVAL,
        POST_CLICK_DELAY,
        OPEN_BUTTON_TIMEOUT,
        ANIMATION_DELAY,
    )
