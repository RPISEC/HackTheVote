//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

// Inventory items.  These objects rely on the item & inventory support
// system defined in item.cs and inventory.cs

//-----------------------------------------------------------------------------
// Health kits can be added to your inventory and used to heal up.
//-----------------------------------------------------------------------------

datablock ItemData(HealthKit)
{
   // Mission editor category, this datablock will show up in the
   // specified category under the "shapes" root category.
   category = "Health";

   // Basic Item properties
   shapeFile = "~/data/shapes/items/healthKit.dts";
   mass = 1;
   friction = 1;
   elasticity = 0.3;

   // Dynamic properties defined by the scripts
   pickupName = "a health kit";
   repairAmount = 50;
};

function HealthKit::onUse(%this,%user)
{
   // Apply some health to whoever uses it, the health kit is only
   // used if the user is currently damaged.
   if (%user.getDamageLevel() != 0) {
      %user.decInventory(%this,1);
      %user.applyRepair(%this.repairAmount);
      if (%user.client)
         messageClient(%user.client, 'MsgHealthKitUsed', '\c2Health Kit Applied');
   }
}


//-----------------------------------------------------------------------------
// Health Patchs cannot be picked up and are not meant to be added to 
// inventory.  Health is applied automatically when an objects collides
// with a patch.
//-----------------------------------------------------------------------------

datablock ItemData(HealthPatch)
{
   // Mission editor category, this datablock will show up in the
   // specified category under the "shapes" root category.
   category = "Health";

   // Basic Item properties
   shapeFile = "~/data/shapes/items/healthPatch.dts";
   mass = 1;
   friction = 1;
   elasticity = 0.3;

   // Dynamic properties defined by the scripts
   repairAmount = 20;
   maxInventory = 0; // No pickup or throw
};

function HealthPatch::onCollision(%this,%obj,%col)
{
   // Apply health to colliding object if it needs it.
   // Works for all shapebase objects.
   if (%col.getDamageLevel() != 0 && %col.getState() !$= "Dead" ) {
      %col.applyRepair(%this.repairAmount);
      %obj.respawn();
      if (%col.client)
         messageClient(%col.client, 'MsgHealthPatchUsed', '\c2Health Patch Applied');
   }
}
