#!/bin/bash

REAL_FLAG1="flag{sh4zb0t_1s_r0ughly_th3_c0rr3ct_s3nt1m3nt}"
REAL_FLAG2="Couldnt get this one in time for testing :(\nSuffice to say if you're reading this, you've gone too far.\nJust get the flag from main.cs"

# -----------------------------------------------------------------------------

if [ -d ../handout ]; then
	chmod -R 755 ../handout
	rm -rf ../handout
fi

mkdir ../handout
cp -aR common main.cs ReadMe.txt start.sh starter.fps starter.web "Torque Demo Debug OSX.app" torque.png ../handout
cd ../handout

rm common/client/prefs.cs
rm common/prefs.cs
rm common/server/banlist.cs
rm common/server/prefs.cs
rm starter.fps/client/config.cs
rm starter.fps/client/prefs.cs
rm starter.fps/server/prefs.cs
rm starter.web/client/prefs.cs
rm starter.web/server/prefs.cs
rm starter.web/server/banlist.cs

echo '$pref::Net::BindAddress = "127.0.0.1";' > starter.web/client/prefs.cs

find . -name "*.dso" -exec sh -c "echo '{}' && rm '{}'" \;

chmod +x "./Torque Demo Debug OSX.app/Contents/MacOS/Torque Demo Debug OSX"
"./Torque Demo Debug OSX.app/Contents/MacOS/Torque Demo Debug OSX" -mod starter.fps -mod starter.web -compileall

find starter.web -name "*.cs" -exec sh -c "echo '{}' && rm '{}'" \;
find starter.web -name "*.gui" -exec sh -c "echo '{}' && rm '{}'" \;

rm flag2.txt
cat main.cs | sed 's/flag{[^}]*}/flag{fake_flag1}/g' > main2.cs
rm main.cs
mv main2.cs main.cs

find . -name "*.DS_Store" -exec sh -c "echo '{}' && rm '{}'" \;
find . -name "*.ml" -exec sh -c "echo '{}' && rm '{}'" \;

cd ../src

# -----------------------------------------------------------------------------

if [ -d chal ]; then
	chmod -R 755 chal
	rm -rf chal
fi
if [ -f chal.zip ]; then
	rm -rf chal.zip
fi
mkdir chal
cp -aR common main.cs ReadMe.txt start.sh starter.fps starter.web "Torque Demo Debug OSX.app" torque.png chal
cd chal

rm common/client/prefs.cs
rm common/prefs.cs
rm common/server/banlist.cs
rm common/server/prefs.cs
rm starter.fps/client/config.cs
rm starter.fps/client/prefs.cs
rm starter.fps/server/prefs.cs
rm starter.web/client/prefs.cs
rm starter.web/server/prefs.cs
rm starter.web/server/banlist.cs

echo '$pref::Net::BindAddress = "0.0.0.0";' > starter.web/client/prefs.cs

find . -name "*.dso" -exec sh -c "echo '{}' && rm '{}'" \;

chmod +x "./Torque Demo Debug OSX.app/Contents/MacOS/Torque Demo Debug OSX"
"./Torque Demo Debug OSX.app/Contents/MacOS/Torque Demo Debug OSX" -mod starter.fps -mod starter.web -compileall

printf "$REAL_FLAG2" > flag2.txt
cat main.cs | sed "s/flag{[^}]*}/$REAL_FLAG1/g" > main2.cs
rm main.cs
mv main2.cs main.cs

find . -name "*.DS_Store" -exec sh -c "echo '{}' && rm '{}'" \;
find . -name "*.ml" -exec sh -c "echo '{}' && rm '{}'" \;
zip -9r ../chal.zip .

cd ..
