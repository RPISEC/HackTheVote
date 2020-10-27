all:
	gcc leakguard.c -o leakguard.so -shared -fPIC -ldl -Wall -Wl,-z,relro,-z,now
	strip leakguard.so
	gcc candles.c -o candles -Wall -Wl,-z,relro,-z,now
	strip candles
