#! /bin/sh

# Import build tools common functions
. /usr/local/bin/build-sys-common.sh

PACKAGE_NAME="endace-ptov"
SVN_ROOT=../../../../..
PWDDIR=$(pwd)
VER="1.0" # e.g. v6.0

echo "Enter the password for GPG key:"
oldmodes=`stty -g`
stty -echo
read password
stty $oldmodes

# build package
echo "=== Building the package ==="

echo "Clearing the old package ..."
rm -f flowmon-update.tar.gz
rm -f flowmon-update.tar.gz.sig
rm -f $PACKAGE_NAME.tar.gz
rm -rf temp
echo "Exporting the flowmon-update data ..."
mkdir -p temp
cp -R "./flowmon-update" "./temp/flowmon-update"
mkdir -p "./temp/flowmon-update/data/"
mkdir -p "./temp/flowmon-update/data/etc/"
cp ../../endace/* "./temp/flowmon-update/data/"
cp -vR "../../endace/etc" "./temp/flowmon-update/data/"

echo "Creating the package ..."
cd temp
chmod 755 ./flowmon-update/*.sh
tar czf flowmon-update.tar.gz flowmon-update
mv flowmon-update.tar.gz ..
cd ..
rm -rf temp
echo "$password" | gpg --batch --yes --passphrase-fd 0 --default-key info@invea-tech.com -b flowmon-update.tar.gz
if [ $? -ne 0 ]; then
    echo "ERROR: Signature not created!"
    exit 1
fi
if [ ! -e flowmon-update.tar.gz.sig ]; then
    echo "ERROR: Signature not created!"
    exit 1
fi
tar czf $PACKAGE_NAME.tar.gz flowmon-update.tar.gz flowmon-update.tar.gz.sig
echo "Package $PACKAGE_NAME created."
exit 0

