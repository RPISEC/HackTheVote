#!/usr/bin/perl

=pod

=head1 NAME

gunzip_bflt - convert gzip-compressed bFLT executable files into uncompressed bFLT


=head1 SYNOPSIS

    gunzip_bflt zipped_blflt_files...

=head1 DESCRIPTION

Convert gzipped bFLT files into an uncompressed bFLT files.
The unzipped bFLT files have B<.unz> added to their file names.
If the file is already ungzipped bFLT, it isn't converted,
but a warning is printed.

=head1 PREREQUSITES

Uses packages C<IO::Uncompress::Gunzip> and C<POSIX>.

=cut

use strict;
use warnings;

# gunzip_bflt zipped_blflt_files...


use IO::Uncompress::Gunzip qw/gunzip $GunzipError/;
use POSIX;

# Read and return the BFLT header
# prints a warning and returns undef on error.
# $bfltZfh is the BFLT file handle,
# $bfltZ is the BFLT file name (for error messages)

sub get_bflt_hdr($$) {
    my ($bfltZfh, $bfltZ) = @_;
    my $buf;
    my $res = sysread $bfltZfh, $buf, 64;
    if(!defined($res)) {
    warn "$bfltZ: $!\n";
    return undef;
    }
    if($res < 64) {
    warn "$bfltZ: Too short!\n";
    return undef;
    }
    # Align the buffered file handle with the unbuffered
    seek $bfltZfh, sysseek($bfltZfh, 0, SEEK_CUR), SEEK_SET;
    return $buf;
}

# Expand a gzipped BFLT intoi an ungziped BFLT

sub expand_blftZ($) {
    my ($bfltZ) = @_;
    my $bflt = $bfltZ . '.unz';
    if(!open BFLTZ, '<' . $bfltZ) {
    warn "$bfltZ: $!\n";
    return;
    }
    my $hdr = get_bflt_hdr(\*BFLTZ, $bfltZ);
    if(!defined $hdr) {
    return;
    }
    if(substr($hdr, 0, 4) eq 'bFLT') {
    # Pack/unpack template for the BFLT header, 4 bytes ACSII,
    # 15 little-endian words
    my $hdrFmt = 'a4 N15';

    my @unpHdr = unpack $hdrFmt, $hdr;

    # Test the header flags 'gzipped' bit
    if($unpHdr[9] & 4) {

        # Unset the header flags 'gzipped' bit, and make a new header
        $unpHdr[9] &= ~4;
        $hdr = pack $hdrFmt, @unpHdr;

        if(open BFLT, '>' . $bflt) {

        # Write the header
        syswrite BFLT, $hdr;

        # Align the buffered file handle with the unbuffered
        seek BFLT, sysseek(BFLT, 0, SEEK_CUR), SEEK_SET;

        # Ungzip from the compressed file into the uncompressed
        # file
        gunzip \*BFLTZ => \*BFLT
            or die "gunzip failed: $GunzipError\n";

        close BFLTZ;
        } else {
        warn "$bflt: $!\n";
        return;
        }
    } else {
        warn "$bfltZ: Not a compressed bFLT file, not gunzipped\n";
        return;
    }
    } else {
    warn "$bfltZ: Not a bFLT file\n";
    }
    close BFLT;
}

# Expand the arguments...

foreach my $bfltZ (@ARGV) {
    expand_blftZ($bfltZ)
}
