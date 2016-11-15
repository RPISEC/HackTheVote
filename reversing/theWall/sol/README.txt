This challenge required that you write cheats for a minecraft clone to bypass a large wall

There are tons of ways to solve this, but here was the main idea.

- There was a function that would on the client side return if a player has certain privileges.
- Most of these were checked by the server as well, with the exception of fly and noclip (and speed walk to an extent)
    o Also note, I didn't modify the server to ignore these, Minetest servers just do ¯\_(ツ)_/¯
- You can patch this function to return true, and the client can now toggle these abilities.

However the binary had extra anti-cheat built in
- There are extra packets added to the system
- It would read the first entry of /proc/self/maps (the .text section) and hashing it with a nonce which the server would verify
- This was only done once at connection
- There are a lot of ways to bypass this.
    o You can dump the hash data, and make a wrapper that will intercept the hash and modify it.
    o You could dynamically patch after connection
    o You could have it hash from a backup of the binary
    o Ect

- You can now fly and noclip though the wall.
- Walk to around (1300, 0, 0) to find the flag.

