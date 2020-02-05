odoo.define('ls_add_column', function (require) {
"use strict";
console.log("Calling js")
    var core = require('web.core');
    var ajax = require('web.ajax');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');

    var qweb = core.qweb;

    var addcolfield = 
    {
        renderButtons: function () 
        {     
            var self = this;
            this._super.apply(this, arguments);
            
            var your_btn = this.$buttons.find('button.o_button_ls_add_column')                
            your_btn.on('click', this.proxy('o_button_ls_add_column'))
        },
        
        o_button_ls_add_column: function()
        {
            var self = this;
            var state = self.model.get(self.handle, {raw: true});
        
             _.each(this.actionViews, function (obj) {
                if(obj.type === 'list'){
                    self.list_view_id = obj.fieldsView.view_id;
                    self.list_fields_name = Object.keys(obj.fieldsView.viewFields);
                    }
                });
         
            var context = {'state':state.getContext(),'modelName':state.model,
            'view_id':self.list_view_id,
            'fields_name':self.list_fields_name};
            return self.do_action
            ({
                name: 'Select Column Name',
                type: 'ir.actions.act_window',
                res_model: 'lsaddcolumn.wizard', 
                // #This model must Transient Model
                target: 'new',
                views: [[false, 'form']], 
                view_type : 'form',
                view_mode : 'form',
                context: context,
                flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
            });
        }
    };
    ListController.include(addcolfield);    
});