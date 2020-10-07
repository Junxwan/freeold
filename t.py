import pandas as pd
from stock import data, name

d = data.Stock('/private/var/www/other/free/csv/stock')
d.readAll()
c = pd.read_csv('/private/var/www/other/free/code.csv')
list = []

for i, row in c.iterrows():
    v = d.data.loc[row['code']]
    id = (v.loc[name.DATE] <= row[name.DATE]).idxmax()
    v = v[id + 1]

    l = row.tolist()
    l.append(v[name.INCREASE])
    list.append(l)

pd.DataFrame(list, columns=[name.DATE, 'code', name.INCREASE]).to_csv('/private/var/www/other/free/result.csv')

pass

# win32gui.SendMessage(hwnd_filename, win32con.WM_SETFOCUS, 0, '2020-09-24-1101')
# win32gui.SendMessage(hwnd_filename, win32con.WM_SETTEXT, 0, '2020-09-24-1101')
# time.sleep(1)
#
# hwnd_save = win32gui.FindWindowEx(d, None, "Button", None)
# win32gui.PostMessage(hwnd_save, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
# win32gui.PostMessage(hwnd_save, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

# win32api.PostMessage(d, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
# win32api.PostMessage(d, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)

# win32gui.SendMessage(tick_hld, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 200)
# win32gui.SendMessage(tick_hld, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, 200)

# win32api.SendMessage(hld, win32con.VK_VOLUME_DOWN, win32con.VK_DOWN, 0)
# win32api.SendMessage(hld, win32con.VK_VOLUME_DOWN, win32con.VK_DOWN, 0)

# win32api.SendMessage(tick_hld, win32con.VK_DOWN, 0, 0)

# win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)
# win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)

# tempt = win32api.GetCursorPos()  # 记录鼠标所处位置的坐标
# windowRec = win32gui.GetWindowRect(tick_hld)  # 目标子句柄窗口的坐标
# x = tempt[0] - windowRec[0]  # 计算相对x坐标
# y = tempt[1] - windowRec[1]  # 计算相对y坐标

# long_position = win32api.MAKELONG(x, y)

# windowRec = win32gui.GetWindowRect(tick_hld)
# time.sleep(1)

# win32gui.SendMessage(tick_hld, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, 200)
# win32gui.SendMessage(tick_hld, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, 200)


# win32gui.EnumChildWindows(hld, s, None)


#
# MN_GETHMENU = 0x01E1
# print(win32gui.SendMessage(int('0x40CD0', 0), MN_GETHMENU, 0, 0))

# win32gui.SendMessage(int('0x40CD0', 0), win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, 0)
