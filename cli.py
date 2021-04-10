import click
import os
import time
import glob
import crawler.twse as twse
import crawler.price as price
import crawler.cmoney as cmoney
import pandas as pd
from datetime import datetime
from xlsx import twse as xtwse

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
    pass


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

    click.echo(f'read {year}-{m}')

    data = twse.month_revenue(year, month)
    data.to_csv(os.path.join(dir, f"{year}-{m}.csv"), index=False, encoding='utf_8_sig')

    click.echo(f"save {year}-{m}")


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

    click.echo(f"save dividend {year}")


# 合併
@cli.command('merge')
@click.option('-i', '--input', type=click.Path(), help="輸入路徑")
@click.option('-o', '--out', type=click.Path(), help="輸出路徑")
@click.option('-t', '--type', default='all', type=click.Choice(MERGE_TYPE, case_sensitive=False), help="合併類型")
def merge(input, out, type):
    def m(type):
        if type == BALANCE_SHEET:
            click.echo("合併 資產負債表...")
            xtwse.balance_sheet(os.path.join(input, type), out)
            click.echo("資產負債表 合併完成")

        if type == CONSOLIDATED_INCOME_STATEMENT:
            click.echo("合併 綜合損益表...")
            xtwse.consolidated_income_statement(os.path.join(input, type), out)
            click.echo("綜合損益表 合併完成")

        if type == CASH_FLOW_STATEMENT:
            click.echo("合併 現金流量表...")
            xtwse.cash_flow_statement(os.path.join(input, type), out)
            click.echo("現金流量表 合併完成")

        if type == CHANGES_IN_EQUITY:
            click.echo("合併 權益變動表...")
            xtwse.changes_inEquity(os.path.join(input, type), out)
            click.echo("權益變動表 合併完成")

        if type == MONTH_REVENUE:
            click.echo("合併 月營收...")
            xtwse.month_revenue(os.path.join(input, type), out)
            click.echo("月營收 合併完成")

        if type == DIVIDEND:
            click.echo("合併 股利...")
            xtwse.dividend(os.path.join(input, type), out)
            click.echo("股利 合併完成")

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
    click.echo("合併 財報...")

    data = {}
    f = os.path.join(input, "財報.xlsx")

    for p in glob.glob(os.path.join(input, "*.csv")):
        name = os.path.basename(p).split('.')[0]
        click.echo(f"read {name}...")

        data[name] = pd.read_csv(p)

    with pd.ExcelWriter(f) as writer:
        for k, v in data.items():
            click.echo(f"save {k}...")
            v.to_excel(writer, sheet_name=k, index=False)

    click.echo("開始合併財報")
    writer.close()
    click.echo("合併財報完成")


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

            click.echo(f"save {name} {date}")


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

        click.echo(f"save {code} {date}")


# 財報
def _get_financial(year, season, outpath, type):
    if season == 0:
        seasons = [4, 3, 2, 1]
    else:
        seasons = [season]

    for season in seasons:
        click.echo(f"read {type} {year}-{season}")
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
                click.echo(f"{type} {code} not found")
            else:
                for k, v in d.items():
                    dir = os.path.join(outPath, k)
                    f = os.path.join(dir, f"{code}.csv")

                    if os.path.exists(f):
                        continue

                    if os.path.exists(dir) == False:
                        os.mkdir(dir)

                    v.to_csv(f, index=False, encoding='utf_8_sig')

                    click.echo(f"save {type} {code} {k}")

            time.sleep(6)


if __name__ == '__main__':
    cli()
