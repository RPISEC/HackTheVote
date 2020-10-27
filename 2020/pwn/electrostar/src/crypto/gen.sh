openssl ecparam -name secp224r1 -genkey -noout -out key.pem
openssl ec -in key.pem -pubout -out public.pem
