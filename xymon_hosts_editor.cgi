#!/usr/bin/perl

##############################
# xymon_hosts_editor.cgi
# Written by: Chris Naude
# Purpose: Provides a basic web interface to edit hosts.cfg.
#          Uses a lock file and md5sums to keep things sane.
# Requirements: md5sum
# File permissions should be setup so that the web user can write to $xymon_hosts
# Hint: Use chmod, chown, setfacl, or sudo. ;)
#
##############################

use strict;
use CGI ":standard";
use CGI::Carp qw( fatalsToBrowser carpout );
use POSIX qw(strftime);
use Fcntl qw (:flock);
$|++;

##############################
# Variables
##############################

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
my $menu = "";

my $remote_sess = param('lock_sess');

my $date = localtime(time);
my %hosts;
my $cmd = param('cmd');
my @lines;

my $lock_file = '/var/tmp/xymon_hosts.lock';
my $vi_swp = '/var/tmp/hosts.swp'; # This may vary
my $lock_sess;
my $lock_ip;
my $expire = 10; # Expire lock after this many minutes.
my ($now, $age);

my $md5sum_prog = '/usr/bin/md5sum';
my $md5sum;
my $ip = $ENV{'REMOTE_ADDR'};
my $time_left;

# Pick your favorite colors here:
my $colors = 1; # 1 = enable color display, 0 = no color display
my $page_color = '#88DD88';
my $group_color = '#8888DD';
my $comment_color = '#FF0000';
my $test_color = '#FFFF00';
my $dialup_color = '#FcFce1';
my $error;

##############################
# Subs
##############################

sub write_xymon_hosts() {
  my @lines = split /\n/, param('xymon_hosts');
  my $md5sum_param = param('md5sum');
  &get_md5sum;
  if ($md5sum ne $md5sum_param) {
    &print_error("The md5sum does not match! Someone may have modified the file after you opened it!", 'red');
  }
  if ($lock_sess ne $remote_sess) {
    &print_error("Your session has expired!", 'red');
  } 
  if (!(-w $xymon_hosts)) {
    &print_error("Your $xymon_hosts is not writable!", 'red');
  }    
  if ($error) {
    print "<CENTER><p><form><input type=\"submit\" name=\"cmd\" value=\"Retry Edit\">
<INPUT NAME=\"lock_sess\" VALUE=\"$lock_sess\" TYPE=\"hidden\">
<INPUT NAME=\"md5sum\" VALUE=\"$md5sum\" TYPE=\"hidden\">
<input name=\"cmd\" value=\"cancel\" type=\"submit\"></form></CENTER>";
  &cancel_edit;
  } else {
    open (HOSTS, ">$xymon_hosts") or &print_error("I can't write to $xymon_hosts!", 'red');
    #flock(HOSTS, LOCK_EX);
    for my $n (0 .. $#lines) { 
      if ($n == 1 && $lines[$n] =~ /^#/) { 
        $lines[$n] = "\# Last Modified: $date $ip"; 
      } elsif ($n == 1 && $lines[$n] !~ /^#/) {
        print HOSTS "\# Last Modified: $date $ip\n"; 
      } 
      $lines[$n] =~ s/\015//g;
      print HOSTS "$lines[$n]\n";
    }
    close HOSTS;
    print "<center><b><font color=\"white\">$xymon_hosts saved.</font></b></center><p>";
    unlink $lock_file;
    &print_menu;
  }
}

sub edit_xymon_hosts() {
  if ($remote_sess) { 
    $lock_sess = $remote_sess; 
  } else {
    $lock_sess = time; 
  }
  if (-s $lock_file && ($remote_sess ne $lock_sess)) {
    &print_error("Locked by $lock_sess:$lock_ip. The lock will expire in $time_left minute(s) . . .", 'red');
    print "<CENTER><P><form><input type=\"submit\" name=\"cmd\" value=\"Retry Edit\">
<input name=\"cmd\" value=\"cancel\" type=\"submit\"></FORM></CENTER>";
  
  } else {
    &read_xymon_hosts;
    open (LOCK, ">$lock_file") or &print_error("I can't open $lock_file! $!", 'red');
    print LOCK "$lock_sess:$ip";
    close LOCK;
    print <<HTML;
<FORM METHOD="POST">
<CENTER><TABLE BORDER="1" CELLPADDING="3"><CAPTION><CENTER>Xymon Hosts [$xymon_hosts]</CENTER></CAPTION>
<TR><TD ALIGN="CENTER"><INPUT NAME="cmd" VALUE="save" TYPE="submit">
<INPUT NAME="cmd" VALUE="cancel" TYPE="submit"></TD></TR>
<TR><TD><TEXTAREA ROWS="35" COLS="80" NAME="xymon_hosts" STYLE="background-color:#000066;color:#dddddd">
HTML
    for (@lines) { print "$_\n"; }
      print <<HTML;
</TEXTAREA></TD></TR>
<TR><TD ALIGN="CENTER"><INPUT NAME="lock_sess" VALUE="$lock_sess" TYPE="hidden">
<INPUT NAME="md5sum" VALUE="$md5sum" TYPE="hidden">
<INPUT NAME="cmd" VALUE="save" TYPE="submit">
<INPUT NAME="cmd" VALUE="cancel" TYPE="submit">
</FORM></TD></TR></TABLE>md5sum: $md5sum</CENTER>
HTML
  }
}

sub read_lock() {
  if (-s $lock_file) {
    open (LOCK, "<$lock_file") or &print_error("I can't open $lock_file! $!" ,'red');
    ($lock_sess, $lock_ip) = split /:/, <LOCK>;
    close LOCK;
    if (((time - $lock_sess)/60) >= $expire) { 
      unlink $lock_file; 
      $lock_sess = ''; 
  } else {
      $time_left = int($expire - ((time - $lock_sess)/60));
    }
  }
  if (-s $vi_swp) {
    my ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blksize, $blocks) = stat($vi_swp);
    my $owner;
    open (GET, "getent passwd $uid|") or &print_error("I can't open getent passwd $uid");
    while (<GET>) {
      if (/^(.*?):/) {
        $owner = $1; 
      } 
    }
    close GET;
    &print_error("User $owner currently has a vi lock on $xymon_hosts! [$vi_swp]", 'red');
  }
}

sub read_xymon_hosts() {
  if (-r "$xymon_hosts") {
    open (HOSTS, "<$xymon_hosts") or &print_error("I can't open $xymon_hosts! $!" ,'red');
    while (<HOSTS>) { 
      chomp;
      push @lines, $_; 
    }
    close HOSTS;
    &get_md5sum;
  } else {
    &print_error("I can't open $xymon_hosts! $!", 'red');
  }
  if (!(-w $xymon_hosts)) {
    &print_error("The $xymon_hosts file is not writable!" ,'red');
  }
}

sub get_md5sum() {
  open(MD5, "$md5sum_prog $xymon_hosts|") or &print_error("I can't open $md5sum_prog! $!", 'red');
  ($md5sum, my $tmp) = split /\s+/, <MD5>;
  close MD5;
}

sub cancel_edit() {
  if (-s $lock_file && ($remote_sess eq $lock_sess)) { unlink $lock_file; }
}

sub print_error() {
  my $error_msg = shift; 
  my $color = shift || 'clear';
  $error = 1;
  print "<CENTER><B><IMG SRC=\"$xymon_gifs/${color}.gif\">$error_msg</FONT></B></CENTER><P>";
}

sub print_menu() {
  &read_xymon_hosts;
  my ($group_count, $page_count, $host_count, $old_host_count, $dialup_count) = 0;
  print <<HTML;
<FORM METHOD="POST">
<CENTER><TABLE BORDER="1" CELLPADDING="3">
<CAPTION>Xymon Hosts [$xymon_hosts]</CAPTION>
<TR><TD><CENTER><INPUT NAME="cmd" VALUE="view" TYPE="submit">
<INPUT NAME="cmd" VALUE="edit" TYPE="submit"></CENTER></TD></TR><TR><TD><PRE>
HTML
  for (@lines) {
    s/^\s+//g;
    s/</&lt;/g; s/>/&gt;/g;
    if ($colors) {
      if (/^#/) { $_ = "<FONT COLOR=\"${comment_color}\">$_<\/FONT>"; }      
      if (/^group/) { $_ = "<FONT COLOR=\"$group_color\">$_<\/FONT>"; $group_count++; }
      if (/^page/) { $_ = "<FONT COLOR=\"$page_color\">$_<\/FONT>"; $page_count++; }  
      if (/^dialup/) { $dialup_count++; }  
      if (!/FONT/ && /(.*?)#(.*?)$/) { $_ = "$1<FONT COLOR=\"${test_color}\">\#$2<\/FONT>"; }      
      if (/^\d+\.\d+\.\d+\.\d+/) { $host_count++; }      
    }
    print "$_\n";
  }
  print <<HTML;
</PRE></TD></TR></TABLE>
There are $page_count page(s), $group_count group(s), $dialup_count modem bank(s) and $host_count host(s).
</CENTER>
</CENTER>
</FORM>
HTML
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

##############################
# Main 
##############################

&print_header('blue');
&read_lock;
if ($cmd =~ /save/) {
  &write_xymon_hosts;
} elsif ($cmd =~ /edit|retry/i) {
  &edit_xymon_hosts;    
} elsif ($cmd =~ /cancel/) {
  &cancel_edit;
   &print_menu;
} else {
  &print_menu;
}
&print_footer;
