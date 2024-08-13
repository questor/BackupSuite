#!/bin/sh

echo "unit test for backup suite"

oneTimeSetUp() {
	rm -rf /dev/shm/_test
	mkdir /dev/shm/_test
}

#oneTimeTearDown() {
#	rm -rf /dev/shm/_test
#}

testDatabaseCreation() {
	../t2-output/linux_x86-clang-debug-default/ctrlcenter2 -i 01SetOfFiles -u 01SetOfFiles -o /dev/shm/_test -c -t ~/BackupSuite/bin_lnx64_release/ -d /dev/shm/_test/db.txt
	diff -u /dev/shm/_test/db.txt expectedFiles/db01.txt
	rtrn=$?
	assertEquals 'diff found in database after initial import!' ${rtrn} 0
	diff -u /dev/shm/_test/filehashes.txt expectedFiles/filehashes01.txt
	rtrn=$?
	assertEquals 'diff found in filehashes after initial import!' ${rtrn} 0
}

testFirstUpdate() {
	../t2-output/linux_x86-clang-debug-default/ctrlcenter2 -i 02ChangedSet -u 02ChangedSet -o /dev/shm/_test -c -t ~/BackupSuite/bin_lnx64_release/ -d /dev/shm/_test/db.txt
	diff -u /dev/shm/_test/db.txt expectedFiles/db02.txt
	rtrn=$?
	assertEquals 'diff found in database after initial import!' ${rtrn} 0
	diff -u /dev/shm/_test/filehashes.txt expectedFiles/filehashes02.txt
	rtrn=$?
	assertEquals 'diff found in filehashes after initial import!' ${rtrn} 0
}

testSecondUpdate() {
	../t2-output/linux_x86-clang-debug-default/ctrlcenter2 -i 03MoreChanges -u 03MoreChanges -o /dev/shm/_test -c -t ~/BackupSuite/bin_lnx64_release/ -d /dev/shm/_test/db.txt
	diff -u /dev/shm/_test/db.txt expectedFiles/db03.txt
	rtrn=$?
	assertEquals 'diff found in database after initial import!' ${rtrn} 0
	diff -u /dev/shm/_test/filehashes.txt expectedFiles/filehashes03.txt
	rtrn=$?
	assertEquals 'diff found in filehashes after initial import!' ${rtrn} 0
}

# load shUnit2
. shunit2/shunit2
