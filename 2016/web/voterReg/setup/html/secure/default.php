<?php
    $s = 1;
if (isset($_GET['s'])) {
    $s = @intval($_GET['s']);
}
if ($s < 0 || $s>3) {
    $s = 1;
}
$error = 0;
if ($s == 2) {
    if (!isset($_GET['rbCitizen']) || !isset($_GET['rbAge']) || !isset($_GET['rbResident']) || !isset($_GET['rbFelony'])) {
        $error = 1;
    } else {
        if ($_GET['rbCitizen']!='Y' || $_GET['rbAge']!='Y' || $_GET['rbResident']!='Y' || $_GET['rbFelony']!='rbFelony1') {
            $error = 2;
        } else {
            $error = 0;
        }
    }
}

if ($s == 3) {
    if (!isset($_GET['txtfirst_name']) || !isset($_GET['txtmiddle_name']) || !isset($_GET['txtname_suffix']) || !isset($_GET['txtLast_name']) || !isset($_GET['txtdob']) || !isset($_GET['txtdl_nmbr']) || !isset($_GET['txtRetypeDL'])) {
        $error = 3;
    } else if ($_GET['txtfirst_name']=='' || $_GET['txtmiddle_name']=='' || $_GET['txtLast_name']=='' || $_GET['txtdob']=='' || $_GET['txtdl_nmbr']=='' || $_GET['txtRetypeDL']=='') {
        $error = 4;
    } else if ($_GET['txtdl_nmbr'] != $_GET['txtRetypeDL']) {
        $error = 5;
    } else {
        include('../sql_util.php');
        $stmt = $sql_conn->prepare("INSERT INTO users (firstName,middleName,lastName,suffix,dob,licenceNumber) VALUES (?,?,?,?,?,?);");
        if ($stmt === false) {
            die($sql_conn->error);
        }
        $stmt->bind_param("ssssss",$_GET['txtfirst_name'],$_GET['txtmiddle_name'],$_GET['txtLast_name'],$_GET['txtname_suffix'],$_GET['txtdob'],$_GET['txtdl_nmbr']);
        $stmt->execute();
        if ($stmt->errno) {
            die($stmt->error);
        }
        $stmt->close();

        $stmt = $sql_conn->prepare("SELECT firstName,lastName,dob FROM users WHERE licenceNumber=?;");
        if ($stmt === false) {
            die($sql_conn->error);
        }
        $stmt->bind_param("s",$_GET['txtdl_nmbr']);
        $stmt->bind_result($fName, $lName, $dob);
        $stmt->execute();
        $stmt->fetch();
        if ($stmt->errno) {
            die($stmt->error);
        }
        $stmt->close();
        $sql_conn->close();
        $error = 0;

        
    }
}
        


if ($s == 1 || $error == 1 || $error == 2) {
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/2000/REC-xhtml1-20000126/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">

<head><title>
	Online Voter Registration - Step 1
</title><link href="../styles/voter.css" rel="stylesheet" type="text/css" /><link href="../styles/Taxcenters.css" rel="stylesheet" type="text/css" /></head>
<body>
  <div id="header">
  </div>
  <div id="body">
    <form name="marginForm" method="get" action="default.php?s=2" id="marginForm">
    <input type="hidden" value="2" name="s"></input>
<div>
</div>

<div>

</div>
    <div>
      <div id="pnlError">
	
        <div id="ValidationSummary1" style="color:Red;">
<?php if ($error == 1) {
    echo "Why won't you answer the questions? What are you trying to hide?";
} else if ($error == 2) {
    echo "Uh.... How about not voting?";
} ?>
	</div>
        
        <br />
        <br />
        
      
        
      
</div>
    </div>
    <div id="pnlVerify" style="height:381px;width:776px;">
	
            <h4>STEP 1 OF 2) VERIFY YOUR VOTING ELIGIBILITY</h4>
  

         <table>         
        <tr>
          <td class="style4">
        
            <span id="lblCitizen">1. Are you a citizen of the United States of America?</span>
          </td>
          <td class="style3">
            
            <table id="rbCitizen" border="0">
		<tr>
			<td><input id="rbCitizen_0" type="radio" name="rbCitizen" value="Y" /><label for="rbCitizen_0">Yes</label></td><td><input id="rbCitizen_1" type="radio" name="rbCitizen" value="N" /><label for="rbCitizen_1">No</label></td>
		</tr>
	</table>
          </td>
        </tr>
       
        <tr>
          <td class="style4">
          
            <span id="lblAge" style="display:inline-block;width:358px;">2. Will you be 18 years of age on or before election day?</span>
          </td>
          <td class="style3">
          
            <table id="rbAge" border="0">
		<tr>
			<td><input id="rbAge_0" type="radio" name="rbAge" value="Y" /><label for="rbAge_0">Yes</label></td><td><input id="rbAge_1" type="radio" name="rbAge" value="N" /><label for="rbAge_1">No</label></td>
		</tr>
	</table>
          </td>
        </tr>
        <tr>
          <td class="style4">
          
            <span id="lblResident">3. Are you a resident of Kansas?</span>
          </td>
          <td class="style3">
         
            <table id="rbResident" border="0">
		<tr>
			<td><input id="rbResident_0" type="radio" name="rbResident" value="Y" /><label for="rbResident_0">Yes</label></td><td><input id="rbResident_1" type="radio" name="rbResident" value="N" /><label for="rbResident_1">No</label></td>
		</tr>
	</table>
          </td>
        </tr>
        <tr>
          <td class="style4">
           
            <span id="lblFelony" style="display:inline-block;width:416px;">4. Felony Conviction - Please Choose One:</span>
          </td>
        </tr>
        <tr>
          <td class="style4">
         
            <span id="lblFelony1">I have never been convicted of a felony.</span>
          </td>
          <td class="style3">
         
            <span RepeatDirection="Horizontal" style="display:inline-block;width:335px;"><input id="rbFelony1" type="radio" name="rbFelony" value="rbFelony1" /></span>
          </td>
        </tr>
        <tr>
          <td class="style4">
         
            <span id="lblFelony2">I have been convicted of a felony. All the terms of my sentence have been completed and my rights have been restored.</span>
          </td>
          <td class="style3">
           
            <span RepeatDirection="Horizontal" style="display:inline-block;width:335px;"><input id="rbFelony2" type="radio" name="rbFelony" value="rbFelony2" /></span>
          </td>
        </tr>
        <tr>
          <td class="style4">
         
            <span id="lblFelony3">I am currently under sentence for a felony.</span>
          </td>
          <td class="style3">
           
            <span RepeatDirection="Horizontal" style="display:inline-block;width:335px;"><input id="rbFelony3" type="radio" name="rbFelony" value="rbFelony3" /></span>
          </td>
        </tr>
      </table>
          <br />
     
      <input type="submit" name="btnContinue" value="Continue" id="btnContinue" class="buttonCon" />
    
      
     
      <button type="button" class="button" onclick="location='../'">Back</button>
      <br />
      <br />
    
</div>
    
    
    
</form>
  </div>
  <div align="center">
        Note this is a parody site and is in no way related to the Kansas Department of Revenue and Secretary of State or any related parties. All likeness any real site is parody or not intentional.
  </div>
</body>
</html>
<?php } else if ($s == 2 || $error == 3 || $error ==4 || $error == 5) {  ?>



<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/2000/REC-xhtml1-20000126/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">

<head><title>
    Online Voter Registration - Step 2
</title><link href="../styles/voter.css" rel="stylesheet" type="text/css" /><link href="../styles/Taxcenter.css" rel="stylesheet" type="text/css" /></head>
<body>
  <div id="header">
  </div>
  <div id="body">
    <form name="marginForm" method="get" action="default.php" id="marginForm">
    <input type="hidden" value="3" name="s"></input>
<div>
</div>

<div>

</div>
    <div>
      <div id="pnlError">
    
        <div id="ValidationSummary1" style="color:Red;">
<?php if ($error == 3 || $error == 4) {
    echo "What do you think that * means???";
} else if ($error == 5) {
    echo "Are you sure you have a driver's license? You didn't enter it right";
} ?>

    </div>
        
        <br />
        <br />
        <span id="lblmessage" class="error" style="color:Red;"></span>
      
        
      
</div>
    </div>
    
    <div id="pnlDL" style="height:667px;">
    
    
     <h4>STEP 2 OF 2) VERIFY VALID DRIVER'S LICENSE OR NONDRIVER'S IDENTIFICATION CARD</h4>
        
      Please enter the following information to verify that you have a valid Kansas driver's license or nondriver's identification card.
      <br />
      <br />
        <fieldset>
            <legend>
      <span id="lblNameInfo" style="font-weight:bold;">Name (as it appears on driver's license/nondriver's identification card)</span>
      <span class="required">*</span>
       <br />
                <br />
      <label for="txtfirst_name">
        <span class="required">*</span>First Name:
        <input name="txtfirst_name" type="text" maxlength="15" id="txtfirst_name" class="dbdata" style="width:190px;" />
      </label>
      <span id="reqfirst_name" style="color:Red;visibility:hidden;">*</span>
      <span id="regfirst_name" style="color:Red;visibility:hidden;">*</span>
      <br />
      <label for="txtmiddle_name">
        Middle Name:</label>
      <input name="txtmiddle_name" type="text" maxlength="15" id="txtmiddle_name" class="dbdata" style="width:190px;" />
      <span id="regMiddleName" style="color:Red;visibility:hidden;">*</span>
      <br />
      <label for="txtLast_name">
        <span class="required">*</span>Last Name:
        <input name="txtLast_name" type="text" maxlength="20" id="txtLast_name" class="dbdata" style="width:190px;" />
      </label>
      <span id="reqLast_name" style="color:Red;visibility:hidden;">*</span>
      <span id="regLast_name" style="color:Red;visibility:hidden;">*</span>
      <br />
      <label for="txtname_suffix">Name Suffix:</label>
      <input name="txtname_suffix" type="text" maxlength="3" id="txtname_suffix" class="dbdata" style="width:190px;" />
      <span id="regSuffix" style="color:Red;visibility:hidden;">*</span>
                </legend>
     </fieldset>
      
        <fieldset>
            <legend>
      <span id="lblDOBInfo" style="font-weight:bold;">Date of Birth (must match driver's license/nondriver's card information)</span>
      <br />
      <br />
      <label for="txtdob">
        <span class="required">*</span>Date of Birth:</label>
      <input name="txtdob" type="text" maxlength="10" id="txtdob" class="dbdata" />
      <span id="reqdob" style="color:Red;visibility:hidden;">*</span>
      <span id="regDOB" style="color:Red;visibility:hidden;">*</span>
      <span>MM/DD/YYYY</span>
                </legend>
            </fieldset>
      
     
        <fieldset>
            <legend>
      <span id="lblDLInfo" style="font-weight:bold;">Kansas driver's license or nondriver's identification card number</span>
      <br />
      <br />
      <label for="txtdl_nmbr">
        <span class="required">*</span>License Number or Identification Card Number:
      </label>
      <input name="txtdl_nmbr" type="text" maxlength="9" id="txtdl_nmbr" class="dbdata" />
      <span id="reqdl_nmbr" style="color:Red;visibility:hidden;">*</span>
      <span id="regdl_nmbr" style="color:Red;visibility:hidden;">*</span>
       <span>Example: K01234567 Do Not Enter Dashes</span>
        <br />
      <br />
      <label for="txtRetypeDL">
        <span class="required">*</span>Reenter License or Identification Card Number:</label>
      <input name="txtRetypeDL" type="text" maxlength="9" id="txtRetypeDL" class="dbdata" />
      <span id="reqdl_nmbr0" style="color:Red;visibility:hidden;">*</span>
      <span id="regdl_nmbr2" style="color:Red;visibility:hidden;">*</span>
     <span id="cvDL" style="color:Red;visibility:hidden;">*</span>
        <span>Example: K01234567 Do Not Enter Dashes</span>
    
                </legend>
     </fieldset>
      <input type="submit" name="btnContinue2" value="Continue" id="btnContinue2" class="buttonCon" />
     
      <button type="button" class="button" onclick="location='default.php?s=1'">Back</button>
      <br />
      <br />
    
</div>

</form>
  </div>
  <div align="center">
        Note this is a parody site and is in no way related to the Kansas Department of Revenue and Secretary of State or any related parties. All likeness any real site is parody or not intentional.
  </div>
</body>
</html>
<?php } else if ($s == 3) { ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/2000/REC-xhtml1-20000126/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">

<head><title>
	Online Voter Registration - Success
</title><link href="../styles/voter.css" rel="stylesheet" type="text/css" /><link href="../styles/Taxcenters.css" rel="stylesheet" type="text/css" /></head>
<body>
  <div id="header">
  </div>
  <div id="body">
    <form name="marginForm" method="get" action="default.php?s=2" id="marginForm">
    <input type="hidden" value="2" name="s"></input>
<div>
</div>

<div>

</div>
    <div>
    </div>
    <div id="pnlVerify" style="height:381px;width:776px;">
	
            <h4>SUCCESSFULLY REGISTERED</h4>
        <br />
        <br />
        <p>        
Confirm that the following data is correct so we know it was stored correctly in our database.
        </p>
        <p><b>Name: </b><?php echo htmlentities($lName.", ".$fName); ?><br />
        <b>DoB: </b><?php echo htmlentities($dob); ?></p>
  

      <button type="button" class="button" onclick="location='../'">Back</button>
      <!-- <a href="debug.php">#</a> -->
      <br />
      <br />
    
</div>
    
    
    
</form>
  </div>
  <div align="center">
        Note this is a parody site and is in no way related to the Kansas Department of Revenue and Secretary of State or any related parties. All likeness any real site is parody or not intentional.
  </div>
</body>
</html>
<?php } ?>


