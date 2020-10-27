//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

// Load up common script base
loadDir("common");

//-----------------------------------------------------------------------------
// Load up defaults console values.

// Defaults console values
exec("./client/defaults.cs");
exec("./server/defaults.cs");

// Preferences (overide defaults)
exec("./client/prefs.cs");
exec("./server/prefs.cs");


//-----------------------------------------------------------------------------
// Package overrides to initialize the mod.
package WebStarterKit {

function displayHelp() {
   Parent::displayHelp();
   error(
      "Web Mod options:\n"@
      "  -listen <port>     Start by listening on <port>\n"
   );
}

function parseArgs()
{
   Parent::parseArgs();

   // Arguments, which override everything else.
   for (%i = 1; %i < $Game::argc ; %i++)
   {
      %arg = $Game::argv[%i];
      %nextArg = $Game::argv[%i+1];
      %hasNextArg = $Game::argc - %i > 1;
   
      switch$ (%arg)
      {
         //--------------------
         case "-listen":
            $argUsed[%i]++;
            if (%hasNextArg) {
               $listenPort = %nextArg;
               $argUsed[%i+1]++;
               %i++;
            }
            else
               error("Error: Missing Command Line argument. Usage: -listen <filename>");
      }
   }
}

function onStart()
{
   Parent::onStart();
   echo("\n--------- Initializing MOD: Web Starter Kit ---------");

   // Load the scripts that start it all...
   exec("./http.cs");

   // Start up in either client, or dedicated server mode
   if ($listenPort $= "") {
      startHTTPServer($HTTP::DefaultPort);
   } else {
      startHTTPServer($listenPort);
   }
}

function onExit()
{
   echo("Exporting client prefs");
   export("$pref::*", "./client/prefs.cs", False);

   echo("Exporting server prefs");
   export("$Pref::Server::*", "./server/prefs.cs", False);

   Parent::onExit();
}

}; // Client package
activatePackage(WebStarterKit);
