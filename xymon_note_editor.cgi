#!/usr/bin/perl

#############################################
# Name: xymon_note_editor.cgi
# Author: Chris Naude
# Purpose: Manage HTML notes files
# Debian: apt-get install libhtml-fromtext-perl
#############################################

use strict;
use CGI ":standard";
use HTML::FromText; 

# Your $BBHOME
my $xymon_home = "/opt/xymon/server";
# The web path to gifs.
my $xymon_gifs = "/xymon/gifs";
# The main web path for Xymon display. 
my $xymon_web  = "/xymon"; 
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
my $cmd = param("cmd");
my $host = param("host");
$host =~ s/(.*?)\///g;
$host =~ s/(\.html)$//g;
my $note = param("note");
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

sub save_note {
    open (NOTE, ">$xymon_notes_data/$host") or &print_error("I can't write to $xymon_notes_data/$host!");
    system("/bin/touch $xymon_notes/${host}.html");
    print NOTE $note;
    close NOTE;
    &get_note;
    print '<center><b><font color="white">Note saved.</font></b></center><p>';
    &print_note;
}

sub edit_note {
    if ($cmd =~ /add html/) {
  my $t2h = HTML::FromText->new({
            blockcode  => 1,
      lines      => 1,
            tables     => 1,
            bullets    => 1,
            numbers    => 1,
            urls       => 1,
            email      => 1,
            bold       => 1,
            underline  => 1,
        });
  $note = $t2h->parse( $note );
  #$note =~ s/\n/<br>/sgi; # 
  
    }
    if ($cmd =~ /strip html/) {
  $note =~ s/<.*?>//sgi;
    }
    print <<HTML;
<CENTER><TABLE BORDER="1" CELLPADDING="3><CAPTION><H2><CENTER>$host [$hosts{$host}]</CENTER></H2></CAPTION>
<TR><TD ALIGN="CENTER"><form method="POST"><input type="hidden" name="host" value="$host">
<TEXTAREA ROWS="35" COLS="80" NAME="note" STYLE="background-color:#000066;color:#dddddd">
HTML
if ($note) {
    print $note;
} elsif ($lines[0]) { 
    print @lines; 
} else {
    print '<!-- Remember to use proper HTML formatting here. -->';
}
    print <<HTML;
</TEXTAREA><br>
<input name="cmd" value="preview" type="submit">
<input name="cmd" value="add html tags" type="submit">
<input name="cmd" value="strip html tags" type="submit">
<input name="cmd" value="cancel" type="submit"></form></TD></TR></TABLE></CENTER>
HTML
}

sub print_note {
    print <<HTML;
<CENTER><TABLE WIDTH="75%" BORDER="1" CELLPADDING="3"><CAPTION><CENTER><H2>$host [$hosts{$host}]</H2></CENTER></CAPTION><TR><TD>
HTML
    if ($lines[0]) {
  print @lines;
  print <<HTML;
</TD></TR><TR><TD ALIGN="CENTER"><form method="POST"><input type="hidden" name="host" value="$host">
HTML
    } elsif ($cmd =~ /preview/) {
  print <<HTML;
$note</TD></TR><TR><TD ALIGN="CENTER"><form method="POST"><input type="hidden" name="host" value="$host">
<input name="cmd" value="save" type="submit">
HTML
    } else {
  print <<HTML;
The are no notes for $host [$hosts{$host}].</TD></TR>
<TR><TD ALIGN="CENTER"><form method="POST"><input type="hidden" name="host" value="$host">
HTML
}
    print <<HTML;
<input type="hidden" name="note" value='$note'>
<input name="cmd" value="edit" type="submit">
<input name="cmd" value="list" type="submit"></form></TD></TR></TABLE></CENTER>
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
      push @lines, $note;
  }
  close NOTE;
    } 
}

sub print_menu{
    print '<CENTER><TABLE BORDER="1" CELLPADDING="3"><CAPTION><H2><CENTER>Big Brother Notes</CENTER></H2><b></b></CAPTION>';
    for my $host(sort keys %hosts) {
  print <<HTML;
<TR><TD>$host</TD><TD>$hosts{$host}</TD>
<TD><form method="POST"><input type="hidden" name="host" value="$host">
<input name="cmd" value="view" type="submit">
<input name="cmd" value="edit" type="submit"></form></TD></TR>
HTML
    }
    print '</TABLE></CENTER>';
}

sub get_hosts{
    open (HOSTS, "<$xymon_hosts") or &print_error("I can't open $xymon_hosts!");
    while (<HOSTS>) {
  if (/^(\d+\.\d+\.\d+\.\d+)\s+(.*?)\s+/) {
      $hosts{$2} = $1;      
  }
    }
    close HOSTS;
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

&get_hosts;
&print_header('blue');
if ($cmd =~ /edit|html/) {
    &get_note;
    &edit_note;
} elsif ($cmd eq 'view') {
    &get_note;
    &print_note;
} elsif ($cmd eq 'preview') {
    &print_note;
} elsif ($cmd eq 'preview as html') {
    &print_note;
} elsif ($cmd eq 'save') {
    &save_note;
} else {
    &print_menu;
}
&print_footer;
