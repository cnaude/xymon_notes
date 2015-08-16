#!/usr/bin/perl

# Copy this script to your xymon cgi-bin
# Create a menu link to it

use strict;
use CGI ":standard";

my $date = localtime(time);
# Your $xymon_top
my $xymon_top = '/opt/xymon';
my $xymon_home = '/opt/xymon/server';
# This is where your annotations are stored. Make sure Apache can write here.
my $annot_top = "${xymon_top}/data/annot";
# The web path to gifs.
my $xymon_gifs = '/xymon/gifs';
# The main web path for bb display.
my $xymon_web  = '/xymon';
my $logo = "Xymon";

my $xymon_header = "$xymon_home/web/info_header"; # Change this if needed.
my $xymon_footer = "$xymon_home/web/info_footer"; # Change this if needed.
my $xymon_cgi = "/xymon-cgi";
my $xymon_seccgi = "/xymon-seccgi";

my $cmd = param("cmd");
my $note = param("note");

my $host = param("host");
my $service = param("service");
my $time_buf = param("timebuf");
my $http_referer = $ENV{'HTTP_REFERER'};
if ($http_referer =~ /HOST=(.*?)&SERVICE=(.*?)&TIMEBUF=(.*?)$/) {
    ($host,$service,$time_buf) = ($1,$2,$3);
}
$host =~ s/\./_/g;
my $remote_addr = $ENV{'REMOTE_ADDR'};
my $remote_user = $ENV{'REMOTE_USER'};
my @hist = ();
my @notes = ();
my @list = ();
my $color = "blue";

my $menu = "";

open (FILE, "$xymon_home/etc/xymonmenu.cfg");
while (<FILE>) {
  s/\$XYMONSERVERWWWURL/$xymon_web/g;
  s/\$XYMONSERVERCGIURL/$xymon_cgi/g;
  s/\$XYMONSERVERSECURECGIURL/$xymon_seccgi/g;
  $menu .= $_;
}
close FILE;

sub print_error {
    my $error = shift;
    print "<center><b><font color=\"red\">$error</font></b></center><p>";
}

sub get_notes() {
  my $tr_color_a = "333333";
  my $tr_color_b = "333300";
  my $tr_color = "";
  my $count = 0;
  if ($host && $service && $time_buf) {  
    my $annot_dir = "${annot_top}/${host}/${service}";
    my $annot_file = "${annot_dir}/${time_buf}";
    if ( -d $annot_dir ) {
      if ( -f $annot_file ) {
        open(ANNOT, "<$annot_file") or die "Can't open $annot_file!\n";
        while (my $line = <ANNOT>) {
          if ($count % 2) { $tr_color = $tr_color_a; } else { $tr_color = $tr_color_b; }
          my @tmp = split(/\|/, $line,5);
          my $date = localtime($tmp[0]);
          push @notes, "<TR ALIGN=LEFT BGCOLOR=\"#${tr_color}\"><TD>$date</TD><TD>${tmp[1]}</TD><TD>${tmp[2]}</TD><TD>${tmp[3]}</TD></TR>";
          $count++;
        }
        close ANNOT;
      }
    }
  }
}

sub get_hist() {
  if ($host && $service && $time_buf) {  
    my $hist_dir = "${xymon_top}/data/histlogs/${host}/${service}";
    my $hist_file = "${hist_dir}/${time_buf}";
    open(HIST, "<$hist_file");
    my $count = 0;
    while (<HIST>) {
      unless ($count) {
        if (/^red\s+/) { $color = "red"; }
        if (/^green\s+/) { $color = "green"; }
        if (/^purple\s+/) { $color = "purple"; }
        if (/^yellow\s+/) { $color = "yellow"; }
        if (/^clear\s+/) { $color = "clear"; }
        if (/^blue\s+/) { $color = "blue"; }
      }
      s/&red|^red/<IMG SRC="$xymon_gifs\/red.gif">/g;
      s/&green|^green/<IMG SRC="$xymon_gifs\/green.gif">/g;
      s/&purple|^purple/<IMG SRC="$xymon_gifs\/purple.gif">/g;
      s/&yellow|^yellow/<IMG SRC="$xymon_gifs\/yellow.gif">/g;
      s/&clear|^clear/<IMG SRC="$xymon_gifs\/clear.gif">/g;
      s/&blue|^blue/<IMG SRC="$xymon_gifs\/blue.gif">/g;
      if (! $count) {
        s/<.*?\.gif">//g;
        push @hist, "<H3>$_</H3><PRE>";
      }  else {
        push @hist, $_;
      }
      $count++;
    }
    close HIST;
  }
}
  

sub print_notes() {
    print "<CENTER><H3>Annotations</H3></CENTER>";
    print "<br><br>
<CENTER><TABLE ALIGN=CENTER BORDER=0 SUMMARY=\"Annotations\"> 
<PRE>";
    if (@notes) {
          print @notes;
    } else {
          print "<br><b>There are no annotations for this alert.</b>";
    }
    print "<TR><TD COLSPAN=\"5\"><form action=\"${xymon_seccgi}/xymon_add_annot.cgi\"><br>Note: <input size=\"75\" name=\"note\" type=\"text\"> <input type=\"submit\" value=\"add\" name=\"cmd\"> <input type=\"reset\" value=\"clear\" name=\"clear\">";
    print "<input type=\"hidden\" name=\"host\" value=\"$host\">";
    print "<input type=\"hidden\" name=\"service\" value=\"$service\">";
    print "<input type=\"hidden\" name=\"timebuf\" value=\"$time_buf\">";
    print "</form></TD></TR>";
    print "</PRE></TABLE></CENTER>";
}

sub print_hist() {
    print "<CENTER><H3>Historical Status</H3><?CENTER>";
    print "<br><br>
<CENTER><TABLE ALIGN=CENTER BORDER=0 SUMMARY=\"Detail Status\">
<TR><TD>";
    if (@hist) {
      print @hist;
    } else {
      print "<br><b>There is no history information for this alert</b>";
    }
    print "</PRE></TD></TR></TABLE></CENTER>";
}

sub print_error {
    my $error = shift; 
    print "<center><b><font color=\"red\">$error</font></b></center><p>";
}

sub get_list() {
  open(FIND, "find $xymon_top/data/annot -type f|");
  while(<FIND>) {
    chomp;
    s/$xymon_top\/data\/annot\///g;
    my @tmp = split(/\//,$_);
    push @list, "<FORM><TR BGCOLOR=\"#333333\"><TD>${tmp[0]}</TD><TD>${tmp[1]}</TD><TD>${tmp[2]}</TD><TD>";
    push @list, "<input type=\"hidden\" name=\"host\" value=\"$tmp[0]\">";
    push @list, "<input type=\"hidden\" name=\"service\" value=\"$tmp[1]\">";
    push @list, "<input type=\"hidden\" name=\"timebuf\" value=\"$tmp[2]\">";
    push @list, "<INPUT TYPE=\"submit\" name=\"cmd\" value=\"view or append\"></TD></FORM>";
  }
  close FIND;
}
  
sub print_list() {
  print "<CENTER><FORM><TABLE ALIGN=CENTER BORDER=0 SUMMARY=\"Annotated Alerts\">";
  if (@list) {
    print @list;
  } else {
    print "<TR><TD><B>There are no alerts with annotations.</B></TD></TR>";  
  }
  print "</PRE></TD></TR></TABLE></CENTER>";
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

&get_notes;
&get_hist;
&print_header($color);
if ($host,$service,$time_buf) {
  &print_notes;
  &print_hist;
} else {
  &get_list;
  &print_list;
}
&print_footer;
