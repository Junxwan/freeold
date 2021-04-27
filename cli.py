import click
import os
import time
import glob
import logging
import smtplib
import crawler.twse as twse
import crawler.price as price
import crawler.cmoney as cmoney
import crawler.news as cnews
import pandas as pd
from datetime import datetime, timedelta
from xlsx import twse as xtwse
from jinja2 import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 月營收
MONTH_REVENUE = 'month_revenue'

# 資產負債表
BALANCE_SHEET = 'balance_sheet'

# 綜合損益表
CONSOLIDATED_INCOME_STATEMENT = 'consolidated_income_statement'

# 現金流量表
CASH_FLOW_STATEMENT = 'cash_flow_statement'

# 權益變動表
CHANGES_IN_EQUITY = 'changes_in_equity'

# 股利
DIVIDEND = 'dividend'

# 財報種類
FINANCIAL_TYPE = ['all', BALANCE_SHEET, CONSOLIDATED_INCOME_STATEMENT, CASH_FLOW_STATEMENT, CHANGES_IN_EQUITY]

# 合併種類
MERGE_TYPE = ['all', MONTH_REVENUE, BALANCE_SHEET, CONSOLIDATED_INCOME_STATEMENT, CASH_FLOW_STATEMENT,
              CHANGES_IN_EQUITY,
              DIVIDEND]

year = datetime.now().year
month = datetime.now().month

if month == 1:
    month = 12
else:
    month = month - 1


@click.group()
def cli():
    dir = os.path.join(os.getcwd(), 'log')

    if os.path.exists(dir) == False:
        os.mkdir(dir)

    filename = os.path.join(dir, datetime.now().strftime(f"%Y-%m-%d-cli.log"))
    log = logging.getLogger()

    for hdlr in log.handlers[:]:
        log.removeHandler(hdlr)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=filename)


# 月營收
@cli.command('month_revenue')
@click.option('-y', '--year', default=0, help="年")
@click.option('-m', '--month', default=0, help="月")
@click.option('-o', '--outPath', type=click.Path(), help="輸出路徑")
def month_revenue(year, month, outpath):
    if month == 0:
        month = datetime.now().month

        if month == 1:
            month = 12
        else:
            month = month - 1

    if year == 0:
        year = datetime.now().year

        if datetime.now().month == 1:
            year = year - 1

    m = "%02d" % month

    dir = os.path.join(outpath, 'month_revenue', str(year))

    if os.path.exists(dir) == False:
        os.mkdir(dir)

    log(f'read month_revenue {year}-{m}')

    data = twse.month_revenue(year, month)
    data.to_csv(os.path.join(dir, f"{year}-{m}.csv"), index=False, encoding='utf_8_sig')

    log(f"save month_revenue {year}-{m}")


# 財報
@cli.command('financial')
@click.option('-y', '--year', default=0, help="年")
@click.option('-s', '--season', default=0, help="季")
@click.option('-o', '--outPath', type=click.Path(), help="輸出路徑")
@click.option('-t', '--type', default='all', type=click.Choice(FINANCIAL_TYPE, case_sensitive=False), help="財報類型")
def get_financial(year, season, outpath, type):
    if year == 0:
        year = datetime.now().year

        if datetime.now().month < 5:
            year = year - 1

    if type == 'all':
        FINANCIAL_TYPE.remove('all')

        for t in FINANCIAL_TYPE:
            _get_financial(year, season, outpath, t)
    else:
        _get_financial(year, season, outpath, type)


# 股利
@cli.command('dividend')
@click.option('-y', '--year', default=year, help="年")
@click.option('-o', '--outPath', type=click.Path(), help="輸出路徑")
def dividend(year, outpath):
    outPath = os.path.join(outpath, "dividend")
    data = twse.dividend(year)
    data.to_csv(os.path.join(outPath, f"{year}.csv"), index=False, encoding='utf_8_sig')

    log(f"save dividend {year}")


# 合併
@cli.command('merge')
@click.option('-i', '--input', type=click.Path(), help="輸入路徑")
@click.option('-o', '--out', type=click.Path(), help="輸出路徑")
@click.option('-t', '--type', default='all', type=click.Choice(MERGE_TYPE, case_sensitive=False), help="合併類型")
def merge(input, out, type):
    def m(type):
        if type == BALANCE_SHEET:
            log("合併 資產負債表...")
            xtwse.balance_sheet(os.path.join(input, type), out)
            log("資產負債表 合併完成")

        if type == CONSOLIDATED_INCOME_STATEMENT:
            log("合併 綜合損益表...")
            xtwse.consolidated_income_statement(os.path.join(input, type), out)
            log("綜合損益表 合併完成")

        if type == CASH_FLOW_STATEMENT:
            log("合併 現金流量表...")
            xtwse.cash_flow_statement(os.path.join(input, type), out)
            log("現金流量表 合併完成")

        if type == CHANGES_IN_EQUITY:
            log("合併 權益變動表...")
            xtwse.changes_inEquity(os.path.join(input, type), out)
            log("權益變動表 合併完成")

        if type == MONTH_REVENUE:
            log("合併 月營收...")
            xtwse.month_revenue(os.path.join(input, type), out)
            log("月營收 合併完成")

        if type == DIVIDEND:
            log("合併 股利...")
            xtwse.dividend(os.path.join(input, type), out)
            log("股利 合併完成")

    if type == 'all':
        MERGE_TYPE.remove('all')

        for t in MERGE_TYPE:
            m(t)
    else:
        m(type)


# 合併財報
@cli.command('merge_financial')
@click.option('-i', '--input', type=click.Path(), help="輸入路徑")
def merge_financial(input):
    log("合併 財報...")

    data = {}
    f = os.path.join(input, "財報.xlsx")

    for p in glob.glob(os.path.join(input, "*.csv")):
        name = os.path.basename(p).split('.')[0]
        log(f"read {name}...")

        data[name] = pd.read_csv(p)

    with pd.ExcelWriter(f) as writer:
        for k, v in data.items():
            log(f"save {k}...")
            v.to_excel(writer, sheet_name=k, index=False)

    log("開始合併財報")
    writer.close()
    log("合併財報完成")


# 面板報價
@cli.command('wits_view')
@click.option('-o', '--out', type=click.Path(), help="輸出路徑")
def wits_view(out):
    out = os.path.join(out, 'wits_view')
    data = price.wits_view()

    for name, item in data.items():
        for date, table in item.items():
            dir = os.path.join(out, name)

            if os.path.exists(dir) == False:
                os.makedirs(dir)

            table.to_csv(os.path.join(dir, f"{date}.csv"), index=False, encoding='utf_8_sig')

            log(f"save {name} {date}")


# SP 500
@cli.command('sp500')
@click.option('-c', '--code', type=click.STRING, help="代碼")
@click.option('-o', '--out', type=click.Path(), help="輸出路徑")
def sp500(code, out):
    for date, table in cmoney.sp500(code).items():
        dir = os.path.join(out, 'sp500', code)

        if os.path.exists(dir) == False:
            os.makedirs(dir)

        table.to_csv(os.path.join(dir, f"{date}.csv"), index=False, encoding='utf_8_sig')

        log(f"save {code} {date}")


# 新聞
@cli.command('news')
@click.option('-e', '--email', type=click.STRING, help="email")
@click.option('-h', '--hours', type=click.INT, help="小時")
@click.option('-l', '--login_email', type=click.STRING, help="發送者")
@click.option('-p', '--login_pwd', type=click.STRING, help="發送密碼")
def news(email, hours, login_email, login_pwd):
    log('start news')

    date = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

    data = [
        ['聯合報-產經', cnews.udn('6644', date)],
        ['聯合報-股市', cnews.udn('6645', date)],
        ['蘋果-財經地產', cnews.appledaily(date)],
        ['中時', cnews.chinatimes(date)],
        ['科技新報', cnews.technews(date)],
        ['經濟日報-產業熱點', cnews.money_udn('5591', '5612', date)],
        ['經濟日報-生技醫藥', cnews.money_udn('5591', '10161', date)],
        ['經濟日報-企業CEO', cnews.money_udn('5591', '5649', date)],
        ['經濟日報-總經趨勢', cnews.money_udn('10846', '10869', date)],
        ['經濟日報-2021投資前瞻', cnews.money_udn('10846', '121887', date)],
        ['經濟日報-國際焦點', cnews.money_udn('5588', '5599', date)],
        ['經濟日報-美中貿易戰', cnews.money_udn('5588', '10511', date)],
        ['經濟日報-金融脈動', cnews.money_udn('12017', '5613', date)],
        ['經濟日報-市場焦點', cnews.money_udn('5590', '5607', date)],
        ['經濟日報-集中市場', cnews.money_udn('5590', '5710', date)],
        ['經濟日報-櫃買市場', cnews.money_udn('5590', '11074', date)],
        ['經濟日報-國際期貨', cnews.money_udn('11111', '11114', date)],
        ['經濟日報-國際綜合', cnews.money_udn('12925', '121854', date)],
        ['經濟日報-外媒解析', cnews.money_udn('12925', '12937', date)],
        ['經濟日報-產業動態', cnews.money_udn('12925', '121852', date)],
        ['經濟日報-產業分析', cnews.money_udn('12925', '12989', date)],
        ['工商時報-產業', cnews.ctee(date, 'industry')],
        ['工商時報-科技', cnews.ctee(date, 'tech')],
        ['工商時報-國際', cnews.ctee(date, 'global')],
        ['工商時報-兩岸', cnews.ctee(date, 'china')],
        ['證交所-即時重大訊息', twse.news(date)],
    ]

    log('get news ok')

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = render('email.html',
                  news=[{'title': v[0], 'news': v[1]} for v in data],
                  date=now,
                  end_date=date,
                  )

    content = MIMEMultipart()
    content["from"] = "bot.junx@gmail.com"
    content["subject"] = f"財經新聞-{now}"
    content["to"] = email
    content.attach(MIMEText(html, 'html'))

    log(f"login email: {login_email}")
    log(f"send email: {email}")

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(login_email, login_pwd)
            smtp.send_message(content)
            log('set news email ok')
        except Exception as e:
            error(f"set news email error {e.__str__()}")


# 財報
def _get_financial(year, season, outpath, type):
    if season == 0:
        seasons = [4, 3, 2, 1]
    else:
        seasons = [season]

    for season in seasons:
        log(f"read {type} {year}-{season}")
        for code in twse.season_codes(year, season):
            outPath = os.path.join(outpath, type)

            if os.path.exists(os.path.join(outPath, f"{year}Q{season}", f"{code}.csv")):
                continue

            def get(code, year, season):
                return []

            if type == BALANCE_SHEET:
                get = twse.balance_sheet
            elif type == CONSOLIDATED_INCOME_STATEMENT:
                get = twse.consolidated_income_statement
            elif type == CASH_FLOW_STATEMENT:
                get = twse.cash_flow_statement
            elif type == CHANGES_IN_EQUITY:
                get = twse.changes_in_equity

            d = get(code, year, season)

            if len(d) == 0:
                log(f"{type} {code} not found")
            else:
                for k, v in d.items():
                    dir = os.path.join(outPath, k)
                    f = os.path.join(dir, f"{code}.csv")

                    if os.path.exists(f):
                        continue

                    if os.path.exists(dir) == False:
                        os.mkdir(dir)

                    v.to_csv(f, index=False, encoding='utf_8_sig')

                    log(f"save {type} {code} {k}")

            time.sleep(6)


def log(msg):
    logging.info(msg)
    click.echo(msg)


def error(msg):
    logging.error(msg)
    click.echo(msg)


def _read_template(html):
    with open(os.path.join(f"./template/{html}")) as template:
        return template.read()


def render(html, **kwargs):
    return Template(
        _read_template(html)
    ).render(**kwargs)


if __name__ == '__main__':
    cli()
