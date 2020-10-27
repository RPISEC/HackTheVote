//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

$defaultGame = "starter.fps";
$displayHelp = false;
$flag = "flag{fake_flag1}";

//-----------------------------------------------------------------------------
// Support functions used to manage the mod string

function pushFront(%list, %token, %delim)
{
   if (%list !$= "")
      return %token @ %delim @ %list;
   return %token;
}

function pushBack(%list, %token, %delim)
{
   if (%list !$= "")
      return %list @ %delim @ %token;
   return %token;
}

function popFront(%list, %delim)
{
   return nextToken(%list, unused, %delim);
}


//------------------------------------------------------------------------------
// Process command line arguments

$modcount = 1;
$userMods = $defaultGame;

for ($i = 1; $i < $Game::argc ; $i++)
{
   $arg = $Game::argv[$i];
   $nextArg = $Game::argv[$i+1];
   $hasNextArg = $Game::argc - $i > 1;
   $logModeSpecified = false;
   
   switch$ ($arg)
   {
      //--------------------
      case "-log":
         $argUsed[$i]++;
         if ($hasNextArg)
         {
            // Turn on console logging
            if ($nextArg != 0)
            {
               // Dump existing console to logfile first.
               $nextArg += 4;
            }
            setLogMode($nextArg);
            $logModeSpecified = true;
            $argUsed[$i+1]++;
            $i++;
         }
         else
            error("Error: Missing Command Line argument. Usage: -log <Mode: 0,1,2>");

      //--------------------
      case "-mod":
         $argUsed[$i]++;
         if ($hasNextArg)
         {
            // Append the mod to the end of the current list
            $userMods = strreplace($userMods, $nextArg, "");
            $userMods = pushFront($userMods, $nextArg, ";");
            $argUsed[$i+1]++;
            $i++;
	    $modcount++;
         }
         else
            error("Error: Missing Command Line argument. Usage: -mod <mod_name>");
            
      //--------------------
      case "-game":
         $argUsed[$i]++;
         if ($hasNextArg)
         {
            // Remove all mods, start over with game
            $userMods = $nextArg;
            $argUsed[$i+1]++;
            $i++;
	    $modcount = 1;
         }
         else
            error("Error: Missing Command Line argument. Usage: -game <game_name>");
            
      //--------------------
      case "-show":
         // A useful shortcut for -mod show
         $userMods = strreplace($userMods, "show", "");
         $userMods = pushFront($userMods, "show", ";");
         $argUsed[$i]++;
	 $modcount++;

      //--------------------
      case "-console":
         enableWinConsole(true);
         $argUsed[$i]++;

      //--------------------
      case "-jSave":
         $argUsed[$i]++;
         if ($hasNextArg)
         {
            echo("Saving event log to journal: " @ $nextArg);
            saveJournal($nextArg);
            $argUsed[$i+1]++;
            $i++;
         }
         else
            error("Error: Missing Command Line argument. Usage: -jSave <journal_name>");

      //--------------------
      case "-jPlay":
         $argUsed[$i]++;
         if ($hasNextArg)
         {
            playJournal($nextArg,false);
            $argUsed[$i+1]++;
            $i++;
         }
         else
            error("Error: Missing Command Line argument. Usage: -jPlay <journal_name>");

      //--------------------
      case "-jDebug":
         $argUsed[$i]++;
         if ($hasNextArg)
         {
            playJournal($nextArg,true);
            $argUsed[$i+1]++;
            $i++;
         }
         else
            error("Error: Missing Command Line argument. Usage: -jDebug <journal_name>");

      //--------------------
      case "-compileall":
         $compileScripts = true;
         $argUsed[$i]++;
         echo("Compile all!");

      //-------------------
      case "-help":
         $displayHelp = true;
         $argUsed[$i]++;

      //-------------------
      default:
         $argUsed[$i]++;
         if($userMods $= "")
            $userMods = $arg;
   }
}

if($modcount == 0) {
      $userMods = $defaultGame;
      $modcount = 1;
}

//-----------------------------------------------------------------------------
// The displayHelp, onStart, onExit and parseArgs function are overriden
// by mod packages to get hooked into initialization and cleanup. 

function onStart()
{
   // Default startup function
}

function onExit()
{
   // OnExit is called directly from C++ code, whereas onStart is
   // invoked at the end of this file.
}

function parseArgs()
{
   // Here for mod override, the arguments have already
   // been parsed.
}   

package Help {
   function onExit() {
      // Override onExit when displaying help
   }
};

function displayHelp() {
   activatePackage(Help);

      // Notes on logmode: console logging is written to console.log.
      // -log 0 disables console logging.
      // -log 1 appends to existing logfile; it also closes the file
      // (flushing the write buffer) after every write.
      // -log 2 overwrites any existing logfile; it also only closes
      // the logfile when the application shuts down.  (default)

   error(
      "Torque Demo command line options:\n"@
      "  -log <logmode>         Logging behavior; see main.cs comments for details\n"@
      "  -game <game_name>      Reset list of mods to only contain <game_name>\n"@
      "  <game_name>            Works like the -game argument\n"@
      "  -mod <mod_name>        Add <mod_name> to list of mods\n"@
      "  -console               Open a separate console\n"@
      "  -show <shape>          Launch the TS show tool\n"@
      "  -jSave  <file_name>    Record a journal\n"@
      "  -jPlay  <file_name>    Play back a journal\n"@
      "  -jDebug <file_name>    Play back a journal and issue an int3 at the end\n"@
      "  -help                  Display this help message\n"
   );
}


//--------------------------------------------------------------------------

// Default to a new logfile each session.
if (!$logModeSpecified) {
   setLogMode(6);
}

// Set the mod path which dictates which directories will be visible
// to the scripts and the resource engine.
setModPaths($userMods);

// Get the first mod on the list, which will be the last to be applied... this
// does not modify the list.
nextToken($userMods, currentMod, ";");

// Execute startup scripts for each mod, starting at base and working up
function loadDir(%dir)
{
   setModPaths(pushback($userMods, %dir, ";"));
   exec(%dir @ "/main.cs");
}

echo("--------- Loading MODS ---------");
function loadMods(%modPath)
{
   %modPath = nextToken(%modPath, token, ";");
   if (%modPath !$= "")
      loadMods(%modPath);

   if(exec(%token @ "/main.cs") != true){
      error("Error: Unable to find specified mod: " @ %token );
      $modcount--;
   }
}
loadMods($userMods);
echo("");

if($modcount == 0) {
   enableWinConsole(true);
   error("Error: Unable to load any specified mods");
   quit();	
}
// Parse the command line arguments
echo("--------- Parsing Arguments ---------");
parseArgs();

// Either display the help message or startup the app.
if($compileScripts)
{
   enableWinConsole(true);
   activatePackage(Help);
   for($file = findFirstFile("*.gui"); $file !$= ""; $file = findNextFile("*.gui"))
   {
      echo($file);
      compile($file);
   }
   for($file = findFirstFile("*.cs"); $file !$= ""; $file = findNextFile("*.cs"))
   {
      echo($file);
      compile($file);
   }
   quit();
} else if ($displayHelp) {
   enableWinConsole(true);
   displayHelp();
   quit();
}
else {
   onStart();
   echo("Engine initialized...");
}

// Display an error message for unused arguments
for ($i = 1; $i < $Game::argc; $i++)  {
   if (!$argUsed[$i])
      error("Error: Unknown command line argument: " @ $Game::argv[$i]);
}
