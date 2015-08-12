
{
    'name': 'Employee Loan management',
    'version': '1.1',
    'author': 'Libu Koshy ',
    'category': 'hr',
    'sequence': 21,
    'website': 'http://www.myhost.com',
    'summary': 'Employee can apply for loan(emi),and EMI Amount will deducted from Monthly Salary ',
    'description': """
         * It Manages Employee  Loan
         * Manages Employee Reschedule of Loan(EMI Amount)
         * Manages Repayment without affects Payroll
         * Reflect on Payroll
         *Manage Accounts of Payroll
         """,
 
    'images': [
               ],
    'depends': ['base', 'hr','hr_payroll','hr_sonic','hr_contract'],
    'data': [   'employee_loan_view.xml',
                'emp_loan_sequence.xml',
                'security/ir.model.access.csv',
                'hr_payroll_data.xml',
                'payslip_loan_view.xml'
            
            
                 ],
    'demo': [],
    'test': [  
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [  ],
}
