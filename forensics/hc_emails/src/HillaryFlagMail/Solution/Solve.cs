using System;
using System.IO;
using System.Linq;
using Redemption;

namespace Solution {
    class Solve {
        static void Main(string[] args) {
            string path = Path.GetFullPath(@"..\..\..\snapshot.pst");

            // Load the PST
            RDOSession session = new RDOSession();
            session.LogonPstStore(path);

            // Grab everything in the inbox
            RDOItems inbox = session.GetDefaultFolder(rdoDefaultFolders.olFolderInbox).Items;

            // Filter out all emails from the flag mailer
            RDOItems spoofed = inbox.Restrict("[SenderEmailAddress]='cl1nt0nm4il3r@gmail.com'");

            // The flag is hidden in the send date (year),
            // sorted by the delivery date
            string flag = string.Concat(spoofed.OfType<RDOMail>()
                                               .OrderBy(m => m.ReceivedTime) // Sort by delivery date
                                               .Select(m => m.SentOn.Year - 2000) // Get the flag ordinal values
                                               .Select(c => (char) c)); // Convert to char
            Console.Out.WriteLine(flag);
        }
    }
}
