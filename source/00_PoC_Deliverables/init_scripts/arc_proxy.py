import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# ===================== 仅需修改这里 =====================
# 替换为你火山平台 Coding Plan 专属 API Key
ARK_CODING_API_KEY = "ark-5a0ee1cc-8278-42d2-bdf3-a4960230ac7b-b7987"
# Coding Plan 固定接口地址
ARK_API_URL = "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions"
# =======================================================

class ProxyRequestHandler(BaseHTTPRequestHandler):
    # 统一放行所有跨域头，解决预检OPTIONS报错
    def add_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    # 处理浏览器预检 OPTIONS 请求
    def do_OPTIONS(self):
        self.send_response(200)
        self.add_cors_headers()
        self.end_headers()

    # 转发POST对话请求至火山方舟
    def do_POST(self):
        # 读取前端传来的消息体
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        # 向后端方舟发送请求（密钥统一放在代理，前端不带鉴权头）
        ark_response = requests.post(
            url=ARK_API_URL,
            headers={
                "Authorization": f"Bearer {ARK_CODING_API_KEY}",
                "Content-Type": "application/json"
            },
            data=raw_body
        )

        # 把方舟返回内容原样返回给前端
        self.send_response(ark_response.status_code)
        self.add_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(ark_response.content)

if __name__ == "__main__":
    # 本地代理端口 9000
    server_address = ("127.0.0.1", 9000)
    http_server = HTTPServer(server_address, ProxyRequestHandler)
    print("=" * 60)
    print("中转代理服务已启动：http://127.0.0.1:9000")
    print("前端页面 fetch 请求地址填写：http://127.0.0.1:9000")
    print("=" * 60)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
        print("\n代理服务已关闭")