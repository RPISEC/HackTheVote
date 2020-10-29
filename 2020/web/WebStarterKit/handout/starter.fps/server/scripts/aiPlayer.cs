//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// AIPlayer callbacks
// The AIPlayer class implements the following callbacks:
//
//    PlayerData::onStuck(%this,%obj)
//    PlayerData::onUnStuck(%this,%obj)
//    PlayerData::onStop(%this,%obj)
//    PlayerData::onMove(%this,%obj)
//    PlayerData::onReachDestination(%this,%obj)
//    PlayerData::onTargetEnterLOS(%this,%obj)
//    PlayerData::onTargetExitLOS(%this,%obj)
//    PlayerData::onAdd(%this,%obj)
//
// Since the AIPlayer doesn't implement it's own datablock, these callbacks
// all take place in the PlayerData namespace.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Demo Pathed AIPlayer.
//-----------------------------------------------------------------------------

datablock PlayerData(DemoPlayer : PlayerBody)
{
   shootingDelay = 2000;
};

function DemoPlayer::onReachDestination(%this,%obj)
{
   // Moves to the next node on the path.
   // Override for all player. Normally we'd override this for only
   // a specific player datablock or class of players.
   if (%obj.path !$= "") {
      if (%obj.currentNode == %obj.targetNode)
         %this.onEndOfPath(%obj,%obj.path);
      else
         %obj.moveToNextNode();
   }
}

function DemoPlayer::onEndOfPath(%this,%obj,%path)
{
   %obj.nextTask();
}

function DemoPlayer::onEndSequence(%this,%obj,%slot)
{
   echo("Sequence Done!");
   %obj.stopThread(%slot);
   %obj.nextTask();
}


//-----------------------------------------------------------------------------
// AIPlayer static functions
//-----------------------------------------------------------------------------

function AIPlayer::spawn(%name,%spawnPoint)
{
   // Create the demo player object
   %player = new AiPlayer() {
      dataBlock = DemoPlayer;
      path = "";
   };
   MissionCleanup.add(%player);
   %player.setShapeName(%name);
   %player.setTransform(%spawnPoint);
   return %player;
}

function AIPlayer::spawnOnPath(%name,%path)
{
   // Spawn a player and place him on the first node of the path
   if (!isObject(%path))
      return;
   %node = %path.getObject(0);
   %player = AIPlayer::spawn(%name,%node.getTransform());
   return %player;
}


//-----------------------------------------------------------------------------
// AIPlayer methods 
//-----------------------------------------------------------------------------

function AIPlayer::followPath(%this,%path,%node)
{
   // Start the player following a path
   %this.stopThread(0);
   if (!isObject(%path)) {
      %this.path = "";
      return;
   }
   if (%node > %path.getCount() - 1)
      %this.targetNode = %path.getCount() - 1;
   else
      %this.targetNode = %node;
   if (%this.path $= %path)
      %this.moveToNode(%this.currentNode);
   else {
      %this.path = %path;
      %this.moveToNode(0);
   }
}

function AIPlayer::moveToNextNode(%this)
{
   if (%this.targetNode < 0 || %this.currentNode < %this.targetNode) {
      if (%this.currentNode < %this.path.getCount() - 1)
         %this.moveToNode(%this.currentNode + 1);
      else
         %this.moveToNode(0);
   }
   else
      if (%this.currentNode == 0)
         %this.moveToNode(%this.path.getCount() - 1);
      else
         %this.moveToNode(%this.currentNode - 1);
}

function AIPlayer::moveToNode(%this,%index)
{
   // Move to the given path node index
   %this.currentNode = %index;
   %node = %this.path.getObject(%index);
   %this.setMoveDestination(%node.getTransform(), %index == %this.targetNode);
}


//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------

function AIPlayer::pushTask(%this,%method)
{
   if (%this.taskIndex $= "") {
      %this.taskIndex = 0;
      %this.taskCurrent = -1;
   }
   %this.task[%this.taskIndex] = %method; 
   %this.taskIndex++;
   if (%this.taskCurrent == -1)
      %this.executeTask(%this.taskIndex - 1);
}

function AIPlayer::clearTasks(%this)
{
   %this.taskIndex = 0;
   %this.taskCurrent = -1;
}

function AIPlayer::nextTask(%this)
{
   if (%this.taskCurrent != -1)
      if (%this.taskCurrent < %this.taskIndex - 1)
         %this.executeTask(%this.taskCurrent++);
      else
         %this.taskCurrent = -1;
}

function AIPlayer::executeTask(%this,%index)
{
   %this.taskCurrent = %index;
   eval(%this.getId() @ "." @ %this.task[%index] @ ";");
}


//-----------------------------------------------------------------------------

function AIPlayer::singleShot(%this)
{
   // The shooting delay is used to pulse the trigger
   %this.setImageTrigger(0,true);
   %this.setImageTrigger(0,false);
   %this.trigger = %this.schedule(%this.shootingDelay,singleShot);
}


//-----------------------------------------------------------------------------

function AIPlayer::wait(%this,%time)
{
   %this.schedule(%time * 1000,"nextTask");
}

function AIPlayer::done(%this,%time)
{
   %this.schedule(0,"delete");
}

function AIPlayer::fire(%this,%bool)
{
   if (%bool) {
      cancel(%this.trigger);
      %this.singleShot();
   }
   else
      cancel(%this.trigger);
   %this.nextTask();
}

function AIPlayer::aimAt(%this,%object)
{
   echo("Aim: " @ %object);
   %this.setAimObject(%object);
   %this.nextTask();
}

function AIPlayer::animate(%this,%seq)
{
   //%this.stopThread(0);
   //%this.playThread(0,%seq);
   %this.setActionThread(%seq);
}


//-----------------------------------------------------------------------------

function AIManager::think(%this)
{
   // We could hook into the player's onDestroyed state instead of
   // having to "think", but thinking allows us to consider other
   // things...
   if (!isObject(%this.player))
      %this.player = %this.spawn();
   %this.schedule(500,think);
}

function AIManager::spawn(%this)
{
   %player = AIPlayer::spawnOnPath("Kork","MissionGroup/Paths/Path1");
   %player.followPath("MissionGroup/Paths/Path1",-1);

   %player.mountImage(CrossbowImage,0);
   %player.setInventory(CrossbowAmmo,1000);
   return %player;
}






