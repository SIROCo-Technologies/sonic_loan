import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import fields,osv
from openerp.osv.fields import _column
from openerp.tools.translate import _
import datetime
from dateutil.relativedelta import relativedelta
import math
import calendar
from openerp.tools.safe_eval import safe_eval as eval

class hr_employee(osv.osv):

       _inherit = 'hr.employee'


       def _contracts_count_new(self, cr, uid, ids, field_name, arg, context=None):
            print("Temp val@@@@@@@@@@@@@@@@@@@")
            Loan = self.pool['hr.employee.loan']

            return {
                employee_id: Loan.search_count(cr, uid,[('employee_id', '=',employee_id)],context=context)
                for employee_id in ids
                    }

       # def _contracts_count(self, cr, uid, ids, field_name, arg, context=None):
       #      Contract = self.pool.get('hr.employee.loan')
       #      temp=int(Contract.search_count(cr, SUPERUSER_ID, [('employee_id', '=', ids[0])], context=context))
       #      print("Temp val@@@@@@@@@@@@@@@@@@@",temp)
       #      print("ids @@@@@@@@@@@@@@@@@@@@",ids)
       #      #employee_id=self.browse(cr,uid,ids[0]).employee_id
       #      return temp

       # def _contracts_count_new(self,cr,uid,ids,field_name,context=None):
       #
       #     valu=self.pool.get('hr.employee.loan').search(cr,uid,[('employee_id','=',ids[0])],context=context)
       #     a=0
       #     for i in valu:
       #         a=a+1
       #         print("aaaaaaaaaaaaaa",a)
       #     return a





       _columns={
                'contracts_count_new': fields.function(_contracts_count_new, type='integer', string='Contracts'),

        }


# hr_employee()

class hr_employee_loan(osv.osv):
      _name = 'hr.employee.loan'
      
      def get_employee_id(self, cr, uid, *args):
          
          employee_id =  self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)]) and self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])[0] or False
          
          return employee_id
      

      _columns = {
                  'test_field':fields.float('TEst'),
                  'emp_contra':fields.many2one('hr.contract','Employee Contract',required=True,states={'draft':[('readonly',False)]}),
                  'emp_img':fields.binary('Image'),
                  'remaining_balance':fields.float(string='Remaining Payment'),
                  'emp_salary':fields.float('Salary'),
                  'name' : fields.char('Name',size=256,required=True,),
                  'employee_id':fields.many2one('hr.employee','Employee',required=True,readonly=True ,states={'draft':[('readonly',False)]}),
                  'state': fields.selection([
                        ('draft', 'Draft'),
                        ('confirm','Confirm'),
                        ('approved','Approve'),
                        ('cancel', 'Cancelled'),
                        ('progress', 'In Progress'),
                        ('done', 'Done'),
                        ],'State'), 
                  'request_date' : fields.date('Request Date',required=True,readonly=False),
                  
                  'approval_date' : fields.date('Approval Date',),
                  'loan_date' : fields.date('Loan Receive Date',states={'approved':[('required',True)]}),
                  'request_loan_amount' : fields.integer('Request Loan Amount',required=True,readonly=True ,states={'draft':[('readonly',False)]}),
                  'approve_loan_amount' : fields.integer('Approve Loan Amount',required = True ,states={'draft':[('required',False)],'cancel':[('required',False)]}),
                  'interest' : fields.float('Interest',required = True ,states={'draft':[('required',False)],'cancel':[('required',False)]}),
                  'approx_emi' : fields.float('Approx. EMI',readonly=True),
                  'no_of_month' : fields.integer('No of Months',required=True,states={'draft':[('readonly',False)]}),
                  'emi_amount': fields.float('EMI Amount'),
                  
                 
                  'loan_line': fields.one2many('hr.employee.loan.line', 'loan_id', 'Loan Lines',),
                  'emi_start_month' : fields.date('EMI Start Month',required=True),
                  'last_emi_date': fields.date('EMI Last Date'),
                  'reason': fields.text('Reason For Loan'),
                  

                  }
      
      _defaults = { 
        'state': 'draft',
        'name': '/',
        'request_date': fields.date.context_today,
        'employee_id' : get_employee_id,
        'no_of_month':1
       }
      
     
      
      def create(self, cr, uid, vals, context=None):
         vals['name'] = self.pool.get('ir.sequence').next_by_code(cr, uid, 'hr.employee.loan')

         return super(hr_employee_loan, self).create(cr, uid, vals, context=context)
     
      
      def loan_confirm(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            self.write(cr, uid, o.id, {'state': 'confirm','request_date' : datetime.date.today()}) 
        return True
    

                  
      def onchange_employee(self,cr,uid,ids,employee_id,context=None):
          vals={}
          emploee_obj=self.pool.get('hr.employee').browse(cr,uid,employee_id)
          contract_obj_m = self.pool.get('hr.contract')
          contract_ids=contract_obj_m.search(cr, uid, [('employee_id','=',employee_id)])
          if contract_ids!=[]:
              contract_obj = contract_obj_m.browse(cr, uid, contract_ids[0])
              print "contract_obj##########3",contract_obj.name
              if employee_id:
                vals={'emp_salary':contract_obj.wage,
                      'emp_img':emploee_obj.image_medium,
                     'emp_contra':contract_ids[0],
#                     'test_field':contract_obj.name
                      }
                print "valuewwwwwwwwwwwwwwwwwwwwwwww",vals
          return {'value':vals}
      
      def onchange_no_month(self,cr,uid,ids,field_val1,field_val2,context=None):
          vals={}
          if field_val2==0:
              raise osv.except_osv(('Warning!'), ("Please Enter a Valid Number of Month."))
          res_val=field_val1/field_val2
          return {'value':{'emi_amount':res_val}}

      def onchange_line(self,cr,uid,ids,loan_line,context=None):
          return True

    
      def loan_cancel(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            self.write(cr, uid, o.id, {'state': 'cancel'}) 
        return True
    
      def loan_complete(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            self.write(cr, uid, o.id, {'state': 'done'}) 
        return True
    
      def loan_approve(self, cr, uid, ids, context=None):
          context = context or {}
          for o in self.browse(cr, uid, ids):
                print "@@@@"*100,o.no_of_month,o.approve_loan_amount,
                P = float(o.approve_loan_amount)  # Principle
                R = float(o.interest)/12/100 #Interest Rate
                N = o.no_of_month  # No. of Monthly Installments
                if R:
                   EMI = (P * R) * math.pow((1+R),N) /  (math.pow((1+R),N)-1)
                elif not o.interest and o.emi_amount:
                    EMI = o.emi_amount
                else:
                     EMI = P/N
                self.write(cr, uid, o.id, {'approx_emi': EMI,'state': 'approved','approval_date' : datetime.date.today()})
                print'After Write Method###############################################'     
          return True
      
      
      def loan_release(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            contra=o.emp_contra.id
            print o.no_of_month,o.approve_loan_amount,
            paid_amount = 0
            P = float(o.approve_loan_amount)  # Principle
            R = float(o.interest)/12/100 #Interest Rate
            N = o.no_of_month  # No. of Monthly Installments
            date1 = datetime.datetime.strptime(o.emi_start_month,"%Y-%m-%d")
            date2 = datetime.datetime.strptime(o.loan_date,"%Y-%m-%d") 
            days = calendar.monthrange(date2.year,date2.month)[1] - date2.day +1
            interest1 = P*R*days/calendar.monthrange(date2.year,date2.month)[1]
            emi_date = datetime.datetime(date2.year,date2.month, calendar.monthrange(date2.year,date2.month)[1]) + relativedelta( days = +(1) )
            last_emi_date = datetime.datetime(date2.year,date2.month, calendar.monthrange(date2.year,date2.month)[1]) + relativedelta( days = +(1) )
            if date1 > emi_date and (date1.month != date2.month or date1.year == date2.year ):
                 dic = {
                       'emi_date' : emi_date -relativedelta( days = +(1) ),
                       'bal_loan_amount' : P,
                       'loan_id' : o.id,
                       'interest_amount' :round(interest1,2),
                       'monthly_principle_paid' : -round(interest1,2),
                       'emi_amount' : 0.00,
                       'em_contra':contra
                      # 'month': 
                       
                       }
                 last_emi_date = emi_date -relativedelta( days = +(1) )
                 P += round(interest1,2)
                 self.pool.get('hr.employee.loan.line').create(cr, uid, dic)
                 emi_date += relativedelta( months = +(1) ) 
                    
            while date1 >= emi_date:
                 interest = P* R
                 dic = {
                       'emi_date' : emi_date -relativedelta( days = +(1) ),
                       'bal_loan_amount' : P,
                       'loan_id' : o.id,
                       'interest_amount' :round(interest,2),
                       'monthly_principle_paid' : -round(interest,2),
                       'emi_amount' : 0.00,
                       'em_contra':contra
                      # 'month': 
                       
                       } 
                 last_emi_date = emi_date -relativedelta( days = +(1) )
                 P += round(interest,2)
                 self.pool.get('hr.employee.loan.line').create(cr, uid, dic)  
                 emi_date += relativedelta( months = +1 ) 
                
            if R:
               EMI = (P * R) * math.pow((1+R),N) /  (math.pow((1+R),N)-1)
            elif not o.interest and o.emi_amount:
                   M = P/o.emi_amount
                   N = int(M)
                   EMI = o.emi_amount
                   
                     
            else:
                 EMI = P/N
            print "EMI",EMI
                 
            amount_per_month = EMI
            summer = 0
            for i in range(0,N):
                interest = (P - paid_amount)* R
                dic = {
                       'emi_date' : emi_date + relativedelta( months = +(i) ) -relativedelta( days = +(1) ),
                       'bal_loan_amount' : P - paid_amount,
                       'loan_id' : o.id,
                       'interest_amount' :round(interest,2),
                       'monthly_principle_paid' : round((amount_per_month-interest),2),
                       'emi_amount' : round(amount_per_month,2),
                       'em_contra':contra
                      # 'month': 
                       
                       }
                summer+=dic['emi_amount']
                last_emi_date = emi_date + relativedelta( months = +(i) ) -relativedelta( days = +(1) )
                if i ==0 and   (date1 <= date2 or (date1.month == date2.month and date1.year == date2.year) ):
                    dic['interest_amount'] = round(interest1,2)
                    dic['emi_amount'] = round(amount_per_month,2) - round(interest,2) + round(interest1,2)
                    
                paid_amount += round((amount_per_month-interest),2)
                self.pool.get('hr.employee.loan.line').create(cr, uid, dic)
            
            if not o.interest and o.emi_amount:
                  if M > N:
                       pending_amount = P -o.emi_amount*N
                       dic1 = {
                       'emi_date' : emi_date + relativedelta( months = +(1) ) -relativedelta( days = +(1) ),
                       'bal_loan_amount' : pending_amount,
                       'loan_id' : o.id,
                       'interest_amount' :0.0,
                       'monthly_principle_paid' : pending_amount,
                       'emi_amount' : pending_amount,
                       'em_contra':contra
                      # 'month': 
                       
                       }

                       last_emi_date = emi_date + relativedelta( months = +(1) ) -relativedelta( days = +(1) )
                       #emi_date + relativedelta( months = +(1) ) -relativedelta( days = +(1) ),
                       self.pool.get('hr.employee.loan.line').create(cr, uid, dic1)

            self.write(cr, uid, o.id, {'state': 'progress',
                                       
                                       'last_emi_date': last_emi_date,'remaining_balance':summer})
            
               
        return True
      
class hr_employee_loan_line(osv.osv):
      _name = 'hr.employee.loan.line'
      _rec_name = "emi_date"
      _columns = {
                  'em_contra':fields.many2one('hr.contract','Employee Contract'),
                  'paid_staus':fields.boolean('paid'),
                  'name' : fields.char('Name',size=256),
                  
                  'loan_id' : fields.many2one('hr.employee.loan','Loan'),
                  'state': fields.selection([
                        ('draft', 'Draft'),
                        ('confirm','Confirm'),
                        ('cancel', 'Cancelled'),
                        ('progress', 'In Progress'),
                        ('done', 'Done'),
                        ],'State'), 
                  'bal_loan_amount' : fields.float('Balance Amount'),
                  'interest_amount': fields.float('Interest Amount'),
                  'monthly_principle_paid' : fields.float('Monthly principle Paid'),
                  'emi_amount' : fields.float('EMI Amount'),
                  'payment_date' : fields.date('Payment Date'),
                  'emi_date' : fields.date('EMI Date'),
                  'payslip_id' : fields.many2one('hr.payslip','PaySlip'),
                  'month' : fields.selection([('1', 'January'), ('2', 'February'), 
                                             ('3', 'March'), ('4', 'April'), 
                                            ('5', 'May'), ('6', 'June'),
                                             ('7', 'July'), ('8', 'August'),
                                             ('9', 'September'), ('10', 'October'),
                                             ('11', 'November'), ('12', 'December'),], 'Month'),
                  
                 
                  }

      def unlink(self, cr, uid, ids, context=None):
          val_o = self.browse(cr, uid, ids[0])
          val = val_o.emi_amount
          old = val_o.loan_id.remaining_balance
          if val_o.paid_staus==True:
              raise osv.except_osv(('Warning!'), ("You Cannot Delete a Confirmed Loan Line ! Please Click on Discard "))
             #raise osv.except_osv(('Warning!'), ("You Cannot Delete a Confirm Loan Line Please Click on Discard %s ")% (val_o.paid_staus))
          self.pool.get('hr.employee.loan').write(cr, uid, val_o.loan_id.id, {'remaining_balance':old-val})
          return super(hr_employee_loan_line, self).unlink(cr, uid, ids, context)

class hr_employee_loan_reschedule(osv.osv):
      _name = 'hr.employee.loan.reschedule'
      
      def get_employee_id(self, cr, uid, *args):
          print "arg value"*50,args
          employee_id =  self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)]) and self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])[0] or False
          print "%%"*50,employee_id
          return employee_id
      
      
      _columns = {
                  'emp_contra':fields.many2one('hr.contract','Employee Contract',required=True),
                  'name' : fields.char('Name',size=256,required=True),
                  'employee_id' : fields.many2one('hr.employee','Employee',required=True),
                  
                  'state': fields.selection([
                        ('draft', 'Draft'),
                        ('confirm','Confirm'),
                        ('cancel', 'Cancelled'),
                        ('approve', 'Approve'),
                        ('done', 'Done'),
                        ],'State'), 
                  'amount' : fields.integer('Amount',required=True),
                  'reason': fields.text('Reason For Reschedule'),
                  'loan_line_id' : fields.many2one('hr.employee.loan.line','Reschedule EMI',required=True),
                  'loan_id' : fields.many2one('hr.employee.loan','Loan',required=True),
                  'adjust_emi' : fields.boolean('Adjust in next EMI'),
                  'no_of_emi' : fields.integer('No of EMI'),
                  'month' : fields.selection([('1', 'January'), ('2', 'February'), 
                                             ('3', 'March'), ('4', 'April'), 
                                            ('5', 'May'), ('6', 'June'),
                                             ('7', 'July'), ('8', 'August'),
                                             ('9', 'September'), ('10', 'October'),
                                             ('11', 'November'), ('12', 'December'),], 'Month'),
                 
                  } 
      _defaults = { 
        'state': 'draft',
        'name': '/',
        'employee_id' : get_employee_id,
        'no_of_emi':1
       }
      def onchange_employee(self,cr,uid,ids,employee_id,context=None):
          print "employee_id#################################(1,2,3)",employee_id
          vals={}
          emploee_obj=self.pool.get('hr.employee').browse(cr,uid,employee_id)
          print "valuewwwwwwwwwwwwwwwwwwwwwwww emploee_objemploee_obj",emploee_obj
          contract_obj_m = self.pool.get('hr.employee.loan')
          print "contract_obj_m@@@@@@@@@@@@@@@@@@@@@",contract_obj_m
          contract_ids=contract_obj_m.search(cr, uid, [('employee_id','=',employee_id)])
          print "contract_ids@@@@@@@@@@@@@@@@@@@@@@@@@@@",contract_ids
          if contract_ids!=[]:
              contract_obj = contract_obj_m.browse(cr, uid, contract_ids[0])
              print "contract_obj##########3",contract_obj
              if employee_id:
                vals={
                    'emp_contra':contract_obj.emp_contra,
                    }
                print "valuewwwwwwwwwwwwwwwwwwwwwwww",vals
          return {'value':vals} 
      
      def create(self, cr, uid, vals, context=None):
         vals['name'] = self.pool.get('ir.sequence').next_by_code(cr, uid, 'hr.employee.loan.reschedule')
         return super(hr_employee_loan_reschedule, self).create(cr, uid, vals, context=context)
     
     
      def loan_reschedule_confirm(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            self.write(cr, uid, o.id, {'state': 'confirm'}) 
            print "o.id$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",o.id
        return True
    
    
      def loan_reschedule_approve(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            contra=o.emp_contra.id
            
            paid_amount = o.amount - o.loan_line_id.interest_amount
            remaining_amount =  o.loan_line_id.monthly_principle_paid - paid_amount
            if o.adjust_emi:
                 
               
               
               self.pool.get('hr.employee.loan.line').write(cr, uid,o.loan_line_id.id, {
                                                                             'monthly_principle_paid' : paid_amount,
                                                                              'emi_amount' : o.amount,}) 
               adjust_amount = float(remaining_amount)/o.no_of_emi
               
                
               
               for i in range(o.no_of_emi):
                   remain_month = o.no_of_emi -i
                   interest_amount = remaining_amount*o.loan_id.interest/1200
                   
                   date =  datetime.datetime.strptime(o.loan_line_id.emi_date,"%Y-%m-%d") + relativedelta( months = +(i+1) ),
                   loan_line_ids = self.pool.get('hr.employee.loan.line').search(cr, uid,[('emi_date','=',date),('loan_id','=',o.loan_id.id)])
                   line_obj = self.pool.get('hr.employee.loan.line').browse(cr, uid,loan_line_ids[0])
                   self.pool.get('hr.employee.loan.line').write(cr, uid,loan_line_ids[0], {'bal_loan_amount' :line_obj.bal_loan_amount + remaining_amount,
                                                                             'monthly_principle_paid' : line_obj.monthly_principle_paid + adjust_amount,
                                                                             'emi_amount' :line_obj.emi_amount+ adjust_amount + interest_amount,
                                                                             'interest_amount': line_obj.interest_amount + interest_amount,
                                                                             })
                   remaining_amount -= adjust_amount
                   
                   
            else:
                
                loan_line_ids = self.pool.get('hr.employee.loan.line').search(cr, uid,[('emi_date','>',o.loan_line_id.emi_date),('loan_id','=',o.loan_id.id)])
                self.pool.get('hr.employee.loan.line').write(cr, uid,o.loan_line_id.id, {
                                                                             'monthly_principle_paid' : paid_amount,
                                                                              'emi_amount' : o.amount,})
                
                for i in loan_line_ids:
                    interest_amount = remaining_amount*o.loan_id.interest/1200
                    line_obj = self.pool.get('hr.employee.loan.line').browse(cr, uid,i)
                    self.pool.get('hr.employee.loan.line').write(cr, uid,i, {'bal_loan_amount' :line_obj.bal_loan_amount + remaining_amount,
                                                                             'monthly_principle_paid' : line_obj.monthly_principle_paid - interest_amount,
                                                                             'emi_amount' :line_obj.emi_amount,
                                                                             'interest_amount': line_obj.interest_amount + interest_amount,
                                                                             
                                                                             
                                                                            
                                                                             })
                    remaining_amount += interest_amount
                
                interest_amount = remaining_amount*o.loan_id.interest/1200    
                dic = {
                       'emi_date' : datetime.datetime.strptime(o.loan_id.last_emi_date,"%Y-%m-%d") + relativedelta( months = +1 ),
                       'bal_loan_amount' : remaining_amount,
                       'loan_id' : o.loan_id.id,
                       'interest_amount' :interest_amount,
                       'monthly_principle_paid' : remaining_amount,
                       'emi_amount' : remaining_amount+interest_amount,
                       'em_contra':contra
                       
                       } 
                self.pool.get('hr.employee.loan.line').create(cr,uid,dic)
                self.pool.get('hr.employee.loan').write(cr, uid,o.loan_id.id, {'last_emi_date': dic['emi_date']} )
            
            self.write(cr, uid, o.id, {'state': 'done',
                                       })   
            
        return True

class hr_payslip_line(osv.osv):
    
    _name='hr.payslip.loan'
    
    _columns = { 
                 'loan_id_new':fields.many2one('hr.payslip','Pay'),
                'ref_loan_new2': fields.char('Loan Ref'),
                 'payment_date_new3':fields.date('Payment Date'),
                 'paid_amount_new4':fields.float('Paid Amount'),
                 'paid_or_new5':fields.boolean('paid'),
                }
hr_payslip_line()
