# Ethereum node
From home assistant use your own node to request wallet info or send your own transactions
This means you can use a and check the status on your phone, without cloud providers

For etherscan there is built in home assistant integration to use.
https://www.home-assistant.io/integrations/etherscan/

## Goal
Get functions with an address parameter in order to
- get balance (input account / contract)
- get transactions (input account / contract)
- get details transaction (input transaction)
- post transaction (input transaction dict)

in Ethereum Handler class that is opened up as api connections