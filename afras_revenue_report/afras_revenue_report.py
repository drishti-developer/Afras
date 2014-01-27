from openerp.osv import osv
from openerp.osv import fields
import datetime

class revenue_report(osv.osv):
    _name = 'revenue.report'
    _columns = {
        'name' : fields.char('Report Name', required=True),
        'comment': fields.char('Reference'),
        'branch': fields.many2one('account.analytic.account','Branch', domain=[('entry_type','=','branch')],  required=True),
        'date' : fields.date('Dated',  required=True),
        'revenue_report_line': fields.one2many('revenue.report.line','revenue_report_id','Data'),
        'company_id':fields.many2one('res.company','Company'),
        'journal_id': fields.property(
            'account.journal',
            type='many2one',
            relation='account.journal',
            string="Journal",
            view_load=True,
            store=True,
            domain="[('type', 'in', ['purchase','general'])]",
            required=True,
            ),
        'state': fields.selection([('draft', 'Draft'),('validate', 'Validate')], 'Status'),
        }

    def default_get(self, cr, uid, fields, context=None):
        res = super(revenue_report, self).default_get(cr, uid, fields, context=context)
 
        user_brw = self.pool.get('res.users').browse(cr, uid, uid)
        if user_brw:
            res.update({'company_id': user_brw.company_id.id})
        account_obj = self.pool.get('account.account')
        
        acc_12002_id = account_obj.search(cr,uid,[('code','=',str(1112002))])
        acc_11001_id = account_obj.search(cr,uid,[('code','=',str(1111001))])
        acc_21001_id = account_obj.search(cr,uid,[('code','=',str(1121001))])
        acc_51001_id = account_obj.search(cr,uid,[('code','=',str(2151001))])
        acc_11000_id = account_obj.search(cr,uid,[('code','=',str(4111000))])
        
        account_ids = [
                       {'name':'Cash Receivable','debit_account':acc_12002_id and acc_12002_id[0] or False,'credit_account':acc_21001_id and acc_21001_id[0] or False,},
                       {'name':'Cash Paid','debit_account':acc_21001_id and acc_21001_id[0] or False,'credit_account':acc_12002_id and acc_12002_id[0] or False},
                       {'name':'Non-Cash Receivable','debit_account':acc_11001_id and acc_11001_id[0] or False,'credit_account':acc_21001_id and acc_21001_id[0] or False},
                       {'name':'Non-Cash Paid','debit_account':acc_21001_id and acc_21001_id[0],'credit_account':acc_11001_id and acc_11001_id[0] or False,},
                       {'name':'Arrears of Closed Contracts','debit_account':acc_21001_id and acc_21001_id[0],'credit_account':acc_11000_id and acc_11000_id[0] or False,},
                       {'name':'Arrears of Open Contracts','debit_account':acc_21001_id and acc_21001_id[0],'credit_account':acc_11000_id and acc_11000_id[0] or False,},
                       {'name':'Customer Deposits','debit_account':acc_12002_id and acc_12002_id[0] or False,'credit_account':acc_51001_id and acc_51001_id[0] or False}
                       ]
        
        res.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'revenue.report'),'state': 'draft','date':str(datetime.date.today()),'revenue_report_line':account_ids})
        return res
    
    def validate(self,cr, uid, ids, context=None):
        created_move_ids = []
        move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        
        self_brw=self.browse(cr,uid,ids[0])
        
        period_id = period_obj.find(cr, uid, self_brw.date, context={'company_id':self_brw.company_id.id})
        journal_id = self_brw.journal_id.id
                  
        for line in self_brw.revenue_report_line:
            move_line1 = {
                'name': '/',
                'ref': self_brw.name,
                'account_id': line.credit_account.id,
                'debit': 0.0,
                'credit': line.amount,
                'period_id': period_id and period_id[0] or False,
                'journal_id': journal_id,
                'date': self_brw.date,
            }
            
            move_line2 = {
                'name': '/',
                'ref': self_brw.name,
                'account_id': line.debit_account.id,
                'credit': 0.0,
                'debit': line.amount,
                'period_id': period_id and period_id[0] or False,
                'journal_id': journal_id,
                'analytic_account_id': self_brw.branch.id,
                'date': self_brw.date,
            }
            
            move_id = move_obj.create(cr, uid, {
                'name': '/',
                'date': self_brw.date,
                'ref': self_brw.name,
                'period_id': period_id and period_id[0] or False,
                'journal_id': journal_id,
                'cost_analytic_id': self_brw.branch.id,
                'line_id':[(0,0,move_line1),(0,0,move_line2)]
                }, context=context)
            
            created_move_ids.append(move_id)
        
        if created_move_ids:
            move_obj.button_validate(cr,uid,created_move_ids)            
            self.write(cr,uid,ids,{'state':'validate'})
            
        return True

revenue_report()
  
class revenue_report_line(osv.osv):
    _name = 'revenue.report.line'
    _columns = {
                'name': fields.char('Description'),
                'amount': fields.float('Amount'),
                'debit_account': fields.many2one('account.account','Debit Account', required=True),
                'credit_account': fields.many2one('account.account','Credit Account', required=True),
                'revenue_report_id': fields.many2one('revenue.report','Related Report', invisible = True,)
                }

revenue_report_line()