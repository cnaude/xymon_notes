Xymon Dynamic Note Editor
================================
 About:
  This note system uses your existing $XYMONHOME/www/notes
  directory. Each note will be replaced by a zero
  length file. If the file is 0 bytes then the
  mod_rewrite rule tells Apache to run the CGI
  instead. If the file is greater than 0 then it loads
  just as usual. The body of each note will be stored
  in a directory of your choice. If you would like to
  see a demo just contact me.

 Files included: 
  xymon_note.cgi (Note printer)
  xymon_note_editor.cgi (Note editor)
  htaccess (Sample .htaccess for $XYMONHOME/www/notes)
  xymon_note_conv.pl (Simple notes conversion tool)

 Requirements: 
  Xymon 4.3.21 or higher
  Perl
  Apache(2) with mod_rewrite enabled

 Optional:
  Perl module - HTML::FromText
	
 Install:
  Read the included INSTALL file.

 Thanks for trying out the Xymon Note Editor.

Installation
================================

 Step 0.
	Make sure you have backups. ;)

 Step 1.
	Edit bbnote.cgi and bbnote_editor.cgi to fit your needs. The CGI scripts are fairly well documented.

 Step 2.
	Copy the CGI scripts to a CGI enabled directory of your choice. I recommend placing the editor script in a password protected directory. 

 Step 3.
	Modify the included htaccess file to suit your needs. 

 Step 4.
	Copy the htaccess to '$XYMONHOME/www/notes/.htaccess'

 Step 5.
	If you have any existing note files then copy them to the bbnotesdata directory and then empty out the originals. (Hint: for i in `ls $XYMONHOME/www/notes`; do; cat /dev/null > $i; done;). You might want to strip off HTML headers and footers. The bbnote.cgi will dynamically create the headers and footers based on the name of the hosts. Included in this tarball is a simple conversion tool. 

 Step 6.
	Visit your Xymon site and click on a note. You should see an edit button. You might want to add a link to the editor somewhere in Xymon headers. Enjoy.

 Troubleshooting tips.
	Make sure that the Apache user has write access to $XYMONHOME/bbnotesdata/ and $XYMONHOME/www/notes/.
	Make sure that Apache is properly configured to allow mod_rewrite rules.	Make sure all of the paths are correct in the CGI scripts.
	If you're not going to use the text2html Perl module then you will need to do some modifications to the bbnote_editor.cgi.
