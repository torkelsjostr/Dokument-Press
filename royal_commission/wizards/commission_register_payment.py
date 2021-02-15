from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}


class CommissionRegisterPayment(models.TransientModel):
    _name = "commission.register.payment"
    _description = "Contains the logic shared between models which allows to register payments"

    commission_ids = fields.Many2many('commission', string='Commissions', copy=False)
    multi = fields.Boolean(string='Multi',
                           help='Technical field indicating if the registering payment will generate multiple payments or not.')

    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type', required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True, oldname="payment_method",
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
        "Check: Pay bill by check and print it from Odoo.\n"\
        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"\
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    payment_method_code = fields.Char(related='payment_method_id.code',
        help="Technical field used to adapt the interface to the payment type selected.", readonly=True)

    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])
    partner_id = fields.Many2one('res.partner', string='Partner')
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])

    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark commissions as fully paid')], default='open', string="Payment Difference Handling", copy=False)
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", domain=[('deprecated', '=', False)], copy=False)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help='Change label of the counterpart that will hold the payment difference',
        default='Write-Off')
    partner_bank_account_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account")
    show_partner_bank_account = fields.Boolean(compute='_compute_show_partner_bank', help='Technical field used to know whether the field `partner_bank_account_id` needs to be displayed or not in the payments form views')
    show_communication_field = fields.Boolean(compute='_compute_show_communication_field')

    @api.depends('commission_ids.partner_id')
    def _compute_show_communication_field(self):
        """ We allow choosing a common communication for payments if the group
        option has been activated, and all the invoices relate to the same
        partner.
        """
        for record in self:
            record.show_communication_field = len(record.commission_ids) == 1 and len(record.mapped('commission_ids.partner_id.commercial_partner_id')) == 1


    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(CommissionRegisterPayment, self)._onchange_journal()
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.invoice'].browse(active_ids)
        self.amount = abs(self._compute_payment_amount(invoices))
        return res

    def _get_payment_group_key(self, inv):
        """Define group key to group invoices in payments."""
        if inv.partner_id.type == 'invoice':
            partner_id = inv.partner_id.id
        else:
            partner_id = inv.commercial_partner_id.id
        account_id = inv.account_id.id
        invoice_type = MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type]
        recipient_account = inv.partner_bank_id
        return (partner_id, account_id, invoice_type, recipient_account)

    @api.multi
    def _prepare_payment_vals(self, commissions):
        '''Create the payment values.

        :param invoices: The invoices that should have the same commercial partner and the same type.
        :return: The payment values as a dictionary.
        '''
        amount = self._compute_payment_amount(commissions=commissions) if self.multi else self.amount
        payment_type = ('inbound' if amount > 0 else 'outbound') if self.multi else self.payment_type
        pmt_communication = self._prepare_communication(commissions)

        partner_id = commissions[0].partner_id

        values = {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': pmt_communication,
            'payment_type': payment_type,
            'amount': abs(amount),
            'currency_id': self.currency_id.id,
            'partner_id': partner_id.id,
            'partner_type': 'supplier',
            'multi': False,
            'payment_difference_handling': self.payment_difference_handling,
            'writeoff_account_id': self.writeoff_account_id.id,
            'writeoff_label': self.writeoff_label,
        }
        return values

    @api.multi
    def get_payments_vals(self):
        '''Compute the values for payments.

        :return: a list of payment values (dictionary).
        '''
        if self.multi:
            groups = self._groupby_invoices()
            return [self._prepare_payment_vals(invoices) for invoices in groups.values()]
        return [self._prepare_payment_vals(self.commission_ids)]

    def _prepare_communication(self, commissions):
        '''Define the value for communication field
        Append all invoice's references together.
        '''
        return self.show_communication_field and self.communication \
                or self.group_invoices and ' '.join([inv.name for inv in commissions]) \
                or commissions[0].reference # in this case, invoices contains only one element, since group_invoices is False

    @api.multi
    def create_payments(self):
        '''Create payments according to the invoices.
        Having invoices with different commercial_partner_id or different type (Vendor bills with customer invoices)
        leads to multiple payments.
        In case of all the invoices are related to the same commercial_partner_id and have the same type,
        only one payment will be created.

        :return: The ir.actions.act_window to show created payments.
        '''
        Payment = self.env['account.payment']
        payments = Payment
        for payment_vals in self.get_payments_vals():
            payments += Payment.create(payment_vals)
        payments.post()

        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        self.commission_ids.write({
            'state': 'paid',
            'paid_amount': sum(payments.mapped('amount')),
            'paid_currency_id': payments[0].currency_id.id,
            'payment_ids': [(4, payments.id)],
        })
        return action_vals

    @api.model
    def default_get(self, fields):
        rec = super(CommissionRegisterPayment, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected commissions ids
        if not active_ids or active_model != 'commission':
            return rec

        commissions = self.env['commission'].browse(active_ids)

        # Check all commissions are open
        if any(commission.state != 'confirm' for commission in commissions):
            raise UserError(_("You can only register payments for confirmed commissions"))
        # Check all commissions have the same currency
        if any(commission.currency_id != commissions[0].currency_id for commission in commissions):
            raise UserError(_("In order to pay multiple commissions at once, they must use the same currency."))

        currency = commissions[0].currency_id

        total_amount = self._compute_payment_amount(commissions=commissions, currency=currency)

        rec.update({
            'amount': abs(total_amount),
            'currency_id': currency.id,
            'payment_type': 'outbound',
            'partner_id': commissions[0].author_id.partner_id.id,
            'partner_type': 'supplier',
            'commission_ids': [(6, 0, commissions.ids)],
            'communication': ' '.join([ref for ref in commissions.mapped('name') if ref])[:2000]
        })
        return rec

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if self.amount < 0:
            raise ValidationError(_('The payment amount cannot be negative.'))

    @api.model
    def _get_method_codes_using_bank_account(self):
        return []

    @api.depends('payment_method_code')
    def _compute_show_partner_bank(self):
        """ Computes if the destination bank account must be displayed in the payment form view. By default, it
        won't be displayed but some modules might change that, depending on the payment type."""
        for payment in self:
            payment.show_partner_bank_account = payment.payment_method_code in self._get_method_codes_using_bank_account() and not self.multi

    @api.multi
    @api.depends('payment_type', 'journal_id')
    def _compute_hide_payment_method(self):
        for payment in self:
            if not payment.journal_id or payment.journal_id.type not in ['bank', 'cash']:
                payment.hide_payment_method = True
                continue
            journal_payment_methods = payment.payment_type == 'inbound'\
                and payment.journal_id.inbound_payment_method_ids\
                or payment.journal_id.outbound_payment_method_ids
            payment.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.depends('commission_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        for pay in self.filtered(lambda p: p.commission_ids):
            payment_amount = pay.amount
            pay.payment_difference = pay._compute_payment_amount() - payment_amount

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            payment_methods_list = payment_methods.ids

            default_payment_method_id = self.env.context.get('default_payment_method_id')
            if default_payment_method_id:
                # Ensure the domain will accept the provided default value
                payment_methods_list.append(default_payment_method_id)
            else:
                self.payment_method_id = payment_methods and payment_methods[0] or False

            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods_list)]}}
        return {}

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        pass

    def _compute_journal_domain_and_types(self):
        journal_type = ['bank', 'cash']
        domain = []
        if self.currency_id.is_zero(self.amount) and hasattr(self, "has_invoices"):
            # In case of payment with 0 amount, allow to select a journal of type 'general' like
            # 'Miscellaneous Operations' and set this journal by default.
            journal_type = ['general']
            self.payment_difference_handling = 'reconcile'
        else:
            if self.payment_type == 'inbound':
                domain.append(('at_least_one_inbound', '=', True))
            else:
                domain.append(('at_least_one_outbound', '=', True))
        return {'domain': domain, 'journal_types': set(journal_type)}

    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        jrnl_filters = self._compute_journal_domain_and_types()
        journal_types = jrnl_filters['journal_types']
        domain_on_types = [('type', 'in', list(journal_types))]
        if self.journal_id.type not in journal_types:
            self.journal_id = self.env['account.journal'].search(domain_on_types, limit=1)
        return {'domain': {'journal_id': jrnl_filters['domain'] + domain_on_types}}

    @api.onchange('currency_id')
    def _onchange_currency(self):
        self.amount = abs(self._compute_payment_amount())

        # Set by default the first liquidity journal having this currency if exists.
        if self.journal_id:
            return
        journal = self.env['account.journal'].search(
            [('type', 'in', ('bank', 'cash')), ('currency_id', '=', self.currency_id.id)], limit=1)
        if journal:
            return {'value': {'journal_id': journal.id}}

    @api.multi
    def _compute_payment_amount(self, commissions=None, currency=None):
        '''Compute the total amount for the payment wizard.

        :param invoices: If not specified, pick all the invoices.
        :param currency: If not specified, search a default currency on wizard/journal.
        :return: The total amount to pay the invoices.
        '''

        # Get the payment invoices
        if not commissions:
            commissions = self.commission_ids

        # Get the payment currency
        payment_currency = currency
        if not payment_currency:
            payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or commissions and commissions[0].currency_id

        total = self.journal_id.company_id.currency_id._convert(
            sum(commissions.mapped('total_commission')),
            payment_currency,
            self.env.user.company_id,
            self.payment_date or fields.Date.today()
        )
        return total
