<nav class="navbar navbar-inverse">
    <div class="container-fluid">
        <div class="navbar-header">
            <a class="navbar-brand" href="https://voteforme.<?=getenv("DOMAIN");?>/">Vote For Me!</a>
        </div>
    <div class="nav navbar-nav">
        <li<?php if ($page=="/") {echo ' class="active"';}?>>
            <a href="https://voteforme.<?=getenv("DOMAIN");?>/">
            Why You Should <b>Vote For Me!</b></a></li>
        </ul>
        <li<?php if ($page=="/comment") {echo ' class="active"';}?>>
            <a href="https://voteforme.<?=getenv("DOMAIN");?>/comment">
            Contact Me</a></li>
        </ul>
    </div>
    </div>
</nav>
