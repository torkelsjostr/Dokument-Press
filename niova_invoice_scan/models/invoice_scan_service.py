# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
import sys
from odoo import api, fields, models, _
import requests
from odoo.http import request
from datetime import datetime, timedelta
import werkzeug
import logging

_logger = logging.getLogger(__name__)

TIMEOUT = 20
INVOICE_SCAN_CLIENT_ID = '92c8e0d6-f232-4c39-83d7-00198e92e12e'
INVOICE_SCAN_BASE_URL = 'https://api.invoice-scan.com/'
INVOICE_SCAN_AUTH_ENDPOINT = 'oauth/authorize'
INVOICE_SCAN_TOKEN_ENDPOINT = 'oauth/token'

ODOO_REDIRECT_URI = 'invoice_scan/authentication'


class InvoiceScanService(models.AbstractModel):
    _name = 'invoicescan.service'
    _description = 'Invoice Scan Service'
    
    expires_in = None
    access_token = str()
    refresh_token = str()
    token_type = str()
    organization = str()
    client_secrect = str()
    
    @api.model
    def redirect_to_invoicescan(self):
        authorize_uri = self._get_authorize_uri('')
        return {
            'type': 'ir.actions.act_url',
            'url': authorize_uri,
            'target': 'new'
        }
        
    @api.multi
    def get_access_token(self):
        if not self._get_refresh_token() and not self.get_organization():
            self._issue_access_token()
        elif not self._get_access_token() or self._get_expires_datetime() < (datetime.now() + timedelta(minutes=1)):
            self._refresh_access_token()
        return self._get_access_token()
        
    @api.multi
    def _issue_access_token(self):
        uri, headers, data = self._get_token_request('invoice_scan', '')
        try:
            _, reponse, _ = self.request(uri, params=data, headers=headers, request_type='POST')
            content = reponse.json()
        except:
            error_msg = "Something went wrong issue access token. Maybe the Authorization setup is invalid."
            raise self.env['res.config.settings'].get_config_warning(error_msg)
        
        self._set_access_token(content.get('access_token', ''), content.get('token_type', ''))
        self._set_expires_datetime(int(content.get('expires_in', 0)))
        self._set_refresh_token(content.get('refresh_token', ''))
        self._set_organization(content.get('organization_id', ''))
        self._set_setting('invoice_scan_active', True)
        self.env.cr.commit()
    
    @api.multi
    def _refresh_access_token(self):
        uri, headers, data = self._get_token_request('refresh_token', '')
        try:
            _, reponse, _ = self.request(uri, params=data, headers=headers, request_type='POST')
            content = reponse.json()
        except:
            self.reset_tokens()
            error_msg = "Something went wrong issue access token. Maybe the Authorization setup is invalid."
            raise self.env['res.config.settings'].get_config_warning(error_msg)
        
        self._set_access_token(content.get('access_token', ''), content.get('token_type', ''))
        self._set_refresh_token(content.get('refresh_token', ''))
        self._set_expires_datetime(int(content.get('expires_in', 0)))
            
    @api.multi
    def request(self, uri, params={}, headers={}, request_type='GET'):
        _logger.debug("Uri: %s - Type : %s - Headers: %s - Params : %s !", (uri, type, headers, params))

        request_time = fields.Datetime.now()
        try:
            if request_type.upper() in ('GET', 'DELETE'):
                response = requests.request(request_type.lower(), uri, params=params, headers=headers, timeout=TIMEOUT)
            elif request_type.upper() in ('POST', 'PATCH', 'PUT'):
                response = requests.request(request_type.lower(), uri, data=params, headers=headers, timeout=TIMEOUT)
            else:
                raise Exception(_('Method not supported [%s] not in [GET, POST, PUT, PATCH or DELETE]!') % (request_type))
            response.raise_for_status()
        except requests.HTTPError as error:
            error_message = 'Bad Invoice Scan request : {error_content}'.format(error_content=error.response.content)
            _logger.exception(error_message)
            raise Exception(_(error_message))
        except:
            error_message  = 'Something went wrong with the request to Invoice Scan request. Error message: {error}'.format(error=sys.exc_info()[1]) 
            _logger.exception(error_message)
            raise Exception(_(error_message))

        return (self._get_status(response), response, self._get_request_time(response, request_time))
    
    @api.multi
    def _get_token_request(self, grant, scope):
        uri = INVOICE_SCAN_BASE_URL + INVOICE_SCAN_TOKEN_ENDPOINT
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        data = {
            'scope': scope,
            'client_id': INVOICE_SCAN_CLIENT_ID,
            'client_secret': self._get_client_secret(),
            'grant_type': grant,
        }
        
        if grant == 'refresh_token':
            data.update({'refresh_token': self._get_refresh_token()})
        elif grant == 'invoice-scan':
            data.update({'redirect_uri': request.httprequest.url_root + ODOO_REDIRECT_URI})
            data.update({'code': 'next level of issue token'})
        return uri, headers, data
    
    @api.model
    def _get_authorize_uri(self, scope):
        return INVOICE_SCAN_BASE_URL
        uri = INVOICE_SCAN_BASE_URL + INVOICE_SCAN_AUTH_ENDPOINT + '?{parms}'
        data = {
            'scope': scope,
            'redirect_uri': request.httprequest.url_root + ODOO_REDIRECT_URI,
            'client_id': INVOICE_SCAN_CLIENT_ID,
            'response_type': 'code',
        }
        return uri.format(parms=werkzeug.url_encode(data))

    @api.multi
    def _get_status(self, response): 
        response.raise_for_status()
        if int(response.status_code) in (204, 404):
            return False
        return True  
    
    @api.multi
    def _get_request_time(self, response, request_time): 
        try:
            request_time = datetime.strptime(response.headers.get('date'), "%a, %d %b %Y %H:%M:%S %Z")
        except:
            pass
        return request_time
    
    @api.multi
    def _set_access_token(self, token, token_type='Bearer'):
        self.token_type = token_type
        self.access_token = token
        
    @api.multi
    def _get_access_token(self):
        if not self.access_token:
            return False
        return self.token_type + ' ' + self.access_token
            
    @api.multi
    def _set_refresh_token(self, token):
        self.refresh_token = token

    @api.multi
    def _get_refresh_token(self):
        return self.refresh_token
    
    @api.multi
    def _set_organization(self, organization):
        self.organization = organization
        
    @api.multi
    def get_organization(self):
        return self.organization
    
    @api.multi
    def set_client_secret(self, client_secret):
        self.client_secrect = client_secret
    
    @api.multi
    def _get_client_secret(self):
        return self.client_secrect
    
    @api.multi
    def _set_expires_datetime(self, expires_in=0):
        self.expires_in = datetime.now() + timedelta(seconds=expires_in)
    
    @api.multi   
    def _get_expires_datetime(self):
        if not self.expires_in:
            return datetime.now()
        return self.expires_in
        
    def _set_setting(self, parameter, value):
        set_param = self.env['ir.config_parameter'].set_param
        set_param(parameter, value)