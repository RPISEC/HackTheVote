<nav class="navbar navbar-default">
    <div class="container-fluid">
        <div class="navbar-header">
        <a class="navbar-brand" href="https://<?php echo getenv("MAIN_DOMAIN");?>/"><?php strtoupper(getenv("SITE_NAME")); ?></a>
        </div>
    <div class="nav navbar-nav">
        <li<?php if ($page=="/") {echo ' class="active"';}?>>
        <a href="https://<?php echo getenv("MAIN_DOMAIN");?>/">
            <span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>
            About</a></li>
        </ul>
        <li<?php if ($page=="/manage") {echo ' class="active"';}?>>
        <a href="https://<?php echo getenv("MAIN_DOMAIN");?>/manage">
            <span class="glyphicon glyphicon-cog" aria-hidden="true"></span>
            Manage DNS</a></li>
        </ul>
        <li<?php if ($page=="/login") {echo ' class="active"';}?>>
        <a href="https://<?php echo getenv("MAIN_DOMAIN");?>/login">
            <span class="glyphicon glyphicon-user" aria-hidden="true"></span>
            Login/Logout</a></li>
        </ul>
    </div>
    </div>
</nav>
