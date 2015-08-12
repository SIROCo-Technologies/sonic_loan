import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp.osv import fields,osv
from openerp import api, tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class hr_payslip(osv.osv):
    
    _inherit = 'hr.payslip'
    
    _columns = {
                 'dummy':fields.float('Current Month Loan Amount')
                }
    temp_emp=0
    
    def onchange_employee_id(self, cr, uid, ids, date_from, date_to,employee_id=False, contract_id=False, context=None):


        empl_payline_pool = self.pool.get('hr.employee.loan.line')
        empl_payline_name=empl_payline_pool.browse(cr,uid,ids)
        empolyee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        worked_days_obj = self.pool.get('hr.payslip.worked_days')
        input_obj = self.pool.get('hr.payslip.input')
        v=self.read(cr,uid,ids,['name'],context)
        #if empl_payline_name==v:

        if context is None:
            context = {}
        #delete old worked days lines
        old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_worked_days_ids:
            worked_days_obj.unlink(cr, uid, old_worked_days_ids, context=context)

        #delete old input lines
        old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_input_ids:
            input_obj.unlink(cr, uid, old_input_ids, context=context)


        #defaults
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': [],
                      'worked_days_line_ids': [],
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      'dummy':0.00
                      }
            }
        
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
        var_val=_('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y')))



        res['value'].update({
                    'name': var_val,
                    'company_id': employee_id.company_id.id,
                    
        })

        if not context.get('contract', False):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

        if not contract_ids:
            return res
        contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
        res['value'].update({
                    'contract_id': contract_record and contract_record.id or False
        })
        struct_record = contract_record and contract_record.struct_id or False
        if not struct_record:
            return res
        res['value'].update({
                    'struct_id': struct_record.id,
        })
        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
        input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
        
        contra = contract_record and contract_record.id or False
        cr.execute('''SELECT emi_amount FROM hr_employee_loan_line WHERE  EXTRACT(month FROM emi_date) = %s AND EXTRACT(year FROM emi_date) = %s AND em_contra = %s''',(ttyme.month,ttyme.year,contra,))
        var_id = cr.fetchall()
#         if var_id!=[]:


        res['value'].update({
                    'worked_days_line_ids': worked_days_line_ids,
                    'input_line_ids': input_line_ids,
                    'dummy':var_id[0][0] if var_id!=[] else ''
        })
        return res
    
    def compute_sheet(self, cr, uid, ids, context=None):
        #cr.execute('''SELECT id FROM hr_employee_loan_line WHERE  EXTRACT(month FROM emi_date) = %s AND EXTRACT(year FROM emi_date) = %s AND em_contra = %s''',(ttyme.month,ttyme.year,payslip.contract_id.id))
        #if paid
        #contract_obj = self.pool.get('hr.contract')
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        #sequence_obj_pool_new = self.pool.get('hr.employee.loan.line')
        #emp_obj_pool_loan = self.pool.get('hr.employee.loan')

        rsss=False
        for payslip in self.browse(cr, uid, ids, context=context):
            ttyme = ttyme = datetime.fromtimestamp(time.mktime(time.strptime(payslip.date_from, "%Y-%m-%d")))
            #rsss1 = self.pool.get('hr.employee.loan.line')
            #temp_obj1 = rsss1.browse(cr, uid, var_id[0][0])

            #chnage the query check with contract of employee line,hr.payslip class

            cr.execute('''SELECT id FROM hr_employee_loan_line WHERE  EXTRACT(month FROM emi_date) = %s AND EXTRACT(year FROM emi_date) = %s AND em_contra = %s''',(ttyme.month,ttyme.year,payslip.contract_id.id))
            var_id = cr.fetchall()
            if var_id!=[]:
                #print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',var_id
                rsss1 = self.pool.get('hr.employee.loan.line')
                temp_obj1 = rsss1.browse(cr, uid, var_id[0][0])
                if var_id!=[] and temp_obj1.paid_staus==False:
                    rsss = self.pool.get('hr.employee.loan.line')
                    rsss.write(cr, uid, var_id[0][0], {'paid_staus':True})
                    temp_obj = rsss.browse(cr, uid, var_id[0][0])
                    print("@@@@@@@@@@@@@@",temp_obj)
                    line_ids = rsss.search(cr, uid, [('loan_id','=',temp_obj.loan_id.id)])
                    # sumer = 0
                    # for each in line_ids:
                    #     sumer = sumer+rsss.browse(cr, uid, each).emi_amount
                    sumer = temp_obj.loan_id.remaining_balance-temp_obj.emi_amount
                    print("@@@@@@@@@@@@@@",sumer)

                    self.pool.get('hr.employee.loan').write(cr, uid, temp_obj.loan_id.id, {'remaining_balance':sumer})


            number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
            #delete old payslip lines
            old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
            #old_slipline_ids_val = sequence_obj_pool_new.search(cr, uid, [('paid_staus', '=', 'True')], context=context)
#            old_slipline_ids
            if old_slipline_ids:
                slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
            if payslip.contract_id:
                #set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            # if old_slipline_ids_val:
            #     for obj in self.pool.get('hr.employee.loan').browse(cr,uid,ids, context):
            #         total={}
            #         total[obj.id]=0
            #         for on2 in obj.loan_line:
            #             total[obj.id]+=on2.monthly_principle_paid
            #     total=sequence_obj_pool_new.write(cr,uid,old_slipline_ids_val,{'test_field':total}, context=context)
            #     #sequence_obj_pool_new.unlink(cr, uid, old_slipline_ids_val, context=context)
            else:
                #if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
#             if self.browse(cr, uid, ids).dummy!=False:
#                 ded_id = self.pool.get('hr.salary.rule.category').search(cr, uid, [('name','=','Deduction')])[0]
#                 deduct = {'name':'Loan','code':'DED','category_id':ded_id,'quantity':1.00,'rate':100.00,'amount':self.browse(cr, uid, ids).dummy,'total':self.browse(cr, uid, ids).dummy}
#                 lines.append(deduct)
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)
        return True