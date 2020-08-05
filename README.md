## VIMES
Very Important Managing of Encrypting a Service 

## Proof of concept, do NOT use in production 
This is not high code quality but exists as a proof of concept. Not recommended to run in a production enviornment.

### Description
An endpoint DNS proxy that opprotunisitically upgrades DNS to an encrypted protocol without overriding the DNS server issued via DHCP. For Windows.

### Installation
1. Open a terminal as Administrator
1. `python3 -m venv .env`
2. `.\.env\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python vimes.py`