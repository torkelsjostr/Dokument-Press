# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
import sys
from odoo import models, api, tools
import threading
import logging

_logger = logging.getLogger(__name__)


class InvoiceScanScheduler(models.AbstractModel):
    _name = 'invoicescan.scheduler'
    _description = 'Invoice Scan Scheduler'
    
    @api.model
    def process_scanned_vouchers(self):
        threaded = threading.Thread(target=self._process_scanned_vouchers(), args=())
        threaded.start()

    @api.model
    def _process_scanned_vouchers(self):
        with api.Environment.manage():
            # Open new thread
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            scheduler_cron = self.sudo().env.ref('niova_invoice_scan.ir_crone_invoice_scan_service')
            # Avoid to run the scheduler multiple times in the same time
            try:
                with tools.mute_logger('odoo.sql_db'):
                    self._cr.execute("SELECT id FROM ir_cron WHERE id = %s FOR UPDATE NOWAIT", (scheduler_cron.id,))
            except Exception:
                _logger.info('Attempt to run invoice scan scheduler aborted, as already running')
                self._cr.rollback()
                self._cr.close()
                return {}
            self.sudo().run_invoice_scan()
            self._cr.close()
    
    @api.model
    def run_invoice_scan(self):
        try:
            # Set Super User
            self = self.sudo()

            # Upload raw vouchers
            self.env['invoicescan.voucher'].upload_vouchers()

            # Get or update scanned vouchers
            self.env['invoicescan.voucher'].receive_scanned_vouchers()
            
            # Generate invoices for ready vouchers
            self.env['account.invoice'].generate_invoices()
            
            # Rematch draft vendor bills
            self.env['account.invoice'].rematch_partner()
        except:
            _logger.exception(sys.exc_info()[1])