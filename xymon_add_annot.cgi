#!/usr/bin/perl

# Copy this script to your cgi-secure directory

use strict;
use CGI ":standard";

my $date = localtime(time);
# Your $xymon_top
my $xymon_top = '/opt/xymon';
# Your $XYMHOME
my $xymon_home = '/opt/xymon/server';
# This is where your annotations are stored. Make sure Apache can write here.
my $annot_top = "${xymon_top}/data/annot";
# The web path to gifs.
my $xymon_gifs = '/xymon/gifs';
# The main web path for bb display.
my $xymon_web  = '/xymon';

# This is where the data files are stored.
my $xymon_header = "$xymon_home/web/info_header"; # Change this if needed.
my $xymon_footer = "$xymon_home/web/info_footer"; # Change this if needed.
my $xymon_cgi = '/xymon-cgi';
my $xymon_seccgi = '/xymon-seccgi';

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

sub print_error {
  my $error = shift;
  print "<center><b><font color=\"red\">$error</font></b></center><p>";
}

sub add_note() {
  chomp(my $note = param("note"));
  if ($note) {
    my $annot_dir = "${annot_top}/${host}/${service}";
    my $annot_file = "${annot_dir}/${time_buf}";
    my $time = time;
    unless ( -d $annot_dir ) { system ("mkdir -p $annot_dir"); }
    open(FILE, ">>$annot_file") or &print_error("Can't add note to $annot_file") ;
    print FILE "$time|$remote_user|$remote_addr|$note\n";
    close FILE;
  }
  print "Location: ${xymon_cgi}/xymon_alert_annot.cgi\n\n";
}

&add_note;
