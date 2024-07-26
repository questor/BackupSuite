#!/bin/sh

echo "unit test for backup suite"

oneTimeSetUp() {
	mkdir /dev/shm/backup_unittests
}

oneTimeTearDown() {
	rm -rf /dev/shm/backup_unittests
}

testDatabaseCreation() {
	python3 ../ctrlcenter/ctrlcenter.py -i 01SetOfFiles -o /dev/shm/backup_unittests -t ../bin_lnx64_release -d /dev/shm/backup_unittests/db.txt -c
	diff -u /dev/shm/db.txt expectedFiles/db01.txt
	rtrn=$?
	assertNull 'diff found in database after initial import!' ${rtrn}
	diff -u /dev/shm/filehashes.txt expectedFiles/filehashes01.txt
	rtrn=$?
	assertNull 'diff found in filehashes after initial import!' ${rtrn}

	
}

# load shUnit2
. ../shunit2/shunit2
