import chargebee
import json
import mysql.connector

# chargebee.configure("test_fcRPfdRIoanNgFbrPEGzbprua5Bb0g6r","fireflix-test")
# entries = chargebee.Subscription.list({
#     "limit" : 100,
#     "plan_id[in]" : ["standard"],
#     "status[in]" : ["active", "in_trial", "non_renewing"]
#     })
# for entry in entries:
#   subscription = entry.subscription
#   customer = entry.customer
#   card = entry.card
#   print(customer.email)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  database="streama"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT username, account_locked FROM user")

myresult = mycursor.fetchall()

mycursor.close()

for x in myresult:
  print(x)


#pip3 install 'chargebee>=2,<3'

#https://apidocs.chargebee.com/docs/api/subscriptions#list_subscriptions_status
#pip3 install mysql-connector-python
#https://www.w3schools.com/python/python_mysql_select.asp