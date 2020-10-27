// This is defined in the root main.cs
%flag = $flag;

// Hidden for security reasons
%flag = getSubStr(%flag, 0, 6) @ "&lt;hidden&gt;" @ getSubStr(%flag, strlen(%flag) - 2, strlen(%flag));

// Replaced by fancy template system
// echo(%flag);

echo(parseTemplate("~/tmpl/base.html",
	buildTemplateArg("content",
		parseTemplate("~/tmpl/flag.html",
			buildTemplateArg("flag", %flag)
	), buildTemplateArg("nav",
		parseTemplate("~/tmpl/nav.html")
	)
)));
