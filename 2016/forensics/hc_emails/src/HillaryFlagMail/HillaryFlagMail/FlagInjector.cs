using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Redemption;

namespace FlagInjector {
    static class FlagInjector {
        static Random rand = new Random();

        // Just having fun at this point
        static string[] aliasStrings = {
            "trump@chi.na",
            "feel@the.bern",
            "Jeb!",
            "zodiac@kill.er",
            "git@g.ud",
            "Literally the NSA",
            "Snow@d.en",
            "Donald Trump",
            "Bernie",
            "Mr. Mile-long Forehead",
            "anon@4chan.org",
            "obama@us.gov",
            "paul@srand.time.NULL",
            "rip@rpi.edu",
            "bill@clinton.io",
            "tellusthe@memes.dwn",
            "herecomed@t.boi",
            "oshitw@dd.up"
        };

        static string[] subjectStrings = {
            "I'M GOING TO BUILD A WALL AND IT'S GOING TO BE YUUUUUGE",
            "About our debate...",
            "I can still win this, I know I can!",
            "I blame trump for everything",
            "CROOKED",
            "We're watching you",
            "Maybe I should leak all this stuff...",
            "WRONG!!",
            "1%",
            "MY FOREHEAD IS GETTING LARGER",
            "TOPKEK",
            "Please stop mentioning me in your debates",
            "17569417231965791794693197561579179562971",
            "Thanks Shirley",
            "Who? What?"
        };

        /// <summary>
        /// Cycles over an enumerable infinitely (like python's itertools.cycle())
        /// </summary>
        /// <typeparam name="T">Element type of enumerable</typeparam>
        /// <param name="iter">Enumerable to cycle over</param>
        /// <returns>An enumerable at the current element in the cycle</returns>
        static IEnumerable<T> Cycle<T>(IEnumerable<T> iter) {
            // Cache everything in an array
            IEnumerable<T> enumerable = iter as T[] ?? iter.ToArray();
            while (true) {
                foreach (T t in enumerable) {
                    yield return t;
                }
            }
        }

        /// <summary>
        /// Extension method for IEnumerator that returns the first element and moves to the next
        /// </summary>
        /// <typeparam name="T">Type of element contained in the enumerator</typeparam>
        /// <param name="list">The enumerator</param>
        /// <returns>First element of the list that was removed</returns>
        public static T Next<T>(this IEnumerator<T> en) {
            if (en == null) throw new InvalidOperationException();
            en.MoveNext();
            return en.Current;
        }

        static DateTime EncodeChar(int c) {
            DateTime date = new DateTime(2000 + c, // year (hide the flag character here)
                                         // Rest are random
                                         rand.Next(1, 13), // month
                                         rand.Next(1, 29), // day
                                         rand.Next(24), // hour
                                         rand.Next(60), // min
                                         rand.Next(60)); // sec

            // Silly sanity check in case of rolling over or some shit
            if (!date.ToString().Contains($"{2000 + c}")) {
                throw new System.Exception("IT FUCKED UP");
            }
            return date;
        }

        static void Main(string[] args) {
            // <3 visual studio
            string origpath = Path.GetFullPath(@"..\..\..\backup.pst"); // Just full of spam
            string targetpath = Path.GetFullPath(@"..\..\..\..\snapshot.pst"); // This will be the challenge

            // Copy over the original pst
            File.Copy(origpath, targetpath, true);

            // Have to use Redemption for this, since outlook is "secure"
            // Open the PST
            RDOSession session = new RDOSession();
            session.LogonPstStore(targetpath);

            // Load the target inbox
            RDOFolder inboxFolder = session.GetFolderFromPath("PRIVATE INBOX");
            RDOItems inbox = inboxFolder.Items;
            inbox.Sort("ReceivedTime", false); // Pre-sort them in ascending order
            Console.WriteLine(inbox.Count);

            // Encode the flag in DateTimes, hiding it in the year (2000 + c)
            // e.g. 3/9/2102 12:45:54 AM ==> 102 => 'f'
            var flag = "flag{w1k1L3ak5_g0T_n0tH1ng_0n_m3}".Select(c => EncodeChar(c)).ToList();

            // fun
            var aliases = Cycle(aliasStrings).GetEnumerator();
            var subjects = Cycle(subjectStrings).GetEnumerator();

            // Approximately space out the emails
            int range = inbox.Count/flag.Count;
            for (int i = 0; i < flag.Count; i++) {
                // Copy the delivery time from a random email in this range
                DateTime recvTime = inbox[rand.Next(i*range, (i + 1)*range)].ReceivedTime;
                DateTime flagtime = flag[i];
                Console.WriteLine($"{flagtime} => {recvTime}");

                // Create a fake email with the two times and other fun stuff
                RDOMail flagmail = inbox.Add("IPM.Note");
                flagmail.Importance = 1;
                flagmail.ReceivedTime = recvTime;
                flagmail.SentOn = flagtime;
                flagmail.Subject = subjects.Next();
                flagmail.To = "n0t.h1ll4ry.cl1nt0n@gmail.com";
                flagmail.Sender = session.GetAddressEntryFromID(session.AddressBook.CreateOneOffEntryID(aliases.Next(), "SMTP",
                                                                                                        "cl1nt0nm4il3r@gmail.com",
                                                                                                        false, false));
                flagmail.Save();
            }

            // Sort the emails by delivery time, scattering the spoofed ones (in order) across the dump
            inbox = inboxFolder.Items;
            Console.WriteLine(inbox.Count);
            inbox.Sort("ReceivedTime", false);

            // Guess we're doing it this way -__-
            Console.WriteLine("Flag is in place, moving to inbox...");
            RDOFolder targetInbox = session.GetDefaultFolder(rdoDefaultFolders.olFolderInbox);
            foreach (RDOMail email in inbox) {
                email.CopyTo(targetInbox);
            }
            targetInbox.Save();
            Console.WriteLine("Done!");
        }
    }
}
