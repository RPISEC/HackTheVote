//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Function to construct and initialize the default canvas window
// used by the games

function initCanvas(%windowName)
{
   videoSetGammaCorrection($pref::OpenGL::gammaCorrection);
   if (!createCanvas(%windowName)) {
      quit();
      return;
   }

   setOpenGLTextureCompressionHint( $pref::OpenGL::compressionHint );
   setOpenGLAnisotropy( $pref::OpenGL::anisotropy );
   setOpenGLMipReduction( $pref::OpenGL::mipReduction );
   setOpenGLInteriorMipReduction( $pref::OpenGL::interiorMipReduction );
   setOpenGLSkyMipReduction( $pref::OpenGL::skyMipReduction );

   // Declare default GUI Profiles.
   exec("~/ui/defaultProfiles.cs");

   // Common GUI's
   exec("~/ui/GuiEditorGui.gui");
   exec("~/ui/ConsoleDlg.gui");
   exec("~/ui/InspectDlg.gui");
   exec("~/ui/LoadFileDlg.gui");
   exec("~/ui/SaveFileDlg.gui");
   exec("~/ui/MessageBoxOkDlg.gui");
   exec("~/ui/MessageBoxYesNoDlg.gui");
   exec("~/ui/MessageBoxOKCancelDlg.gui");
   exec("~/ui/MessagePopupDlg.gui");
   exec("~/ui/HelpDlg.gui");
   exec("~/ui/RecordingsDlg.gui");

   // Commonly used helper scripts
   exec("./metrics.cs");
   exec("./messageBox.cs");
   exec("./screenshot.cs");
   exec("./cursor.cs");
   exec("./help.cs");
   exec("./recordings.cs");

   // Init the audio system
   OpenALInit();
}

function resetCanvas()
{
   if (isObject(Canvas))
   {
      Canvas.repaint(); 
   }
}
