from bitmex_websocket import BitMEXWebsocket
import logging, pprint, bitmex, configparser
from time import sleep

# Basic use of websocket.
def run():
    logger = setup_logger()
    config = configparser.ConfigParser()
    config.read('config.ini')
    client = bitmex.bitmex(api_key=config['AUTH']['api_key'],
        api_secret=config['AUTH']['api_secret'])

    # Instantiating the WS will make it connect. Be sure to add your api_key/api_secret.
    ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD",
                         api_key=config['AUTH']['api_key'],
                         api_secret=config['AUTH']['api_secret'])

    # logger.info("Instrument data: %s" % ws.get_instrument())

    a1 = config['VALUES']['a1']
    a2 = config['VALUES']['a2']
    aQty = config['VALUES']['aQty']
    b1 = config['VALUES']['b1']
    b2 = config['VALUES']['b2']
    bQty = config['VALUES']['bQty']

    # Run forever
    triggered = False
    try:

        (body, response) = client.Order.Order_new(
                symbol='XBTUSD', orderQty=aQty, price="8999",
                contingencyType="OneTriggersTheOther", clOrdLinkID="Triggered").result()
        while(ws.ws.sock.connected):
            price = ws.get_ticker()
            print(price['mid'])
            if not triggered and price['mid'] > float(a1):
                (body, response) = client.Order.Order_new(
                    symbol='XBTUSD', orderQty=aQty, price=a1,
                    contingencyType="OneTriggersTheOther", clOrdLinkID="Triggered").result()
                (body, response) = client.Order.Order_new(
                    symbol='XBTUSD', orderQty=aQty, price=a2, side="Sell",
                    clOrdLinkID="Triggered").result()
                triggered = True
            elif not triggered and price['mid'] < float(b1):
                (body, response) = client.Order.Order_new(
                    symbol='XBTUSD', orderQty=bQty, price=b1, side="Sell",
                    contingencyType="OneTriggersTheOther", clOrdLinkID="Triggered").result()
                (body, response) = client.Order.Order_new(
                    symbol='XBTUSD', orderQty=bQty, price=b2,
                    clOrdLinkID="Triggered").result()
                triggered = True

            pp = pprint.PrettyPrinter(indent=4)
            sleep(1)
    except KeyboardInterrupt as e:
        print(client.Order.Order_cancelAll().result())


def setup_logger():
    # Prints logger info to terminal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Change this to DEBUG if you want a lot more info
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    run()
