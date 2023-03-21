import argparse
import ftplib

# define a list of required packages
required_packages = ['argparse', 'ftplib']

# check if the required packages are installed
for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        # install the missing package using pip
        import subprocess
        subprocess.run(['pip', 'install', package])

import argparse
import ftplib
import subprocess

# Define the command-line arguments
parser = argparse.ArgumentParser(description='FTP client to list directories, delete files, download files, and upload files.')
parser.add_argument('--server', required=True, help='FTP server address')
parser.add_argument('--credentials', required=True, help='Path to encrypted credentials file')
parser.add_argument('--list', metavar='DIRECTORY', help='List directories')
parser.add_argument('--delete', metavar='FILE', help='Delete file')
parser.add_argument('--download', metavar='FILE', help='Download file')
parser.add_argument('--upload', metavar=('LOCAL_FILE', 'REMOTE_FILE'), nargs='+', help='Upload file and optionally rename it')

# Parse the command-line arguments
args = parser.parse_args()

# Decrypt the credentials
result = subprocess.run(['gpg', '--quiet', '--decrypt', args.credentials], capture_output=True)
if result.returncode != 0:
    print('Error: failed to decrypt credentials')
    exit(1)
username, password = result.stdout.decode().strip().split('\n')

# Connect to the FTP server
ftp = ftplib.FTP(args.server)
ftp.login(username, password)

# Perform the requested operation
if args.list:
    ftp.cwd(args.list)
    directories = ftp.nlst()
    print(directories)
elif args.delete:
    ftp.delete(args.delete)
elif args.download:
    with open(args.download, 'wb') as f:
        ftp.retrbinary('RETR {}'.format(args.download), f.write)
elif args.upload:
    local_file = args.upload[0]
    remote_file = args.upload[1] if len(args.upload) > 1 else local_file
    with open(local_file, 'rb') as f:
        ftp.storbinary('STOR {}'.format(remote_file), f)
    print('File uploaded successfully')

# Close the FTP connection
ftp.quit()


# prompt the user if they want to keep the installed packages
answer = input("Do you want to keep the installed packages? (y/n) ")
if answer.lower() == 'n':
    # remove the installed packages using pip
    for package in required_packages:
        subprocess.run(['pip', 'uninstall', '-y', package])
