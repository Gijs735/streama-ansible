import chargebee
import json

chargebee.configure("test_fcRPfdRIoanNgFbrPEGzbprua5Bb0g6r","fireflix-test")
entries = chargebee.Subscription.list({
    "limit" : 100,
    "plan_id[in]" : ["standard"],
    "status[in]" : ["active", "in_trial"]
    })
for entry in entries:
  subscription = entry.subscription
  customer = entry.customer
  card = entry.card

print(customer)


#pip3 install 'chargebee>=2,<3'

#https://apidocs.chargebee.com/docs/api/subscriptions#list_subscriptions_status