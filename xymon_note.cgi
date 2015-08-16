#!/usr/bin/perl

#############################################
# Name: xymon_note.cgi
# Author: Chris Naude
# Purpose: Print fancy notes for Xymon
#############################################

use strict;
use CGI ":standard";

# Your $XYMHOME
my $xymon_home = '/opt/xymon/server';
# The web path to gifs.
my $xymon_gifs = '/xymon/gifs';
# The main web path for xymon display. 
my $xymon_web  = '/xymon'; 
#  Text or HTML IMG tag
my $logo = "Xymon";

# This is where the data files are stored.
# Not to be confused with the default notes dir.
my $xymon_notes  = "$xymon_home/www/notes"; 
# The actual www notes dir on the server
my $xymon_notes_data  = "$xymon_home/notesdata"; 
my $xymon_header = "$xymon_home/web/info_header"; # Change this if needed.
my $xymon_footer = "$xymon_home/web/info_footer"; # Change this if needed.
my $xymon_cgi = '/xymon-cgi';
my $xymon_seccgi = '/xymon-seccgi';
#Standard hosts.cfg file
my $xymon_hosts = "$xymon_home/etc/hosts.cfg";

# No changes needed below.
my $date = localtime(time);
my %hosts;
my $host = $ENV{'REDIRECT_URL'};
$host =~ s/(.*?)\///g;
$host =~ s/(\.html)$//g;
my @lines;
my $menu = "";

open (FILE, "$xymon_home/etc/xymonmenu.cfg");
while (<FILE>) {
  s/\$XYMONSERVERWWWURL/$xymon_web/g;
  s/\$XYMONSERVERCGIURL/$xymon_cgi/g;
  s/\$XYMONSERVERSECURECGIURL/$xymon_seccgi/g;
  $menu .= $_;
}
close FILE;

sub get_hosts{
    open (HOSTS, "<$xymon_hosts") or &print_error("I can't open $xymon_hosts!");
    while (<HOSTS>) {
	if (/^(\d+\.\d+\.\d+\.\d+)\s+(.*?)\s+/) {
	    $hosts{$2} = $1;	    
	}
    }
    close HOSTS;
}

sub print_note {
	print <<HTML;
<CENTER><TABLE BORDER="1" WIDTH="75%" CELLPADDING="3"><CAPTION ALIGN="CENTER"><H2>$host [$hosts{$host}]</H2></CAPTION><TR><TD>
HTML
    if ($lines[0]) {
	print @lines;
	print "</TD></TR>";
    } else {
	print "The are no notes for this host.</TD></TR>";
    }
	print <<HTML;
<TR><TD ALIGN="CENTER"><form action="$xymon_seccgi/xymon_note_editor.cgi" method="POST"><input type="hidden" name="host" value="$host">
<input name="cmd" value="edit" type="submit"></form></TD></TR></TABLE></CENTER>
HTML
}

sub print_error {
    my $error = shift; 
    print "<center><b><font color=\"red\">$error</font></b></center><p>";
}

sub get_note {
    if ( -s "$xymon_notes_data/$host") {
	open (NOTE, "<$xymon_notes_data/$host") or &print_error("I can't open $xymon_notes_data/$host for reading!");
	while (my $note = <NOTE>) {
	    chomp;
	    push @lines, $note;
	}
	close NOTE;
    } 
}

sub print_header {
    my $color = shift;
    print "Content-type: text/html; charset=iso-8859-1\n\n";
    open (HEAD, "<$xymon_header") or &print_error("I can't open $xymon_header for reading!",'DIE');
    while (<HEAD>) {
	if (/META/i && /HTTP-EQUIV/i && /REFRESH/i && /CONTENT/i) { s/<(.*?)>/<!-- Refresh removed -->/g; } # It's a bit hard to edit with a refresh ;)
	s/&XYMWEBBACKGROUND/$color/g;
	s/&XYMONSKIN/$xymon_gifs/g;
	s/&XYMONBODYCSS/$xymon_gifs\/xymonbody.css/g;
	s/&XYMONBODYMENUCSS/$xymon_web\/menu\/xymonmenu-blue.css/g;
	s/&XYMWEBHIKEY//g;
	s/&XYMWEBDATE/$date/g;
	s/&XYMWEBHOST/$xymon_web/g;
	s/&XYMONBODYHEADER/$menu/g;
        s/&XYMONLOGO/$logo/g;
	print;
    }
    close HEAD;
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

&get_hosts;
&print_header('blue'); # I like blue notes ;)
&get_note;
&print_note;
&print_footer;
