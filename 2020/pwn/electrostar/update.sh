cp -r ./bin /home/app/.
cp -r ./serve.sh /home/app/.

chown root:app -R /home/app
chmod -r /home/app/bin/flag3.exe

systemctl daemon-reload
systemctl enable electrostar
systemctl restart electrostar
