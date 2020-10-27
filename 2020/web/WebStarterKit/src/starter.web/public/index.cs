%dir = filePath($Con::File);
%listing = "";
for (%f = findFirstFile("./*"); %f !$= ""; %f = findNextFile("./*")) {
	if (fileExt(%f) $= ".DS_Store") {
		continue;
	}
	if (fileBase(%f) $= "flag") {
		continue;
	}
	%subfile = getSubStr(%f, strlen(%dir) + 1, strlen(%f));
	%listing = %listing @ "<li><a href=\"" @ expandEscape(%subfile) @ "\">" @ %subfile @ "</a></li>";
}

if ($_GET["code"] !$= "") {
	code($_GET["code"]);
}

//if ($_GET["calc"] !$= "") {
//	// Not that easy
//	%result = eval($_GET["calc"]);
//}

echo(parseTemplate("~/tmpl/base.html",
	buildTemplateArg("content",
		parseTemplate("~/tmpl/index.html",
			buildTemplateArg("listing", %listing,
			buildTemplateArg("server_address", $pref::Net::BindAddress,
			buildTemplateArg("server_port", $pref::Server::Port,
			buildTemplateArg("server_online", ClientGroup.getCount(),
			buildTemplateArg("server_total", $pref::Server::MaxPlayers,
			buildTemplateArg("sim_time", $Sim::Time,
			buildTemplateArg("current_mission", MissionInfo.name,
			buildTemplateArg("mission_sequence", $MissionSequence,
			buildTemplateArg("code", $socket.responseCode
		))))))))) //No regrets
	), buildTemplateArg("nav", 
		parseTemplate("~/tmpl/nav.html")
	)
)));
