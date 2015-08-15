#!/usr/bin/perl

use strict;

my @files = @ARGV;
my $xymon_notes_data_default = '/opt/xymon/server/notesdata';
my $num = $#files + 1;
my $s = 's' if ($num != 1);
print "Are you sure that you want to convert $num file${s}?\n [y/n] ";
my $yn = <STDIN>;
unless ($yn =~ /y/i) { print "Cancelling.\n"; exit 0; }
print "Please enter the destination directory. Press enter for default\n";
print " [$xymon_notes_data_default] ";
chomp(my $xymon_notes_data = <STDIN>);
$xymon_notes_data =~ s/^(\s+)//g; # Kill leading white space
$xymon_notes_data =~ s/(\s+)$//g; # Kill trailing white space
if ($xymon_notes_data !~ /./) {
    $xymon_notes_data = $xymon_notes_data_default; 
}
if ((-d $xymon_notes_data) && (-w $xymon_notes_data)) {
    print "Your directory '$xymon_notes_data' seems valid.\n";
    &convertFiles;
} else {
    print "Your directory '$xymon_notes_data' is not valid. Bye\n";
    exit 1;
}

sub convertFiles {
    for my $file (@files) {
	my $html = '';
	if ( -r $file ) {
	    open(FILE, "<$file") or die "Can't open $_\n";
	    while (<FILE>) {
		$html .= $_;
	    }
	    close FILE;
	    # Here we strup everything before <body*> and the end tags.
	    $html =~ s/<\/html.*?>|<\/body.*?>|<html.*?<body.*?>//sgi; 
	    # Strip off extension. You can add others here . . .
	    system("mv $file $file.bak; touch $file"); # Create empty file
	    print "Moving $file to $file.bak and touching $file\n";
	    $file =~ s/\.html$//i;
	    open(FILE, ">$xymon_notes_data/$file") or die "Can't open $xymon_notes_data/$file\n";
	    print FILE $html;
	    close FILE;
	    print "I successfully converted $file\n";
	} else {
	    print "File $_ is not readable. Skipping.\n";
	}
    }
}
