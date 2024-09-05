BackupSuite
===========

a small project to create backup media for my own stuff. mostly processing specified folders, creating initial and incremental backups to be written to read-only memory like DVDs (there are variants that are a long time durable). the data to be written on media can be preprocessed to get a better compression (for example mp3, pdf, jpg and some other to gain extra 20-30%, the rest is packed by a generic compressor).

ctrlcenter.py is deprecated, a reimplementation is done in c++ and also available in this repo. the ctrlcenter2 is used to control the backup process.

the general usage is:
- first create an initial set of a backup by creating a backup-set:
	ctrlcenter2 -c -i INPUTFOLDER -o OUTPUTFOLDER
  this will take the files from the inputfolder and compress them to the output folder. it will also create a "filehashes.txt" in the output folder and will create in the folder where the programm is called a database-file. you can write the data from the OUTPUTFOLDER onto DVDs and delete the folder afterwards.

  you optional can check that the decompressed files match the hashes of the input files by doing a verification:
  	ctrlcenter2 -v -i OUTPUTFOLDER

- now you can create an incremental update by:
    ctrlcenter2 -c -i INPUTFOLDER -o OUTPUTFOLDER
  this will scan for updates in the INPUTFOLDER, compress the changed files, create again a "filehashes.txt" and will update the database-file with the new hashes of the files.

if you loose the database (for whatever reason) you can recreate the database by importing the filehashes from the output folders back into the database.