# Tailscale 设备状态通知

定时检查 Tailscale 设备状态，并通过 Bark 推送设备上线或下线通知。

## 使用要求

- Python 3
- 已安装并登录 Tailscale，且命令行可执行 `tailscale status`
- 可导入提供 `BarkNotificator` 的 Python 模块
- 一个 Bark 设备推送 Token

## 配置与运行

设置 Bark 设备 Token 后运行脚本：

```bash
export BARK_DEVICE_TOKEN="你的 Bark 设备 Token"
python3 ts_notification.py
```

程序每 5 秒检查一次设备状态。运行期间检测到设备上线或下线时，会发送 Bark 通知；设备管理页面会作为通知跳转链接。
