#!/usr/bin/perl

#############################################
# Name   : xymon_no_purple.cgi
# Author : Chris Naude
# Purpose: Manage purple alerts 
# NOTE: Add this to your sudoers file
#       www-data ALL=NOPASSWD: /opt/xymon/server/bin/xymon
#############################################

use strict;
use CGI ":standard";
use CGI::Carp qw( fatalsToBrowser carpout );

##############################
# Variables
##############################

# Character set
my $charset = "UTF-8";
#my $charset = "iso-8859-1";

# Your $XYMONHOME
my $xymon_home = "/opt/xymon/server";
my $xymon_logs  = "/opt/xymon/data/hist";
# The web path to gifs.
my $xymon_gifs = "/xymon/gifs";
# The main web path for xymon display. 
my $xymon_web  = "/xymon"; 
my $logo = "Xymon";

my $xymon_header = "$xymon_home/web/info_header"; # Change this if needed.
my $xymon_footer = "$xymon_home/web/info_footer"; # Change this if needed.
my $xymon_cgi = '/xymon-cgi';
my $xymon_seccgi = '/xymon-seccgi';
#Standard hosts.cfg file
my $xymon_hosts = "$xymon_home/etc/hosts.cfg";

# No changes needed below.
my $date = localtime(time);

my $menu = "";
our %xymon_env = {};

open (FILE, "$xymon_home/etc/xymonmenu.cfg");
while (<FILE>) {
  s/\$XYMONSERVERWWWURL/$xymon_web/g;
  s/\$XYMONSERVERCGIURL/$xymon_cgi/g;
  s/\$XYMONSERVERSECURECGIURL/$xymon_seccgi/g;
  $menu .= $_;
}
close FILE;


##############################
# Subs
##############################

sub print_error {
    my $error = shift; 
    print "<center><b><font color=\"red\">$error</font></b></center><p>";
}

sub print_menu{
    my @hosts;
    my %xymon_hosts;
    if (! -d $xymon_logs) {
      &print_error("Unable to change to $xymon_logs");
      return;
    } 
    chdir $xymon_logs;
    open (FILE, 'for i in *; do echo -n "$i:"; tail -n 1 $i; echo ""; done | grep purple|');
    while (<FILE>) { 
	chomp; 
	my ($x,$y) = split /:/,$_,2;
	push @hosts, $x; 
    }
    close FILE;

    open (FILE, "<$xymon_hosts");
    while (<FILE>) { 
	chomp; 
	if (/^(\d+\.\d+\.\d+\.\d+)\s+(.*?)\s+.*?$/) {
	    $xymon_hosts{$2} = $1;
	}
    }
    close FILE;

    print "<CENTER><FORM METHOD=\"POST\" NAME=\"myform\">";
    print "<TABLE BORDER=\"1\" CELLPADDING=\"2\" CELLSPACING=\"2\"><TR><TD VALIGN=CENTER ALIGN=CENTER COLSPAN=\"3\">";
    if (@hosts) {
	print "Please select the purple alerts to clear</TD></TR>";
	print "<TR><TD ALIGN=\"LEFT\">";
    
	print "<input type=\"checkbox\" name=\"Check_ctr\" value=\"yes\" onClick=\"Check(document.myform.host)\"><b>ALL</b><TD>Test</TD><TD>Status</TD></TD></TR>";
	for (@hosts) {
	    my $alert = "Stale";
	    my ($host, $test) = split /\./;
	    $host =~ s/.*?\///g;
	    $host =~ s/,/\./g;
	    if ($xymon_hosts{$host}) { $alert = "<b>Active</b>"; }
	    print "<TR><TD ALIGN=\"LEFT\"><input name=\"host\" value=\"$_\" type=\"checkbox\"><img src=\"$xymon_gifs/purple.gif\">$host</TD>";
	    print "<TD><A HREF=\"/xymon/html/$host.$test.html\">$test</A><TD>$alert</TD></TD></TR>";
	}
	print "<TR><TD COLSPAN=\"3\" VALIGN=CENTER ALIGN=CENTER><input type=\"submit\" name=\"cmd\" value=\"Clear Purple Alerts\">";
	print " <input type=\"submit\" name=\"cmd\" value=\"Refresh List\">";
    } else {
	print "There are no purple alerts";
	print "<TR><TD COLSPAN=\"3\" VALIGN=CENTER ALIGN=CENTER><INPUT TYPE=\"submit\" NAME=\"cmd\" VALUE=\"Refresh List\">";
    }
    print "</TD></TR></TABLE></FORM><p>Active hosts are still in the hosts.cfg file.<br>Stale hosts are no longer in the hosts.cfg file.</CENTER>";
}

sub clear_purple{
    my @hosts = param('host');
    print "<CENTER><FORM METHOD=\"POST\">";
    print "<TABLE BORDER=\"1\" CELLPADDING=\"2\" CELLSPACING=\"2\"><TR><TD VALIGN=CENTER ALIGN=CENTER>";
    if (@hosts) {	
	print "The following alerts have been cleared</TD></TR>";
	print "<TR><TD ALIGN=LEFT>";
	for (@hosts) {
            my $error = 0;
	    my ($host, $test) = split /\./;
	    $host =~ s/.*?\///g;
	    $host =~ s/,/\./g;
            open (CMD, "(sudo $xymon_home/bin/xymon 127.0.0.1 \"drop $host $test\"| sed 's/^/STDOUT:/') 2>&1 |");
            while (<CMD>) {
              unless (s/^STDOUT://) {
                print "$_<br>";
                $error = 1;
              }
            }
            close CMD;
            if ($error) { &print_error("Unable to clear purple alert for '$host - $test'"); 
            } else {
              print "$host - $test<br>";
            } 
	}
    } else {
	print "No alerts cleared</TD></TR>";
    }
    print "<TR><TD VALIGN=CENTER ALIGN=CENTER>";
    print "<INPUT TYPE=\"submit\" NAME=\"cmd\" value=\"View Alerts\"></TD></TR></TABLE></FORM></CENTER>";
}

sub print_header {
  my $color = shift;
  print "Content-type: text/html; charset=iso-8859-1\n\n";
  open (HEAD, "<$xymon_header") or &print_error("I can't open $xymon_header for reading!",'DIE');
  while (<HEAD>) {
    if (/META/i && /HTTP-EQUIV/i && /REFRESH/i && /CONTENT/i) {
      s/<(.*?)>/<!-- Refresh removed -->/g;
    } # It's a bit hard to edit with a refresh ;)
    s/&XYMWEBBACKGROUND/$color/g;
    s/&XYMONSKIN/$xymon_gifs/g;
    s/&XYMONBODYCSS/$xymon_gifs\/xymonbody.css/g;
    s/&XYMONBODYMENUCSS/$xymon_web\/menu\/xymonmenu-blue.css/g;
    s/&XYMWEBHIKEY//g;
    s/&XYMWEBDATE/$date/g;
    s/&XYMWEBHOST/$xymon_web/g;
    s/&XYMONBODYHEADER/$menu/g;
    s/&XYMONLOGO/$logo/g;
    for my $key (keys %xymon_env) {
      s/&$key/$xymon_env{$key}/g;
    }
    print;
  }
  close HEAD;
    print <<HTML;
<SCRIPT LANGUAGE="JavaScript">
<!--
// Thanks to http://www.plus2net.com/javascript_tutorial/checkbox-checkall.php
function Check(chk)
{
    if (document.myform.Check_ctr.checked){
        chk.checked = true;
        for (i = 0; i < chk.length; i++)
            chk[i].checked = true ;
    } else {
        chk.checked = false;
        for (i = 0; i < chk.length; i++)
            chk[i].checked = false ;
    }
}
// End -->
</script>
HTML
}

sub print_footer{
  my $color = shift;
  my $xymon_version = "";
  open (FOOT, "<$xymon_footer") or &print_error("I can't open $xymon_footer for reading!",'DIE');
  while (<FOOT>) {
    s/&XYMONBODYFOOTER//g;
    if (/&XYMONDREL/ && -x "$xymon_home/bin/xymon") {
      open(CMD, "$xymon_home/bin/xymon --version|");
      chomp($xymon_version = <CMD>);
      $xymon_version =~ s/.*?\s+//g;
      close CMD;
    }
    s/&XYMONDREL/$xymon_version/g;
    print;
  }
  close FOOT;
}


# Main

&print_header('purple');
if (param('cmd') eq 'Clear Purple Alerts') {
    &clear_purple();
} else {
    &print_menu;
}
&print_footer;
