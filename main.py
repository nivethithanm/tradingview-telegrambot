import os
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import requests
import json
import subprocess

path = os.path.abspath(os.getcwd())


class TradingViewBot:
    def __init__(self):
        self.bot = webdriver.Firefox()

    def login(self):
        bot = self.bot
        bot.get("file:///"+ str(path)+ "/index.html")
        time.sleep(10)
                      
    def getScreen(self):
        self.bot.save_screenshot(str(path) + '/screenshot.png')
        
    def close(self):
        self.bot.close()

class telegram_chatbot():
    
    def __init__(self, token):
        self.token = token
        self.base = "https://api.telegram.org/bot{}/".format(self.token)

    def get_updates(self, offset=None):
        url = self.base + "getUpdates?timeout=100"
        if offset:
            url = url + "&offset={}".format(offset + 1)
        r = requests.get(url)
        return json.loads(r.content)

    def send_message(self, msg, chat_id):
        url = self.base + "sendMessage?chat_id={}&text={}".format(chat_id, msg)
        if msg is not None:
            requests.get(url)

    def make_reply(self,msg):
        reply = None
        if msg is not None:
            reply = msg
        return reply
    
    def getHtml(self, symbol, interval):

        html = """
<html>
<head>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js">
</script>
</head>
<body>
<div class="tradingview-widget-container" id="tradingview_c39ad"></div>
<script>
LoadChart("""+ "\"" + str(symbol) + "\"" + ',' + "\"" + str(interval) + "\"" + """);
function LoadChart(symbol, interval){
new TradingView.widget(
  {
  "width": 980,
  "height": 610,
  "symbol": symbol,
  "interval": interval,
  "timezone": "Etc/UTC",
  "theme": "light",
  "style": "1",
  "locale": "in",
  "toolbar_bg": "#f1f3f6",
  "enable_publishing": false,
  "allow_symbol_change": true,
  "container_id": "tradingview_c39ad"
	});
}
</script>
</body>
</html>
"""
        with open(str(path)+ "/index.html", "w+") as file:
            file.write(html)

    
    def botFunctions(self,symbol, interval):
        self.getHtml(symbol, interval)
        instanc = TradingViewBot()
        instanc.login()
        instanc.getScreen()
        instanc.close()
    
    def getPlot(self,symbol, interval, chat_id):
        self.botFunctions(symbol, interval)
        command = 'curl -s -X POST https://api.telegram.org/bot' + str(self.token) + '/sendPhoto -F chat_id=' + str(chat_id) + ' -F photo=@' + str(os.path.abspath(os.getcwd())) + '/screenshot.png'
        subprocess.call(command.split(' '))
        return   
    
    def make_plot(self,msg,from_):
        list_ = msg.split(',')
        if(len(list_) == 3):
            self.getPlot(str(list_[1]), str(list_[2]),from_)
            return
    
token = 'YOUR_ACCESS_TOKEN'
bot = telegram_chatbot(token)

update_id = None
while True:
    updates = bot.get_updates(offset=update_id)
    updates = updates["result"]
    if updates:
        for item in updates:
            update_id = item["update_id"]
            try:
                message = str(item["message"]["text"])
            except:
                message = None
            from_ = item["message"]["from"]["id"]
            if (message.find('/getPlot') != -1):
                bot.make_plot(message,from_)
            elif (message.find('/help') != -1):
                bot.send_message('Syntax:\nUse this function to get plots /getPlot,Ticker1,Ticker2,StartTime,EndTime\nNote: Dates should be in detail DD/MM/YYYY/hh/mm format', from_)
            else:
                bot.send_message('Syntax:\nUse this function to get plots /getPlot,Ticker1,Ticker2,StartTime,EndTime\nNote: Dates should be in detail DD/MM/YYYY/hh/mm format', from_)           
