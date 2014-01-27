import xmlrpclib

user = 'admin'
pwd = 'admin'
dbname = 'test_security'
model = 'res.partner'

sock = xmlrpclib.ServerProxy('http://localhost:6118/xmlrpc/common')
uid = sock.login(dbname ,user ,pwd)

sock = xmlrpclib.ServerProxy('http://localhost:6118/xmlrpc/object')

# CREATE A PARTNER
partner_data = {'name':'Dhawal', 'active':True, 'vat':'ZZZZZ'}
partner_id = sock.execute(dbname, uid, pwd, model, 'create', partner_data)
# The relation between res.partner and res.partner.category is of type many2many
# To add  categories to a partner use the following format:
partner_data = {'name':'Provider2', 'category_id': [(6,0,[3, 2, 1])]}
# Where [3, 2, 1] are id fields of lines in res.partner.category
# SEARCH PARTNERS
args = [('vat', '=', 'ZZZZZ'),]
ids = sock.execute(dbname, uid, pwd, model, 'search', args)

# READ PARTNER DATA
fields = ['name', 'active', 'vat', 'ref']
results = sock.execute(dbname, uid, pwd, model, 'read', ids, fields)

# EDIT PARTNER DATA
values = {'vat':'ZZ1ZZ'}
results = sock.execute(dbname, uid, pwd, model, 'write', ids, values)

# DELETE PARTNER DATA
results = sock.execute(dbname, uid, pwd, model, 'unlink', ids)
