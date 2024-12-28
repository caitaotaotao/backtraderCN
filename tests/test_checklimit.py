import pandas as pd
from backtrader.cerebro import Cerebro
from backtrader.feeds.pandafeed import PandasData
from backtrader.strategy import Strategy


signal = pd.DataFrame(data={
    'datetime': ['2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04', '2024-10-05', '2024-10-06', '2024-10-07',
                 '2024-10-08', '2024-10-09'],
    'close': [10, 12, 12.5, 12.4, 13, 14.3, 15, 13, 13.5],
    'signal': [1, 1, 0, -1, 1, 0, 0, -1, 0],
})
signal['datetime'] = pd.to_datetime(signal['datetime'])
signal.set_index('datetime', inplace=True)


class myData(PandasData):
    lines = ('signal', )
    params = (('signal', -1),)


class TestStrategy(Strategy):
    def __init__(self):
        self.signal = self.data.signal
        self.dataclose = self.data.close
        self.order = None

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if not self.position:
            if self.signal == 1:
                self.order = self.buy(price=self.dataclose[1], limitype=0)
                self.log('BUY CREATE, %.2f' % self.dataclose[1])
            elif self.signal == -1:
                self.order = self.sell(price=self.dataclose[1], limitype=0)
                self.log('SELL CREATE, %.2f' % self.dataclose[1])
            else:
                pass


def main():
    cerebro = Cerebro()

    data_signal = myData(dataname=signal)
    cerebro.adddata(data_signal)
    cerebro.broker.set_checklimit(True)

    cerebro.broker.set_cash(1000000)
    cerebro.addstrategy(TestStrategy)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    main()

