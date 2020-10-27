//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//------------------------------------------------------------------------------
// Console onEditorRender functions:
//------------------------------------------------------------------------------
// Functions:
//   - renderSphere([pos], [radius], <sphereLevel>);
//   - renderCircle([pos], [normal], [radius], <segments>);
//   - renderTriangle([pnt], [pnt], [pnt]);
//   - renderLine([start], [end], <thickness>);
//
// Variables:
//   - consoleFrameColor - line prims are rendered with this
//   - consoleFillColor
//   - consoleSphereLevel - level of polyhedron subdivision
//   - consoleCircleSegments
//   - consoleLineWidth
//------------------------------------------------------------------------------

function SpawnSphere::onEditorRender(%this, %editor, %selected, %expanded)
{
   if(%selected $= "true")
   {
      %editor.consoleFrameColor = "255 0 0";
      %editor.consoleFillColor = "0 0 0 0";
      %editor.renderSphere(%this.getWorldBoxCenter(), %this.radius, 1);
   }
}

function AudioEmitter::onEditorRender(%this, %editor, %selected, %expanded)
{
   if(%selected $= "true" && %this.is3D && !%this.useProfileDescription)
   {
      %editor.consoleFillColor = "0 0 0 0";

      %editor.consoleFrameColor = "255 0 0";
      %editor.renderSphere(%this.getTransform(), %this.minDistance, 1);

      %editor.consoleFrameColor = "0 0 255";
      %editor.renderSphere(%this.getTransform(), %this.maxDistance, 1);
   }
}

//function Item::onEditorRender(%this, %editor, %selected, %expanded)
//{
//   if(%this.getDataBlock().getName() $= "MineDeployed")
//   {
//      %editor.consoleFillColor = "0 0 0 0";
//      %editor.consoleFrameColor = "255 0 0";
//      %editor.renderSphere(%this.getWorldBoxCenter(), 6, 1);
//   }
//}