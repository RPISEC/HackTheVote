More Suspicious Traffic
---

* Examine the UDP packets in the pcap. The server sends packets and the receiver ACKs them. 
* They are sent in groups of 3 or 6. 
* 3 corresponds to . (dot) and 6 corresponds to - (dash). This gives Morse Code. 
* Dots/Dashes making up the same letter are sent 0.5 seconds apart with a 1.5 second gap when moving on to the next letter. (looking at the time they are received)
* A little hint is the port which traffic is sent to, according to wikipedia port 23284 is used by something called TimeTracker hinting that they should look at the time.
