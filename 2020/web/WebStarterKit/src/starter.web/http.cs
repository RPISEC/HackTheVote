//-----------------------------------------------------------------------------
// TCPObject HTTP Server
// Extremely terrible idea implemented extremely well (poorly) by yours truly,
// glenns
//
// "you have the worst ideas" -My friends
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Constants
//-----------------------------------------------------------------------------

$HTTP::DefaultFile = "index.cs";

$HTTP::ResponseCode[100] = "Continue";
$HTTP::ResponseCode[101] = "Switching Protocols";
$HTTP::ResponseCode[200] = "OK";
$HTTP::ResponseCode[201] = "Created";
$HTTP::ResponseCode[202] = "Accepted";
$HTTP::ResponseCode[203] = "Non-Authoritative Information";
$HTTP::ResponseCode[204] = "No Content";
$HTTP::ResponseCode[205] = "Reset Content";
$HTTP::ResponseCode[206] = "Partial Content";
$HTTP::ResponseCode[300] = "Multiple Choices";
$HTTP::ResponseCode[301] = "Moved Permanently";
$HTTP::ResponseCode[302] = "Found";
$HTTP::ResponseCode[303] = "See Other";
$HTTP::ResponseCode[304] = "Not Modified";
$HTTP::ResponseCode[305] = "Use Proxy";
$HTTP::ResponseCode[307] = "Temporary Redirect";
$HTTP::ResponseCode[400] = "Bad Request";
$HTTP::ResponseCode[401] = "Unauthorized";
$HTTP::ResponseCode[402] = "Payment Required";
$HTTP::ResponseCode[403] = "Forbidden";
$HTTP::ResponseCode[404] = "Not Found";
$HTTP::ResponseCode[405] = "Method Not Allowed";
$HTTP::ResponseCode[406] = "Not Acceptable";
$HTTP::ResponseCode[407] = "Proxy Authentication Required";
$HTTP::ResponseCode[408] = "Request Timeout";
$HTTP::ResponseCode[409] = "Conflict";
$HTTP::ResponseCode[410] = "Gone";
$HTTP::ResponseCode[411] = "Length Required";
$HTTP::ResponseCode[412] = "Precondition Failed";
$HTTP::ResponseCode[413] = "Request Entity Too Large";
$HTTP::ResponseCode[414] = "Request-URI Too Long";
$HTTP::ResponseCode[415] = "Unsupported Media Type";
$HTTP::ResponseCode[416] = "Requested Range Not Satisfiable";
$HTTP::ResponseCode[417] = "Expectation Failed";
$HTCPCP::ResponseCode[418] = "I'm a teapot"; // RFC 2324
$HTTP::ResponseCode[500] = "Internal Server Error";
$HTTP::ResponseCode[501] = "Not Implemented";
$HTTP::ResponseCode[502] = "Bad Gateway";
$HTTP::ResponseCode[503] = "Service Unavailable";
$HTTP::ResponseCode[504] = "Gateway Timeout";
$HTTP::ResponseCode[505] = "HTTP Version Not Supported";

$HTTP::MimeTypeDefault = "text/plain";
$HTTP::MimeType[".cs"] = "text/html";
$HTTP::MimeType[".dso"] = "application/cs";
$HTTP::MimeType[".ppm"] = "image/ppm";
$HTTP::MimeType[".html"] = "text/html";
$HTTP::MimeType[".js"] = "text/javascript";
$HTTP::MimeType[".css"] = "text/css";

//-----------------------------------------------------------------------------
// Server
//-----------------------------------------------------------------------------

function startHTTPServer(%port) {
   new TCPObject(HTTPServer);
   echo("Starting HTTP Server on " @ $pref::Net::BindAddress @ ":" @ %port);
   HTTPServer.port = %port;
   HTTPServer.listen(%port);
   // Torque is stupid so the first time you make a ConsoleLogger nothing works
   new ConsoleLogger(HTTPLogger, "http.log");
}

function HTTPServer::onConnectRequest(%this, %address, %fd) {
   // Gotta admit I forgot constructors could have arguments...
   // Quick scan of the engine source shows that literally only TCPObjects and
   // ConsoleLoggers use constructor arguments.
   %name = "HTTPServerClient for fd #" @ %fd;
   %connection = new TCPObject("", %fd);
   %connection.setName(%name);
   %connection.httpClient = true;
   %connection.server = %this;
   %connection.address = %address;
   %connection.init();
}

function autoreload() {
   %newCRC = getFileCRC($Con::File);
   if ($lastCRC !$= %newCRC) {
      $lastCRC = %newCRC;
      exec($Con::File);
      setModPaths(getModPaths());
   }
   cancel($autoloop);
   $autoloop = schedule(1000, 0, autoreload);
}
autoreload();

//-----------------------------------------------------------------------------
// Connection Management
//-----------------------------------------------------------------------------

function TCPObject::init(%this) {
   %this.state = "REQUEST";
   %this.responseCode = 500;
   %this.headers = 0;
   %this.requestLine = "";

   for (%i = 0; %i < %this.receivedHeaders; %i ++) {
      %this.receivedHeader[%this.receivedHeader[%i, "name"]] = "";
      %this.receivedHeader[%i, "name"] = "";
      %this.receivedHeader[%i, "value"] = "";
   }

   %this.receivedHeaders = 0;
   %this.chunked = false;
   %this.buffer = "";
   %this.body = "";
   %this.requestBody = "";
   %this.maxChunkSize = 0x1000;

   %this.addHeader("Connection", "Keep-Alive");
   %this.addHeader("Server", "TGE/1.2 WebStarterKit/0.1 " @ $platform);
}

function TCPObject::onDisconnect(%this) {
   // This SIGSEGVs if they still have more data pending, because it will keep
   // calling onLine on the deleted object
   //if (%this.getName() $= "HTTPServerClient")
   //   %this.delete();
}

function TCPObject::onLine(%this, %line) {
   // Apparently this build of TGE is so old you can't link namespaces?
   if (!%this.httpClient)
      return;

   switch$ (%this.state) {
      case "REQUEST":
         %this.requestLine = %line;
         %this.state = "HEADER";
      case "HEADER":
         if (%line !$= "") {
            %this.receivedHeader[%this.receivedHeaders] = %line;
            %this.receivedHeaders ++;
         } else {
            %this.processHeaders();
         }
         break;
      case "POST":
         if (%this.requestBody $= "") {
            %this.requestBody = %line;
         } else {
            %this.requestBody = %this.requestBody @ "\r\n" @ %line;
         }
         if (strlen(%this.requestBody) >=
            %this.receivedHeader["Content-Length"]) {
            %this.route();
         }
         break;
      case "ROUTE" or "BODY":
         // Nothing
   }
}

//-----------------------------------------------------------------------------
// Request Processing
//-----------------------------------------------------------------------------

function TCPObject::route(%this) {
   if (%this.state !$= "HEADER" && %this.state !$= "POST") {
      return;
   }

   %question = strpos(%this.uri, "?");
   if (%question != -1) {
      %file = getSubStr(%this.uri, 0, %question);
      %query = getSubStr(%this.uri, %question + 1, strlen(%this.uri));
   } else {
      %file = %this.uri;
      %query = "";
   }

   // Only allow HTTP methods that we have implemented
   if (%this.isMethod(%this.method)) {
      %logger = new ConsoleLogger(HTTPLogger, "http.log");
      %logger.level = warning;

      %this.state = "ROUTE";
      %this.responseCode = %this.call(%this.method, 3, %file, %query,
         %this.requestBody);
      echo(%this.method @ " " @ %this.uri SPC %this.responseCode
         SPC %this.address);

      // Collect errors
      for (%line = %logger.getNextLine(); %line !$= "";
         %line = %logger.getNextLine()) {
         %error = %error NL %line;
      }
      if (%error !$= "") {
         %this.body = %this.body NL "Script Errors: " @ %error;
      }
   } else {
      %this.responseCode = 405;
      %this.body = "";
   }

   %logger.delete();

   %this.finish();
}

function TCPObject::GET(%this, %uri, %query, %body) {
   %path = expandFilename("~/public" @ %uri);
   if (!isFile(%path) && !isFile(%path @ ".dso")) {
      %path = %path @ $HTTP::DefaultFile;
      if (!isFile(%path)) {
         return 404;
      }
   }

   if (!%this.parseQuery(%query)) {
      return 400;
   }

   %this.addHeader("ETag", getFileCRC(%path));
   %this.responseCode = 200;
   if (fileExt(%path) $= ".cs") {
      return %this.runScript(%path);
   } else if (fileExt(%path) $= ".dso") {
      %this.body = "Cannot load compiled script (dso) file.";
      return 500;
   } else {
      return %this.startDownload(%path);
   }

   return %this.responseCode;
}

// Unimplemented HTTP methods

function TCPObject::PUT(%this, %uri, %query, %body) {
   return 501;
}

function TCPObject::PATCH(%this, %uri, %query, %body) {
   return 501;
}

function TCPObject::POST(%this, %uri, %query, %body) {
   return 501;
}

function TCPObject::OPTIONS(%this, %uri, %query, %body) {
   return 501;
}

function TCPObject::HEAD(%this, %uri, %query, %body) {
   return 501;
}

// This one is actually a real HTTP method
// But delete() is a method on our superclass, SimObject
// So technically sending a DELETE request actually deletes the *request*
// This will probably cause the server to crash so prevent that
function TCPObject::DELETE(%this, %uri, %query, %body) {
   if (%uri !$= "") {
      error("DELETE request conflicts with superclass method delete()!");
      // Debugging
      %this.dump();
   } else {
      Parent::delete(%this);
   }
}


//-----------------------------------------------------------------------------

function TCPObject::runScript(%this, %path) {
   %this.addHeader("Content-Type", "text/html");
   for (%i = 0; %i < %this.receivedHeaders; %i ++) {
      %name = %this.receivedHeader[%i, "name"];
      %value = %this.receivedHeader[%i, "value"];
      $_HEADER[%name] = %value;
   }

   for (%i = 0; %i < %this.params; %i ++) {
      %name = %this.param[%i, "name"];
      %value = %this.param[%i, "value"];
      $_GET[%name] = %value;
   }

   $socket = %this;
   $ScriptError = "";
   // Capture all output of the script. Script writer can use echo("text") to
   // output text.
   ob_start(%this);
   %ret = exec(%path);
   %this.body = ob_end_flush(%this);
   $socket = "";

   deleteVariables("$_HEADER*");
   deleteVariables("$_GET*");

   if ($ScriptError !$= "") {
      if (%this.body $= "") {
         %this.body = $ScriptError;
      } else {
         %this.body = %this.body NL $ScriptError;
      }
      return 500;
   }

   return %this.responseCode;
}

function TCPObject::startDownload(%this, %path) {
   // Probably
   if ($HTTP::MimeType[fileExt(%path)] !$= "") {
      %this.addHeader("Content-Type", $HTTP::MimeType[fileExt(%path)]);
   } else {
      %this.addHeader("Content-Type", $HTTP::MimeTypeDefault);
   }
   %this.setChunked();

   %this.chunkedFile = new FileObject();
   if (!%this.chunkedFile.openForRead(%path)) {
      %this.chunkedFile.close();
      %this.chunkedFile.delete();
      return 500;
   }

   %this.body = "";

   return 200;
}

//-----------------------------------------------------------------------------
// Data Transfer
//-----------------------------------------------------------------------------

function TCPObject::sendHeaders(%this) {
   if ($HTTP::ResponseCode[%this.responseCode] $= "") {
      %this.responseCode = 405;
   }

   if (!%this.chunked) {
      %this.addHeader("Content-Length", strlen(%this.body));
   }

   %message = "HTTP/1.1" SPC %this.responseCode SPC
      $HTTP::ResponseCode[%this.responseCode];
   for (%i = 0; %i < %this.headers; %i ++) {
      %message = %message @ "\r\n" @ %this.header[%i, "name"] @ ":" SPC
         %this.header[%i, "value"];
   }
   %message = %message @ "\r\n";
   %message = %message @ "\r\n";
   %r = %this.send(%message);
   if (%r < 0) {
      // TODO: Handle
      error("Send error: " @ %r);
   }
   %this.state = "BODY";
}

function TCPObject::sendBody(%this) {
   %r = %this.send(%this.body);
   if (%r < 0) {
      // TODO: Handle
      error("Send error: " @ %r);
   }
   %r = %this.send("\r\n\r\n");
   if (%r < 0) {
      // TODO: Handle
      error("Send error: " @ %r);
   }
}

function TCPObject::finish(%this) {
   if (%this.chunked) {
      %this.sendBodyChunks();
   } else {
      %this.sendHeaders();
      %this.sendBody();
      %this.init();
   }
}

//-----------------------------------------------------------------------------
// Chunked Encoding support
//-----------------------------------------------------------------------------

function TCPObject::setChunked(%this) {
   %this.chunked = true;
   %this.addHeader("Transfer-Encoding", "chunked");
   %this.sendHeaders();
}

function TCPObject::sendBodyChunks(%this) {
   if (!%this.sendNextChunk()) {
      return;
   }
   // Rate limiting because otherwise one person will max the cpu
   %this.schedule(100, sendBodyChunks);
}

function TCPObject::sendNextChunk(%this) {
   if (isObject(%this.chunkedFile)) {
      while (!%this.chunkedFile.isEOF()
         && strlen(%this.body) < %this.maxChunkSize) {
         %this.body = %this.body @ %this.chunkedFile.readLine() @ "\r\n";
      }
   }

   if (%this.buffer $= "") {
      if (strlen(%this.body) >= %this.maxChunkSize) {
         %chunk = getSubStr(%this.body, 0, %this.maxChunkSize);
         %chunkSize = %this.maxChunkSize;
      } else {
         %chunk = %this.body;
         %chunkSize = strlen(%this.body);
      }

      %header = dec2hex(strlen(%chunk)) @ "\r\n";
      %footer = "\r\n";
      %totalLength = strlen(%header) + strlen(%footer) + %chunkSize;
      %buffer = %header @ %chunk @ %footer;
   } else {
      %buffer = %this.buffer;
      %totalLength = strlen(%buffer);
   }

   // This is cheating (normally Torque doesn't give you return code from send)
   // But without it the server keeps SIGPIPEing and I've already made enough
   // engine changes that I can justify one more *technically* non-breaking
   // change.
   // Plus it makes this next section *way* more fun!
   %result = %this.send(%buffer);

   if (%result < 0) {
      if (%result == -3) { // WouldBlock
         %this.decreaseRate();
         return true;
      } else if (%result == 4) { // NotASocket
         // Usually disconnect
         return false;
      }
      // Unknown Error
      return false;
   } else if (%result != %totalLength) {
      // Incomplete send
      if (%totalLength < %result) {
         // Not really sure wtf happened here
         error("Sent more bytes than we should have? Total: " @ %totalLength @
            " Result: " @ %result);
         backtrace();
         return false;
      }
      if (%this.buffer $= "") {
         %this.body = getSubStr(%this.body, %this.maxChunkSize,
            strlen(%this.body));
      }
      %this.buffer = getSubStr(%buffer, %result, %totalLength - %result);
      %this.decreaseRate();
      return true;
   } else if (%this.buffer !$= "") {
      %this.buffer = "";
      // Finished buffered data, but no new data
      return true;
   }

   %this.body = getSubStr(%this.body, %this.maxChunkSize, strlen(%this.body));
   %this.increaseRate();

   // EOF
   if (%chunkSize == 0) {
      %this.finishChunks();
      return false;
   }
   return true;
}

function TCPObject::finishChunks(%this) {
   if (isObject(%this.chunkedFile)) {
      %this.chunkedFile.close();
      %this.chunkedFile.delete();
   }

   %this.init();
}

function TCPObject::sendChunk(%this, %chunk) {
   return %this.send(dec2hex(strlen(%chunk)) @ "\r\n" @ %chunk @ "\r\n");
}

// This is *basically* slow start, right?
function TCPObject::decreaseRate(%this) {
   %this.maxChunkSize /= 2;
   if (%this.maxChunkSize < 1024) {
      %this.maxChunkSize = 1024;
   }
}
function TCPObject::increaseRate(%this) {
   %this.maxChunkSize += 0x1000;
   if (%this.maxChunkSize > 0x80000) {
      %this.maxChunkSize = 0x80000;
   }
}

//-----------------------------------------------------------------------------
// Utilities
//-----------------------------------------------------------------------------

function TCPObject::addHeader(%this, %name, %value) {
   %this.header[%this.headers, "name"] = %name;
   %this.header[%this.headers, "value"] = %value;
   %this.headers ++;
}

function TCPObject::processHeaders(%this) {
   %method  = getWord(%this.requestLine, 0);
   %uri     = getWord(%this.requestLine, 1);
   %version = getWord(%this.requestLine, 2);

   if (getSubStr(%version, 0, 7) !$= "HTTP/1.") {
      %this.responseCode = 505;
      %this.finish();
      return;
   }

   if (stripChars(%method, "ABCDEFGHIJKLMNOPQRSTUVWXYZ") !$= "") {
      %this.responseCode = 405;
      %this.finish();
      return;
   }

   %this.method = %method;
   %this.uri = %uri;

   for (%i = 0; %i < %this.receivedHeaders; %i ++) {
      %header = %this.receivedHeader[%i];
      %colon = strpos(%header, ":");
      if (%colon == -1) {
         %this.responseCode = 400;
         %this.finish();
         return;
      }
      %name = trim(getSubStr(%header, 0, %colon));
      %value = trim(getSubStr(%header, %colon + 1, strlen(%header)));
      %this.receivedHeader[%i, "name"] = %name;
      %this.receivedHeader[%i, "value"] = %value;
      %this.receivedHeader[%name] = %value;
   }

   if (%this.receivedHeader["Content-Length"] == 0) {
      %this.route();
   } else {
      %this.state = "POST";
   }
}

function TCPObject::parseQuery(%this, %query) {
   %this.params = 0;
   %amp = strpos(%query, "&");
   while (%amp != -1) {
      %param = getSubStr(%query, 0, %amp);
      %equals = strpos(%param, "=");
      if (%equals == -1) {
         return false;
      }
      %name = getSubStr(%param, 0, %equals);
      %value = getSubStr(%param, %equals + 1, strlen(%param));

      %this.param[%this.params, "name"] = URLDecode(%name);
      %this.param[%this.params, "value"] = URLDecode(%value);
      %this.params ++;

      %query = getSubStr(%query, %amp + 1, strlen(%query));
      %amp = strpos(%query, "&");
   }
   %param = %query;
   if (%param $= "") {
      return true;
   }
   %equals = strpos(%param, "=");
   if (%equals == -1) {
      return false;
   }
   %name = getSubStr(%param, 0, %equals);
   %value = getSubStr(%param, %equals + 1, strlen(%param));

   %this.param[%this.params, "name"] = URLDecode(%name);
   %this.param[%this.params, "value"] = URLDecode(%value);
   %this.params ++;

   return true;
}

//-----------------------------------------------------------------------------
// Extremely PHP-inspired output buffering
//-----------------------------------------------------------------------------

function ob_start(%tcp) {
   $ob_tcp = %tcp;
   $ob_buffer = "";
   activatePackage(OutputBuffer);
}

function ob_end_flush(%tcp) {
   deactivatePackage(OutputBuffer);
   $ob_tcp = "";
   return $ob_buffer;
}

package OutputBuffer {
   function header(%name, %value) {
      $ob_tcp.addHeader(%name, %value);
   }
   function code(%code) {
      $ob_tcp.responseCode = %code;
   }
   function echo(%text) {
      if ($ob_tcp.chunked) {
         $ob_tcp.sendChunk(%text @ "\r\n");
      } else {
         if ($ob_buffer $= "") {
            $ob_buffer = %text;
         } else {
            $ob_buffer = $ob_buffer NL %text;
         }
      }
   }
};

function ConsoleLogger::onLog(%this, %line) {
   if (%this.lines $= "") {
      %this.lines = 0;
   }
   %this.line[%this.lines] = %line;
   %this.lines ++;
}

//-----------------------------------------------------------------------------
// Really Good Templating Library
//-----------------------------------------------------------------------------

function parseTemplate(%path, %args) {
   %file = new FileObject();
   if (!%file.openForRead(expandFilename(%path))) {
      return "Error reading " @ %Path;
   }
   %template = "";
   while (!%file.isEOF()) {
      %template = %template @ %file.readLine() @ "\r\n";
   }
   %file.close();
   %file.delete();

   for (%i = 0; %i < getRecordCount(%args); %i ++) {
      %record = getRecord(%args, %i);
      %name = getField(%record, 0);
      %value = unescapeTemplate(getField(%record, 1));

      if (%name $= "")
         continue;

      %template = strReplace(%template, "{{" @ %name @ "}}", %value);
   }

   return %template;
}

function escapeTemplate(%name, %value) {
   // Hack lovingly stolen from spy47
   %name = strReplace(%name, "\t", "-TAB-");
   %name = strReplace(%name, "\n", "-NL-");
   %value = strReplace(%value, "\t", "-TAB-");
   %value = strReplace(%value, "\n", "-NL-");
   return %name TAB %value;
}

function unescapeTemplate(%value) {
   %value = strReplace(%value, "-TAB-", "\t");
   %value = strReplace(%value, "-NL-", "\n");
   return %value;
}

function buildTemplateArg(%name, %value, %rest) {
   return escapeTemplate(%name, %value) NL %rest;
}

function htmlEntities(%value) {
   // Just try to XSS me now!
   %value = strReplace(%value, "&", "&amp;");
   %value = strReplace(%value, "<", "&lt;");
   %value = strReplace(%value, ">", "&gt;");
   %value = strReplace(%value, "\"", "&quot;");
   return %value;
}

//-----------------------------------------------------------------------------
// Utility Functions
//-----------------------------------------------------------------------------

function longstringify(%value) {
   %result = "";
   //4096 is upper bound for buffer overflow so let's be safe
   %blockSize = 1000;
   for (%j = 0; %j < strlen(%value); %j += %blockSize) {
      if (%j > 0) {
         %result = %result @ "@";
      }
      //Fuck you too, torque lexer
      %result = %result @ "\"" @ expandEscape(
         getSubStr(%value, %j, %blockSize)) @ "\"";
   }
   if (%result $= "") {
      return "\"\"";
   }
   return %result;
}

function validateIdentifier(%ident) {
   %goodChars = "abcdefghijklmnopqrstuvwxyz" @
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_:";
   for (%i = 0; %i < strlen(%ident); %i ++) {
      if (strpos(%goodChars, getSubStr(%ident, %i, 1)) == -1) {
         return false;
      }
   }
   return true;
}

function SimObject::call(%this, %func, %nargs, %a0, %a1, %a2, %a3) {
   if (!validateIdentifier(%func)) {
      error("SimObject::call() :: Invalid function name " @ %func);
      return "";
   }
   switch (%nargs) {
   case 0: return eval("return " @ %this @ "." @ %func @ "();");
   case 1: return eval("return " @ %this @ "." @ %func @ "(" @
      longstringify(%a0) @ ");");
   case 2: return eval("return " @ %this @ "." @ %func @ "(" @
      longstringify(%a0) @ "," @ longstringify(%a1) @ ");");
   case 3: return eval("return " @ %this @ "." @ %func @ "(" @
      longstringify(%a0) @ "," @ longstringify(%a1) @ "," @
      longstringify(%a2) @ ");");
   case 4: return eval("return " @ %this @ "." @ %func @ "(" @
      longstringify(%a0) @ "," @ longstringify(%a1) @ "," @
      longstringify(%a2) @ "," @ longstringify(%a3) @ ");");
   default:
      echo("SimObject::call() :: Unimplemented for " @ %nargs @ " args");
      return "";
   }
}

function dec2hex(%val) {
   %digits = "0123456789ABCDEF";
   %result = "";
   while (%val != 0) {
      %digit = getSubStr(%digits, %val & 0xF, 1);
      %result = %digit @ %result;
      %val >>= 4;
   }
   if (%result $= "")
      return "0";
   return %result;
}

function hex2dec(%val) {
   %digits = "0123456789ABCDEF";
   %result = 0;
   while (%val !$= "") {
      %result <<= 4;
      %digit = getSubStr(%val, 0, 1);
      %result |= strPos(%digits, %digit);
      %val = getSubStr(%val, 1, strlen(%val));
   }
   return %result;
}

//http://www.garagegames.com/community/blogs/view/10202
function chrValue(%chr) {
   // So we don't have to do any C++ changes we approximate the function
   // to return ASCII Values for a character.  This ignores the first 31
   // characters and the last 128.

   // Setup our Character Table.  Starting with ASCII character 32 (SPACE)
   %charTable = " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTU" @
      "VWXYZ[\\]^\'_abcdefghijklmnopqrstuvwxyz{|}~\t\n\r";

   //Find the position in the string for the Character we are looking for the
   // value of
   %value = strpos(%charTable, %chr);

   // Add 32 to the value to get the true ASCII value
   %value = %value + 32;

   //HACK:  Encode TAB, New Line and Carriage Return

   if (%value >= 127) {
      if (%value == 127)
         %value = 9;
      if (%value == 128)
         %value = 10;
      if (%value == 129)
         %value = 13;
   }

   //return the value of the character
   return %value;
}

function chrForValue(%chr) {
   // So we don't have to do any C++ changes we approximate the function
   // to return ASCII Values for a character.  This ignores the first 31
   // characters and the last 128.

   // Setup our Character Table.  Starting with ASCII character 32 (SPACE)
   %charTable = " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTU" @
      "VWXYZ[\\]^\'_abcdefghijklmnopqrstuvwxyz{|}~\t\n\r";

   //HACK:  Decode TAB, New Line and Carriage Return

   if (%chr == 9)
      %chr = 127;
   if (%chr == 10)
      %chr = 128;
   if (%chr == 13)
      %chr = 129;

   %chr -= 32;
   if (%chr >= 0) {
      %value = getSubStr(%charTable, %chr, 1);
   } else {
      %value = "";
   }

   return %value;
}

function URLEncode(%rawString) {
   // Encode strings to be HTTP safe for URL use

   // Table of characters that are valid in an HTTP URL
   %validChars = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstu" @
      "vwxyz:/.?_-$(){}~";

   // If the string we are encoding has text... start encoding
   if (strlen(%rawString) > 0) {
      // Loop through each character in the string
      for (%i = 0; %i < strlen(%rawString); %i ++) {
         // Grab the character at our current index location
         %chrTemp = getSubStr(%rawString, %i, 1);

         //  If the character is not valid for an HTTP URL... Encode it
         if (strstr(%validChars, %chrTemp) == -1) {
            //Get the HEX value for the character
            %chrTemp = dec2hex(chrValue(%chrTemp));

            // Is it a space?  Change it to a "+" symbol
            if (%chrTemp $= "20") {
               %chrTemp = "+";
            } else {
               // It's not a space, prepend the HEX value with a %
               %chrTemp = "%" @ %chrTemp;
            }
         }
         // Build our encoded string
         %encodeString = %encodeString @ %chrTemp;
      }
   }
   // Return the encoded string value
   return %encodeString;
}
function URLDecode(%rawString) {
   // Encode strings from HTTP safe for URL use

   // If the string we are encoding has text... start encoding
   if (strlen(%rawString) > 0) {
      // Loop through each character in the string
      for (%i = 0; %i < strlen(%rawString); %i ++) {
         // Grab the character at our current index location
         %chrTemp = getSubStr(%rawString, %i, 1);

         if (%chrTemp $= "+") {
            // Was it a "+" symbol?  Change it to a space
            %chrTemp = " ";
         }
         //  If the character was not valid for an HTTP URL... Decode it
         if (%chrTemp $= "%") {
            //Get the dec value for the character
            %chrTemp = chrForValue(hex2dec(getSubStr(%rawString, %i + 1, 2)));
            %i += 2;
         }
         // Build our encoded string
         %encodeString = %encodeString @ %chrTemp;
      }
   }
   // Return the encoded string value
   return %encodeString;
}
