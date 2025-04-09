# apc2ovpn
Convert Sophos' XGS firewall site2site .apc files to native openvpn format

Options supported:
- Creates inline entries for cert, key and ca
- Creates a separated file for auth-user-pass
- Adds "dev tun" and "client".
- Encloses the server DN with double quotes.

Please check that it works for you and propose any changes you may need. 


