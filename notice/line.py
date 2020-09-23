from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage


class Api():
    def __init__(self, token, secret):
        self._app = Flask(__name__)
        self._api = LineBotApi(token)
        self._handler = WebhookHandler(secret)

        self.route()

    @_handler.add(MessageEvent, message=TextMessage)
    def callback(self):
        signature = request.headers['X-Line-Signature']

        body = request.get_data(as_text=True)
        self._app.logger.info("Request body: " + body)

        print(body, signature)
        self._handler.handle(body, signature)

        return 'OK'

    # @handler.add(MessageEvent, message=TextMessage)
    def pretty_echo(self, event):
        self._api.reply_message(event.reply_token, TextSendMessage(text='text'))

    def route(self):
        self._handler.add(MessageEvent, message=TextMessage)

        self._app.add_url_rule('/callback', methods=['POST'], view_func=self.callback)

    def run(self, port=8080):
        self._app.run(port=port)
