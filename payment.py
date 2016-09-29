#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta

__all__ = ['PayLine', 'PayLineAskJournal']


class PayLineAskJournal:
    __metaclass__ = PoolMeta
    __name__ = 'account.move.line.pay.ask_journal'

    approve = fields.Boolean('Approve payments',
        help='Create payments in approved state')


class PayLine:
    __metaclass__ = PoolMeta
    __name__ = 'account.move.line.pay'

    def do_pay(self, action):
        pool = Pool()
        Payment = pool.get('account.payment')
        action, data = super(PayLine, self).do_pay(action)
        if self.ask_journal.approve:
            payments = Payment.browse(data['res_id'])
            Payment.approve(payments)

        return action, data
