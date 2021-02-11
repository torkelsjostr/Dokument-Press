/* Author      : Niova Group ApS (<https://niova.dk/>) */
/* Copyright(c): 2018-Present Niova Group ApS */
/* License URL : https://invoice-scan.com/license/ */
/* All Rights Reserved. */
odoo.define('invoice.scan.sync.button', function (require) {
"use strict";
var core = require('web.core');
var rpc = require('web.rpc');

var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.$buttons) {
                let refresh_button = this.$buttons.find('.oe_sync_invoice_scan');
                refresh_button && refresh_button.click(this.proxy('sync_button'));
            }
        },
        sync_button: function () {
	        rpc.query({
				   model: 'invoicescan.scheduler',			
				   method: 'process_scanned_vouchers',
				   args: [],		
				}).then(function(data){
				   console.log('sync done');
				});			
	    }
    });
})
